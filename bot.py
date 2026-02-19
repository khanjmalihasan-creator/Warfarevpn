import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from config import BOT_TOKEN, ADMIN_IDS, PLANS
from database import Database
import datetime

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# اتصال به دیتابیس
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
🌟 به ربات فروش VPN خوش آمدید {user.first_name}!

با استفاده از این ربات می‌توانید:
🔹 خرید اکانت VPN با کیفیت بالا
🔹 مشاهده اکانت‌های فعال
🔹 پشتیبانی ۲۴ ساعته

برای شروع از منوی زیر استفاده کنید:
    """
    
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy")],
        [InlineKeyboardButton("📋 اکانت‌های من", callback_data="my_accounts")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy":
        await show_plans(query)
    elif query.data == "my_accounts":
        await show_user_accounts(query)
    elif query.data == "support":
        await show_support(query)
    elif query.data == "about":
        await show_about(query)
    elif query.data.startswith("plan_"):
        await process_plan_selection(query, context)
    elif query.data == "back_to_main":
        await back_to_main(query)

async def show_plans(query):
    keyboard = []
    for plan_id, plan in PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{plan['name']} - {plan['price']:,} تومان",
                callback_data=f"plan_{plan_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📦 پلن‌های موجود:\n\n"
        "لطفاً یکی از پلن‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def process_plan_selection(query, context):
    plan_id = query.data.replace("plan_", "")
    plan = PLANS.get(plan_id)
    
    if not plan:
        await query.edit_message_text("❌ پلن انتخاب شده معتبر نیست!")
        return
    
    # ذخیره پلن انتخاب شده در context
    context.user_data['selected_plan'] = plan_id
    
    keyboard = [
        [InlineKeyboardButton("✅ تایید و پرداخت", callback_data="confirm_payment")],
        [InlineKeyboardButton("🔙 بازگشت به پلن‌ها", callback_data="buy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📋 خلاصه سفارش:\n\n"
        f"پلن: {plan['name']}\n"
        f"مدت زمان: {plan['duration']} روز\n"
        f"مبلغ: {plan['price']:,} تومان\n\n"
        "آیا برای پرداخت آماده هستید؟",
        reply_markup=reply_markup
    )

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    plan_id = context.user_data.get('selected_plan')
    if not plan_id:
        await query.edit_message_text("❌ خطا: لطفاً دوباره تلاش کنید.")
        return
    
    plan = PLANS[plan_id]
    
    # ایجاد سفارش در دیتابیس
    order_id = db.create_order(user_id, plan_id, plan['price'])
    
    # اینجا باید به درگاه پرداخت متصل شوید
    # برای مثال با زرین‌پال:
    payment_url = f"https://example.com/pay/{order_id}"  # لینک ساختگی
    
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت", url=payment_url)],
        [InlineKeyboardButton("✅ پرداخت انجام شد", callback_data=f"verify_payment_{order_id}")],
        [InlineKeyboardButton("🔙 انصراف", callback_data="buy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔗 لطفاً برای پرداخت مبلغ {plan['price']:,} تومان "
        "روی دکمه زیر کلیک کنید:\n\n"
        "⚠️ پس از اتمام پرداخت، دکمه 'پرداخت انجام شد' را بزنید.",
        reply_markup=reply_markup
    )

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = int(query.data.split('_')[-1])
    
    # اینجا باید صحت پرداخت را از درگاه بررسی کنید
    # برای مثال:
    payment_verified = True  # این را با بررسی واقعی جایگزین کنید
    
    if payment_verified:
        db.update_order_status(order_id, 'paid')
        
        # دریافت اطلاعات سفارش
        # و ایجاد اکانت VPN
        # اینجا باید کد ساخت اکانت VPN را قرار دهید
        
        # مثال ساخت اکانت:
        config = f"vless://example-config-for-order-{order_id}"
        db.add_vpn_account(query.from_user.id, config, 30)  # 30 روز
        
        await query.edit_message_text(
            "✅ پرداخت با موفقیت انجام شد!\n\n"
            "اکانت VPN شما ساخته شد و به اکانت‌های شما اضافه گردید.\n"
            "برای مشاهده اکانت خود به بخش 'اکانت‌های من' بروید."
        )
    else:
        await query.edit_message_text(
            "❌ پرداخت ناموفق بود!\n"
            "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
        )

async def show_user_accounts(query):
    user_id = query.from_user.id
    accounts = db.get_user_accounts(user_id)
    
    if not accounts:
        await query.edit_message_text(
            "📭 شما هیچ اکانت فعالی ندارید.\n"
            "برای خرید از بخش 'خرید VPN' اقدام کنید."
        )
        return
    
    text = "📋 اکانت‌های فعال شما:\n\n"
    for acc in accounts:
        expiry = datetime.datetime.strptime(acc[3], '%Y-%m-%d %H:%M:%S.%f')
        days_left = (expiry - datetime.datetime.now()).days
        text += f"🔹 کانفیگ {acc[0]}:\n"
        text += f"   تاریخ انقضا: {expiry.date()}\n"
        text += f"   روزهای باقیمانده: {days_left}\n"
        text += f"   کانفیگ: `{acc[2]}`\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_support(query):
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📞 پشتیبانی:\n\n"
        "برای ارتباط با پشتیبانی می‌توانید از راه‌های زیر اقدام کنید:\n"
        "🆔 @support_username\n"
        "📧 support@example.com\n\n"
        "ساعات پاسخگویی: ۹ صبح تا ۱۲ شب",
        reply_markup=reply_markup
    )

async def show_about(query):
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "ℹ️ درباره ما:\n\n"
        "این ربات با هدف ارائه خدمات VPN با کیفیت و پرسرعت راه‌اندازی شده است.\n"
        "✅ پشتیبانی ۲۴ ساعته\n"
        "✅ سرورهای پرسرعت\n"
        "✅ قیمت مناسب\n"
        "✅ بازگشت وجه در صورت نارضایتی",
        reply_markup=reply_markup
    )

async def back_to_main(query):
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy")],
        [InlineKeyboardButton("📋 اکانت‌های من", callback_data="my_accounts")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌟 به منوی اصلی خوش آمدید!\n"
        "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ شما دسترسی به این بخش ندارید!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton("👥 کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("📤 ارسال همگانی", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 پنل مدیریت",
        reply_markup=reply_markup
    )

def main():
    # ساخت اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # اجرای ربات
    print("ربات در حال اجرا است...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
