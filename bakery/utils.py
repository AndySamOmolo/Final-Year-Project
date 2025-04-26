from .models import Order, OrderItem
from cart.models import Cart, CartItem
from bakery.models import BakeryItem

def create_orders_from_cart(user, session=None):
    try:
        cart = Cart.objects.get(user=user) if user.is_authenticated else Cart.objects.filter(session=session).first()

        if cart and cart.items.exists():
            for item in cart.items.all():
                if not item.product:
                    print(f"CartItem {item.id} is missing a product!")
                    continue 

                if item.quantity is None or item.quantity <= 0:
                    item.quantity = 1  
                    print(f"Default quantity for {item.product.name}: {item.quantity}")

                order = Order.objects.create(
                    user=user if user.is_authenticated else None,
                    cart=cart,
                    status='Pending',
                    total_price=item.get_total_price(), 
                )
                print(f"Order created for cart #{cart.id}.")

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.get_total_price(),
                )
                print(f"OrderItem created for {item.product.name} with quantity {item.quantity}")
            

            cart.items.all().delete()
            return True  
        else:
            print("No items in the cart or cart not found.")
            return False  
    except Exception as e:
        print(f"Error creating orders from cart: {e}")
        return False  
