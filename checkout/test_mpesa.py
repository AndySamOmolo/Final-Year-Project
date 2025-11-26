# Test utility to simulate M-Pesa callback
# This is for testing purposes only - not for production use

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bakery.models import Order
import json


@csrf_exempt
def simulate_mpesa_success(request, order_id):
    """
    Simulates a successful M-Pesa callback for testing purposes.
    Access via: /checkout/test-mpesa-success/<order_id>/
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Simulate the M-Pesa callback data structure
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-12345",
                    "CheckoutRequestID": order.checkout_request_id if order.checkout_request_id else f"test-checkout-{order_id}",
                    "ResultCode": 0,  # 0 = Success
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": float(order.total_price)},
                            {"Name": "MpesaReceiptNumber", "Value": "TEST123456"},
                            {"Name": "TransactionDate", "Value": "20231126150000"},
                            {"Name": "PhoneNumber", "Value": order.phone_number}
                        ]
                    }
                }
            }
        }
        
        # Update order as if M-Pesa confirmed payment
        order.status = 'Paid'
        order.payment_status = 'Successful'
        order.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Order {order_id} marked as paid (TEST MODE)',
            'order_status': order.status,
            'payment_status': order.payment_status,
            'simulated_callback': callback_data
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'Order {order_id} not found'
        }, status=404)


@csrf_exempt  
def simulate_mpesa_failure(request, order_id):
    """
    Simulates a failed M-Pesa callback for testing purposes.
    Access via: /checkout/test-mpesa-failure/<order_id>/
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Simulate failed payment
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-12345",
                    "CheckoutRequestID": order.checkout_request_id if order.checkout_request_id else f"test-checkout-{order_id}",
                    "ResultCode": 1032,  # User canceled
                    "ResultDesc": "Request cancelled by user"
                }
            }
        }
        
        # Update order as failed
        order.status = 'Failed'
        order.payment_status = 'Failed'
        order.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Order {order_id} marked as failed (TEST MODE)',
            'order_status': order.status,
            'payment_status': order.payment_status,
            'simulated_callback': callback_data
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': f'Order {order_id} not found'
        }, status=404)
