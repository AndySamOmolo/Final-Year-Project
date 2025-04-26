from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from bakery.models import UserProfile, Order
from bakery.forms import UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404

# Create your views here.
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at') 
    return render(request, 'user_dashboard/orders.html', {'orders': orders})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('user_dashboard:account_details') 
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'user_dashboard/password.html', {'form': form})

@login_required
def account_details(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard:account_details') 
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'user_dashboard/account_details.html', {'form': form, 'profile': profile})


@login_required
def delivery_status(request):
    orders = Order.objects.filter(user=request.user)

    context = {
        'orders': orders
    }

    return render(request, 'user_dashboard/delivery_status.html', context)

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    order_items = order.order_items.all()
    estimated_delivery_time = order.estimated_delivery_time
    
    return render(request, 'user_dashboard/order_details.html', {
        'order': order,
        'order_items': order_items,
        'estimated_delivery_time': estimated_delivery_time,
    })

