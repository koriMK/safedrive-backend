import requests
import base64
from datetime import datetime
from models import Config

class MpesaService:
    def __init__(self):
        try:
            self.consumer_key = Config.get_value('MPESA_CONSUMER_KEY', 'UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t')
            self.consumer_secret = Config.get_value('MPESA_CONSUMER_SECRET', 'eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb')
            self.business_shortcode = Config.get_value('MPESA_BUSINESS_SHORTCODE', '174379')
            self.passkey = Config.get_value('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
            self.base_url = Config.get_value('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
        except Exception:
            # Fallback to environment variables
            import os
            self.consumer_key = os.environ.get('MPESA_CONSUMER_KEY', 'UnDvUCktXcQDyRScx0uAnJlA7rboMWhSnAxvhSOYQiX8QU0t')
            self.consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET', 'eP7nwvhM3OwL0nVhRlOCsGnRawPi32BkENmT33NygDpdYdq5sy1WyAshdCnidCkb')
            self.business_shortcode = os.environ.get('MPESA_BUSINESS_SHORTCODE', '174379')
            self.passkey = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
            self.base_url = os.environ.get('MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
        
        # Token caching
        self._cached_token = None
        self._token_expires = None
        
    def get_access_token(self):
        """Get OAuth access token with caching"""
        # Check cached token
        if self._cached_token and self._token_expires:
            if datetime.now() < self._token_expires:
                return self._cached_token
        
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {"Authorization": f"Basic {encoded_credentials}"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                
                # Cache token
                self._cached_token = access_token
                from datetime import timedelta
                self._token_expires = datetime.now() + timedelta(seconds=expires_in - 60)  # 1 min buffer
                
                return access_token
            return None
                
        except Exception:
            return None
    
    def generate_password(self, timestamp):
        """Generate password for STK push"""
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode()).decode()
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        try:
            # Validate inputs
            if not phone_number or not amount:
                return {"success": False, "error": "Phone number and amount are required"}
            
            # Validate phone number format
            if not str(phone_number).isdigit() or len(str(phone_number)) not in [9, 10, 12]:
                return {"success": False, "error": "Invalid phone number format"}
            
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "Failed to get M-Pesa access token"}
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self.generate_password(timestamp)
            
            # Format phone number properly
            phone_str = str(phone_number)
            if phone_str.startswith('+254'):
                phone_str = phone_str[4:]  # Remove +254
            elif phone_str.startswith('254'):
                phone_str = phone_str[3:]  # Remove 254
            elif phone_str.startswith('0'):
                phone_str = phone_str[1:]  # Remove 0
            
            # Ensure we have 9 digits and add 254
            if len(phone_str) == 9:
                formatted_phone = f"254{phone_str}"
            else:
                return {"success": False, "error": "Invalid phone number length"}
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": formatted_phone,
                "PartyB": self.business_shortcode,
                "PhoneNumber": formatted_phone,
                "CallBackURL": Config.get_value('MPESA_CALLBACK_URL', 'https://safedrive-backend-d579.onrender.com/api/v1/payments/callback'),
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            print(f"M-Pesa STK Push payload: {payload}")  # Debug log
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ResponseCode") == "0":
                    return {
                        "success": True,
                        "checkout_request_id": result.get("CheckoutRequestID"),
                        "merchant_request_id": result.get("MerchantRequestID"),
                        "response_code": result.get("ResponseCode"),
                        "response_description": result.get("ResponseDescription")
                    }
                else:
                    return {"success": False, "error": result.get("errorMessage", result)}
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                return {"success": False, "error": error_data}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_stk_status(self, checkout_request_id):
        """Query STK Push payment status"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "Failed to get access token"}
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self.generate_password(timestamp)
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json()}
                
        except Exception as e:
            return {"success": False, "error": str(e)}