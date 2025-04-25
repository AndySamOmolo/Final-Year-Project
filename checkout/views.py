from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import initiate_stk_push
from bakery.utils import create_orders_from_cart
import json
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from bakery.models import Order, UserProfile, OrderItem
from cart.models import Cart
from django.http import JsonResponse


def get_details(request):
    user = request.user
    if user.is_authenticated:
        cart = Cart.objects.get(user=user)
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session=session_key).first()

    if cart:
        phone_number = request.POST.get('phone_number', None)
        address = request.POST.get('address', None)

        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            cart=cart,
            status='Pending',
            payment_status='Pending',
            address=address, 
            phone_number=phone_number 
        )

        total_price = Decimal('0.00')
        for item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.price * item.quantity
            )
            total_price += order_item.total_price

        order.total_price = total_price
        order.save()

        if user.is_authenticated:
            if phone_number or address:
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                user_profile.update_profile(address=address, phone_number=phone_number)

        return render(request, 'checkout/payment_form.html', {'order': order, 'total_price': total_price})
    else:
        return HttpResponse("No cart found.", status=400)



@login_required
def initiate_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        phone_number = request.POST.get('phone_number')

        if not order_id:
            return render(request, 'checkout/payment_error.html', {'error': 'Order ID is missing.'})

        if not phone_number:
            return render(request, 'checkout/payment_error.html', {'error': 'Phone number is required.'})

        try:
            order = Order.objects.get(id=order_id)
            total_price = order.total_price

            if total_price <= 0:
                return render(request, 'checkout/payment_error.html', {'error': 'Invalid total price.'})

            # Initiate the STK Push
            response = initiate_stk_push(phone_number, total_price, f"Order-{order_id}", "Checkout Payment")

            if 'error' in response:
                return render(request, 'checkout/payment_error.html', {'error': response.get('error')})

            # Store the CheckoutRequestID in the order
            if 'CheckoutRequestID' in response:
                order.checkout_request_id = response['CheckoutRequestID']
                order.save()

            return render(request, 'checkout/payment_pending.html', {'order': order, 'response': response})

        except Order.DoesNotExist:
            return render(request, 'checkout/payment_error.html', {'error': 'Order not found'})

    return redirect('checkout:get_details')



@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            # Parse the request body into JSON
            data = json.loads(request.body.decode('utf-8'))
            print("Full Callback Data:", json.dumps(data, indent=2))

            # Extract the relevant details from the callback response
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')  # Safaricom's unique identifier

            # Log extracted fields
            print("[DEBUG] Extracted CheckoutRequestID:", checkout_request_id)

            # Validate that the necessary fields are present
            if not checkout_request_id:
                print("[ERROR] Missing CheckoutRequestID in the callback")
                return JsonResponse({'status': 'error', 'message': 'Missing CheckoutRequestID'}, status=400)

            # Find the order using the CheckoutRequestID (which is unique to each payment request)
            try:
                order = Order.objects.get(checkout_request_id=checkout_request_id)
                if result_code == 0:  # Payment was successful
                    order.status = 'Paid'  # Change to the appropriate status
                    order.payment_status = 'Successful'
                    order.save()

                    # Process the payment and update the cart or order items
                    print("[DEBUG] Payment successful for Order:", order.id)
                    return render(request, 'checkout/payment_success.html')

                else:  # Payment failed or other result codes
                    print(f"[DEBUG] Payment failed. ResultDesc: {result_desc}")
                    return render(request, 'checkout/payment_error.html', {'error': f"Payment failed: {result_desc}"})

            except Order.DoesNotExist:
                print(f"[ERROR] Order with CheckoutRequestID {checkout_request_id} not found.")
                return render(request, 'checkout/payment_error.html', {'error': "Order not found"})

        except json.JSONDecodeError as json_error:
            print("[ERROR] JSONDecodeError:", str(json_error))
            return render(request, 'checkout/payment_error.html', {'error': "Invalid JSON data received from Mpesa"})
        except Exception as e:
            print(f"[ERROR] Exception while processing callback: {str(e)}")
            return render(request, 'checkout/payment_error.html', {'error': f"Error processing callback: {str(e)}"})

    else:
        return render(request, 'checkout/payment_error.html', {'error': "Invalid request method. Expected POST."})
