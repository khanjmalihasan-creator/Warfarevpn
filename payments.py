import requests
import json
from config import ZARINPAL_MERCHANT_ID

class ZarinpalPayment:
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id
        self.base_url = "https://api.zarinpal.com/pg/v4/payment/"
    
    def create_payment(self, amount, description, callback_url, order_id):
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,  # تبدیل به ریال
            "description": description,
            "callback_url": callback_url,
            "metadata": {"order_id": order_id}
        }
        
        try:
            response = requests.post(
                self.base_url + "request.json",
                json=data
            )
            result = response.json()
            
            if result['data']['code'] == 100:
                return {
                    'success': True,
                    'url': f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}",
                    'authority': result['data']['authority']
                }
            else:
                return {'success': False, 'error': result['errors']}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, amount, authority):
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,
            "authority": authority
        }
        
        try:
            response = requests.post(
                self.base_url + "verify.json",
                json=data
            )
            result = response.json()
            
            if result['data']['code'] == 100:
                return {'success': True, 'ref_id': result['data']['ref_id']}
            else:
                return {'success': False, 'code': result['data']['code']}
        except Exception as e:
            return {'success': False, 'error': str(e)}
