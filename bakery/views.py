from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomRegisterForm, CustomLoginForm
from django.contrib import messages
from .models import BakeryItem, Category, BakeryItem, Size, Topping
from cart.models import CartItem 
from django.core.paginator import Paginator
from .forms import NewsletterSubscriptionForm, ContactForm
from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(email):
    send_mail(
        'Subscription Confirmation',
        'Thank you for subscribing to our newsletter!',  
        [email],  
        fail_silently=False,
    )

def home(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save()
            send_confirmation_email(subscription.email)  
            messages.success(request, "Thank you for subscribing to our newsletter!")
            return redirect('home')
        else:
            print(form.errors)  
            messages.error(request, "Invalid email address. Please try again.")
    else:
        form = NewsletterSubscriptionForm()

    bestsellers = BakeryItem.objects.filter(available=True).order_by('-sales')[:9]

    context = {
        'form': form,
        'bestsellers': bestsellers,
    }

    return render(request, 'bakery/home.html', context)


def products(request):
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    
    if category_slug:
        category = Category.objects.get(slug=category_slug)
        items = BakeryItem.objects.filter(category=category)
    else:
        items = BakeryItem.objects.all()

    paginator = Paginator(items, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'bakery/products.html', context)

def about(request):
    return render(request, 'bakery/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject,       
                message,       
                email,          
                [settings.DEFAULT_FROM_EMAIL], 
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  
        else:
            messages.error(request, "There was an error with your form. Please try again.")
    else:
        form = ContactForm()

    return render(request, 'bakery/contact.html', {'form': form})


def account(request):
    return render(request, 'bakery/account.html')

def cake_template(request, slug):
    item = get_object_or_404(BakeryItem, slug=slug)
    sizes = Size.objects.all() 
    toppings = Topping.objects.all() 
    
    return render(request, 'bakery/cake-template.html', {
        'item': item,
        'sizes': sizes,
        'toppings': toppings
    })

@login_required
def user_dashboard(request):  
    return render(request, 'user_dashboard/account_details.html')

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")
            return redirect('login') 
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomRegisterForm()

    return render(request, 'bakery/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard:add_bakery_item') 
                elif user.is_staff:
                    return redirect('staff_dashboard:manage_orders')
                else:
                    return redirect('user_dashboard:account_details') 
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "There was an error in the form.")
    else:
        form = CustomLoginForm()

    return render(request, 'bakery/login.html', {'form': form})

def search_bakery_items(request):
    query = request.GET.get('q', '')  
    items = BakeryItem.objects.none()

    if query:
        items = BakeryItem.objects.filter(name__icontains=query)

    return render(request, 'bakery/search.html', {'items': items, 'query': query})