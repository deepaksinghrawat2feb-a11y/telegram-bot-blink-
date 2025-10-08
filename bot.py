import os, time, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("8398661571:AAGbQFDS1EDm3He6_EvqbtPr-LbsqISqM_U")
BLINK_USER_TOKEN = os.getenv("d36dcddf0f4cf6a39daf06501fa010ff")
CREATE_ORDER_URL = "https://www.blinktransact.com/api/create-order"
CHECK_ORDER_URL = "https://www.blinktransact.com/api/check-order-status"
REDIRECT_URL = os.getenv("BLINK_REDIRECT_URL", "https://your-callback.onrender.com/callback")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot live ✅\nUse /pay <amount> or /status <order_id>")

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = context.args[0] if context.args else "1"
    order_id = f"ORDR{update.effective_user.id}{int(time.time())}"
    payload = {
        "customer_mobile": str(update.effective_user.id),
        "user_token": BLINK_USER_TOKEN,
        "amount": amount,
        "order_id": order_id,
        "redirect_url": REDIRECT_URL,
        "remark1": "telegram",
        "remark2": "upi"
    }
    r = requests.post(CREATE_ORDER_URL, data=payload)
    result = r.json()
    link = result.get("payment_url") or "No link returned"
    await update.message.reply_text(f"💳 Pay {amount} INR here:\n{link}\nOrder ID: {order_id}")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = context.args[0] if context.args else None
    if not order_id:
        await update.message.reply_text("Usage: /status <order_id>")
        return
    payload = {"user_token": BLINK_USER_TOKEN, "order_id": order_id}
    r = requests.post(CHECK_ORDER_URL, data=payload)
    result = r.json()
    await update.message.reply_text(f"📊 Status: {result}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", status_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
