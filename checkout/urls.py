from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('get_details/', views.get_details, name="get_details"),
]