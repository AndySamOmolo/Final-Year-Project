from django.urls import path
from . import views

app_name = 'user_dashboard'

urlpatterns = [
    path('orders/', views.orders, name='orders'),
    path('account_details', views.account_details, name='account_details'),
    path('change_password/', views.change_password, name='change_password'),
    path('delivery_status/', views.delivery_status, name='delivery_status'),
    path('order/<int:order_id>/details/', views.order_details, name='order_details'),
]
