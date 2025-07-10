import requests
import json
import base64
from datetime import datetime
from decimal import Decimal
from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while getting access token: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {e}")
    except KeyError as e:
        logger.error(f"Key error - access_token not found: {e}")
    
    return None

def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Concatenate Business Short Code, PassKey, and Timestamp
    password_string = f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"

    # Base64 encode the string
    encoded_password = base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

    return encoded_password

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_access_token()

    if not access_token:
        return {"error": "Failed to get access token"}

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    try:
        amount = int(Decimal(amount))
    except (ValueError, TypeError) as e:
        return {"error": f"Invalid amount format: {e}"}

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password()

    payload = {
        "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    logger.info(f"Initiating STK push with AccountReference: {account_reference}")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        response_json = response.json()
        logger.info("STK Push API Response: %s", json.dumps(response_json, indent=4))
        
        if response.status_code != 200:
            return {"error": f"API Error: {response_json.get('errorMessage', 'Unknown error')}"}

        return response_json
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during STK push: {e}")
        return {"error": f"Request error: {e}"}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding response JSON: {e}")
        return {"error": f"JSON decoding error: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error during STK push: {e}")
        return {"error": f"Unexpected error: {e}"}
