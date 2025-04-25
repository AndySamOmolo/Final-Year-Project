from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from bakery.models import BakeryItem
from django.contrib.auth.models import User
from .forms import BakeryItemForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from bakery.models import Order, User, NewsletterSubscription
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils.timezone import now



def admin_check(user):
    return user.is_superuser


@user_passes_test(admin_check)
def report_dashboard(request):
    return render(request, 'admin_dashboard/report_dashboard.html')

@user_passes_test(admin_check)
def generate_pdf_report(request, report_type):
    context = {}

    if report_type == 'registered_users':
        context['registered_users'] = User.objects.all()

    elif report_type == 'newsletter_subscriptions':
        context['newsletter_subscriptions'] = NewsletterSubscription.objects.all()

    elif report_type == 'order_summary':
        orders = Order.objects.all()
        context['total_orders'] = orders.count()
        context['pending_orders'] = orders.filter(status='Pending').count()
        context['completed_orders'] = orders.filter(status='Completed').count()

    elif report_type == 'bakery_items':
        context['bakery_items'] = BakeryItem.objects.all()

    else:
        return HttpResponse('Invalid report type.', content_type='text/plain')

    # Render the HTML template for the report
    html = render_to_string(f'admin_dashboard/reports/{report_type}.html', context)

    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF', content_type='text/plain')

    # Serve the PDF as a response
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{now().strftime("%Y%m%d")}.pdf"'
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
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_staff = request.POST.get('is_staff') == 'on'

        # Validate the passwords match
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


@login_required
@user_passes_test(admin_check)
def add_bakery_item(request):
    if request.method == 'POST':
        form = BakeryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  
            return redirect('admin_dashboard:add_bakery_item') 
    else:
        form = BakeryItemForm()

    return render(request, 'admin_dashboard/add_bakery_item.html', {'form': form})


