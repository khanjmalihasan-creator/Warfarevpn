import os
from dotenv import load_dotenv

load_dotenv()

# توکن ربات شما
BOT_TOKEN = '8512123339:AAEOrT2yPiH1OmScwKByngVkOrnqroXaYco'

# اطلاعات ادمین - آیدی عددی شما
ADMIN_IDS = [8131712128]  # آیدی شما اضافه شد

# قیمت‌ها (به تومان)
PLANS = {
    '1month': {'name': '۱ ماهه', 'price': 50000, 'duration': 30},
    '3months': {'name': '۳ ماهه', 'price': 120000, 'duration': 90},
    '6months': {'name': '۶ ماهه', 'price': 200000, 'duration': 180},
    '1year': {'name': 'یک ساله', 'price': 350000, 'duration': 365}
}

# درگاه پرداخت (اگر ندارید، می‌تونید خالی بذارید)
ZARINPAL_MERCHANT_ID = ''
