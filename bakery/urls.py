from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('products/', views.products, name='products'),  
    path('about/', views.about, name='about'),
    path('account/', views.account, name='account'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('cake/<slug:slug>/', views.cake_template, name='cake_template'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('search/', views.search_bakery_items, name='search_bakery_items'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
