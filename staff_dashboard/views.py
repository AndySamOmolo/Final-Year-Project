from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from bakery.models import Order, BakeryItem, OrderItem
from django.db.models import Sum
from django.contrib.auth.models import User



def staff_check(user):
    return user.is_staff and not user.is_superuser


# Manage Orders
@user_passes_test(staff_check)
def manage_orders(request):
    orders = Order.objects.filter(status='In Progress').prefetch_related('order_items__product').order_by('-created_at')
    return render(request, 'staff_dashboard/manage_orders.html', {'orders': orders})


@user_passes_test(staff_check)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        status = request.POST.get('status')
        estimated_delivery_time = request.POST.get('estimated_delivery_time')

        order.status = status

        if estimated_delivery_time:
            order.estimated_delivery_time = estimated_delivery_time
        
        order.save()
        return redirect('staff_dashboard:manage_orders')

    return render(request, 'staff_dashboard/update_order_status.html', {'order': order})


# Update Bakery Items
@user_passes_test(staff_check)
def update_items(request):
    items = BakeryItem.objects.all()
    return render(request, 'staff_dashboard/update_items.html', {'items': items})


@user_passes_test(staff_check)
def edit_item(request, item_id):
    item = get_object_or_404(BakeryItem, id=item_id)
    if request.method == "POST":
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.available = request.POST.get('available') == 'on'
        item.save()
        return redirect('staff_dashboard:update_items')
    return render(request, 'staff_dashboard/edit_item.html', {'item': item})

