# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from bakery.models import BakeryItem, Category, Topping, Size, OrderItem
from django.contrib.auth.models import User
from .forms import BakeryItemForm
from bakery.forms import CategoryForm, ToppingForm, SizeForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from bakery.models import Order, User, NewsletterSubscription
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils.timezone import now
from datetime import datetime


def admin_check(user):
    return user.is_superuser

def truncate_text(text, max_length):
    """Truncate text to max_length chars, adding ellipsis if truncated"""
    if not text:
        return ""
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length] + "..."

@user_passes_test(admin_check)
def report_dashboard(request):
    return render(request, 'admin_dashboard/report_dashboard.html')



from .utils import generate_order_status_chart, generate_user_role_chart, generate_sales_chart, generate_subscription_chart

@user_passes_test(admin_check)
def generate_pdf_report(request, report_type):
    template_path = ''
    context = {}
    chart = None

    if report_type == 'registered_users':
        users = User.objects.all()
        
        # Pre-process users with truncated fields for PDF
        processed_users = []
        for user in users:
            processed_users.append({
                'username': truncate_text(user.username, 12),
                'email': truncate_text(user.email, 20),
                'is_staff': user.is_staff,
            })
        
        context['registered_users'] = processed_users
        context['total_users'] = users.count()
        context['staff_users'] = users.filter(is_staff=True).count()
        context['regular_users'] = users.filter(is_staff=False).count()
        chart = generate_user_role_chart(users)

    elif report_type == 'newsletter_subscriptions':
        subscriptions = NewsletterSubscription.objects.all()
        context['newsletter_subscriptions'] = subscriptions
        context['total_subscribers'] = subscriptions.count()
        
        # Calculate new this month
        current_month = now().month
        current_year = now().year

        total_subscribers = subscriptions.count()
        new_this_month = subscriptions.filter(date_subscribed__month=current_month, date_subscribed__year=current_year).count()
        
        context = {
            'newsletter_subscriptions': subscriptions,
            'total_subscribers': total_subscribers,
            'new_this_month': new_this_month,
        }
        chart = generate_subscription_chart(subscriptions)

    elif report_type == 'order_summary':
        orders = Order.objects.all()
        
        # Pre-process orders with truncated fields for PDF
        processed_orders = []
        for order in orders:
            username = "N/A"
            if order.user:
                username = truncate_text(order.user.username, 12)
            
            processed_orders.append({
                'username': username,
                'status': order.status,
                'total_price': order.total_price,
                'created_at': order.created_at,
            })
        
        total_orders = orders.count()
        pending_orders = orders.filter(status='Pending').count()
        completed_orders = orders.filter(status='Completed').count()
        context = {
            'orders': processed_orders,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
        }
        chart = generate_order_status_chart(orders)

    elif report_type == 'bakery_items':
        template_path = 'admin_dashboard/reports/bakery_items.html'
        bakery_items = BakeryItem.objects.all()

        sales_data = []
        total_revenue_all = 0
        
        for item in bakery_items:
            total_quantity_sold = OrderItem.objects.filter(product=item).aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_revenue = OrderItem.objects.filter(product=item).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            total_revenue_all += total_revenue
            
            sales_data.append({
                'item': item,
                'total_quantity_sold': total_quantity_sold,
                'total_revenue': total_revenue
            })
        
        top_selling_item = None
        if sales_data:
            top_selling_item = max(sales_data, key=lambda x: x['total_quantity_sold'])['item']

        context = {
            'sales_data': sales_data,
            'total_items': bakery_items.count(),
            'total_revenue_all': total_revenue_all,
            'top_selling_item': top_selling_item,
        }
        chart = generate_sales_chart(sales_data)

    else:
        return HttpResponse('Invalid report type.', content_type='text/plain')

    if chart:
        context['chart'] = chart
    # Render the HTML template for the report
    html = render_to_string(f'admin_dashboard/reports/{report_type}.html', context)

    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF', content_type='text/plain')

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response



@user_passes_test(admin_check)
def manage_users(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'admin_dashboard/manage_users.html', {'users': users})

@user_passes_test(admin_check)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        user.username = username
        user.email = email
        user.save()

        profile = user.userprofile
        profile.address = address
        profile.phone_number = phone_number
        profile.save()

        messages.success(request, "User details updated successfully!")
        return redirect('admin_dashboard:manage_users')

    return render(request, 'admin_dashboard/edit_user.html', {'user': user})

