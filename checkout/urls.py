from django.urls import path
from . import views
from . import test_mpesa

app_name = 'checkout'

urlpatterns = [
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('get_details/', views.get_details, name="get_details"),
    
    # Test endpoints (for development only - remove in production)
    path('test-mpesa-success/<int:order_id>/', test_mpesa.simulate_mpesa_success, name='test_mpesa_success'),
    path('test-mpesa-failure/<int:order_id>/', test_mpesa.simulate_mpesa_failure, name='test_mpesa_failure'),
]