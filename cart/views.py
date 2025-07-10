from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem, Cart
from bakery.models import BakeryItem, Topping, Size
from decimal import Decimal

def product_list(request):
    return render(request, 'bakery/products.html')
                    
def view_cart(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
        except Cart.DoesNotExist:
            cart_items = []  
    else:
        session_key = request.session.session_key
        if not session_key:
            cart_items = []
        else:
            try:
                cart = Cart.objects.get(session=session_key)
                cart_items = CartItem.objects.filter(cart=cart)
            except Cart.DoesNotExist:
                cart_items = []

    total_price = sum(item.get_total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, item_id):
    product = get_object_or_404(BakeryItem, id=item_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, defaults={'session': None})
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session=session_key, user=None)

    if request.method == "POST":
        size_name = request.POST.get('size', '1.5') 
        topping_name = request.POST.get('toppings', '')  
        custom_message = request.POST.get('message', '')
        quantity = int(request.POST.get('quantity', 1))

        base_price = product.price

        size = get_object_or_404(Size, name=size_name)

   
        topping = None
        if topping_name:
            try:
                topping = Topping.objects.get(name=topping_name)
            except Topping.DoesNotExist:
                topping = None 

        size_price_adjustment = get_size_price_adjustment(size.name)
        topping_price_adjustment = get_topping_price_adjustment(topping_name) if topping else Decimal('0.00')

        item_price = base_price + size_price_adjustment + topping_price_adjustment

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,  
            toppings=topping,  
            custom_message=custom_message,
            defaults={'quantity': quantity, 'price': item_price}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price = item_price
            cart_item.save(update_fields=['quantity', 'price'])

    return redirect('cart:view_cart')



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart:view_cart')


def update_quantity(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        cart_item.quantity = max(1, quantity)
        cart_item.save(update_fields=['quantity'])
        
        base_price = cart_item.product.price
        size_price_adjustment = get_size_price_adjustment(cart_item.size)
        topping_price_adjustment = get_topping_price_adjustment(cart_item.toppings)
        cart_item.price = base_price + size_price_adjustment + topping_price_adjustment
        cart_item.save(update_fields=['price'])

    return redirect('cart:view_cart')


def get_size_price_adjustment(size_name):
    try:
        size = Size.objects.get(name=size_name)
        return size.price_adjustment
    except Size.DoesNotExist:
        return Decimal('0.00') 


def get_topping_price_adjustment(topping_name):
    try:
        topping = Topping.objects.get(name=topping_name)
        return topping.price_adjustment
    except Topping.DoesNotExist:
        return Decimal('0.00') 