@user_passes_test(admin_check)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('admin_dashboard:manage_users')

@user_passes_test(admin_check)
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_staff = request.POST.get('is_staff') == 'on'

        if password != confirm_password:
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Passwords do not match."
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Username already exists."
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'admin_dashboard/add_user.html', {
                'error': "Email already in use."
            })

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=is_staff
        )
        user.save()

        messages.success(request, "User details added successfully!")
        return redirect('admin_dashboard:manage_users')
    return render(request, 'admin_dashboard/add_user.html')


@user_passes_test(admin_check)
def add_bakery_item(request):
    if request.method == 'POST':
        form = BakeryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:manage_bakery_items')
    else:
        form = BakeryItemForm()
    return render(request, 'admin_dashboard/add_bakery_item.html', {'form': form})



@user_passes_test(admin_check)
def manage_bakery_items(request):
    items = BakeryItem.objects.all()
    categories = Category.objects.all()
    toppings = Topping.objects.all()
    sizes = Size.objects.all()

    category_form = CategoryForm()
    topping_form = ToppingForm()
    size_form = SizeForm()

    if request.method == 'POST':
        if 'category_name' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, "Category added successfully!")
                return redirect('admin_dashboard:manage_bakery_items')

        elif 'topping_name' in request.POST:
            topping_form = ToppingForm(request.POST)
            if topping_form.is_valid():
                topping_form.save()
                messages.success(request, "Topping added successfully!")
                return redirect('admin_dashboard:manage_bakery_items')

        elif 'size_name' in request.POST:
            size_form = SizeForm(request.POST)
            if size_form.is_valid():
                size_form.save()
                messages.success(request, "Size added successfully!")
                return redirect('admin_dashboard:manage_bakery_items')

    return render(request, 'admin_dashboard/manage_bakery_items.html', {
        'items': items,
        'categories': categories,
        'toppings': toppings,
        'sizes': sizes,
        'category_form': category_form,
        'topping_form': topping_form,
        'size_form': size_form,
    })




@user_passes_test(admin_check)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('admin_dashboard:manage_attributes')
    return render(request, 'admin_dashboard/edit_category.html', {'form': form, 'category': category})

@user_passes_test(admin_check)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('admin_dashboard:manage_attributes')


@user_passes_test(admin_check)
def edit_topping(request, topping_id):
    topping = get_object_or_404(Topping, id=topping_id)
    form = ToppingForm(instance=topping)
    if request.method == 'POST':
        form = ToppingForm(request.POST, instance=topping)
        if form.is_valid():
            form.save()
            messages.success(request, "Topping updated successfully!")
            return redirect('admin_dashboard:manage_attributes')
    return render(request, 'admin_dashboard/edit_topping.html', {'form': form, 'topping': topping})

@user_passes_test(admin_check)
def delete_topping(request, topping_id):
    topping = get_object_or_404(Topping, id=topping_id)
    topping.delete()
    messages.success(request, "Topping deleted successfully!")
    return redirect('admin_dashboard:manage_attributes')



@user_passes_test(admin_check)
def edit_size(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    form = SizeForm(instance=size)
    if request.method == 'POST':
        form = SizeForm(request.POST, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, "Size updated successfully!")
            return redirect('admin_dashboard:manage_attributes')
    return render(request, 'admin_dashboard/edit_size.html', {'form': form, 'size': size})

@user_passes_test(admin_check)
def delete_size(request, size_id):
    size = get_object_or_404(Size, id=size_id)
    size.delete()
    messages.success(request, "Size deleted successfully!")
    return redirect('admin_dashboard:manage_attributes')


@user_passes_test(admin_check)
def edit_bakery_item(request, item_id):
    item = get_object_or_404(BakeryItem, id=item_id)
    form = BakeryItemForm(instance=item)
    if request.method == 'POST':
        form = BakeryItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Bakery Item updated successfully!")
            return redirect('admin_dashboard:manage_bakery_items')
    return render(request, 'admin_dashboard/edit_bakery_item.html', {'form': form, 'item': item})

@user_passes_test(admin_check)
def delete_bakery_item(request, item_id):
    item = get_object_or_404(BakeryItem, id=item_id)
    item.delete()
    messages.success(request, "Bakery Item deleted successfully!")
    return redirect('admin_dashboard:manage_bakery_items')
