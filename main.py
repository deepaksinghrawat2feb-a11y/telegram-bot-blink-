import os, time, requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

BOT_TOKEN = os.getenv("8398661571:AAGbQFDS1EDm3He6_EvqbtPr-LbsqISqM_U")
BLINK_USER_TOKEN = os.getenv("d36dcddf0f4cf6a39daf06501fa010ff")
bot = Bot(token=BOT_TOKEN)

CREATE_ORDER_URL = "https://www.blinktransact.com/api/create-order"
CHECK_ORDER_URL = "https://www.blinktransact.com/api/check-order-status"
REDIRECT_URL = os.getenv("BLINK_REDIRECT_URL", "https://your-service.onrender.com/callback")

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# --- Telegram Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot live ✅\nUse /pay <amount> or /status <order_id>")

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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

        r = requests.post(CREATE_ORDER_URL, data=payload, timeout=20)
        result = r.json()

        link = result.get("payment_url") or result.get("upi_url") or "No link returned"
        await update.message.reply_text(f"💳 Pay {amount} INR here:\n{link}\nOrder ID: {order_id}")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        order_id = context.args[0] if context.args else None
        if not order_id:
            await update.message.reply_text("Usage: /status <order_id>")
            return

        payload = {"user_token": BLINK_USER_TOKEN, "order_id": order_id}
        r = requests.post(CHECK_ORDER_URL, data=payload, timeout=20)
        result = r.json()

        await update.message.reply_text(f"📊 Status: {result}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("pay", pay))
application.add_handler(CommandHandler("status", status_cmd))

# --- Flask Routes ---
@app.route("/")
def health():
    return {"status": "ok"}, 200

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/callback", methods=["GET", "POST"])
def blink_callback():
    data = request.args.to_dict() if request.method == "GET" else request.get_json(silent=True) or request.form.to_dict()
    app.logger.info(f"Blink callback: {data}")
    return {"ok": True, "data": data}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
