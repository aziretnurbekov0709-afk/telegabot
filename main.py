import telebot
from telebot import types
import requests
import time
import threading
import os

# 🔐 Безопасное получение токенов
BOT_TOKEN = os.getenv("8656129697:AAH4g6qI-7aRKH7yYEA_1j_CHUJKHhmb5PI")
CRYPTO_TOKEN = os.getenv("UQD4kfKvot7S7a-k0D7YLsRQquU5pOQ6Lj7vjNh9uzn7Q-ep")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ❗ Проверка (чтобы не крашился)
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не найден")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# 📌 Главное меню
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📂 Мои работы", "💼 Услуги")
    kb.row("💰 Цены", "📩 Заказать")
    kb.row("📝 Отзыв")
    return kb

# ▶️ Старт
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        bot.send_message(
            msg.chat.id,
            "👋 Привет!\nЯ делаю сайты, ботов и презентации\n\nВыбери ниже 👇",
            reply_markup=main_menu()
        )
    except:
        pass

# 💰 Создание платежа
def create_payment(chat_id, amount, service):
    try:
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
        data = {"asset": "USDT", "amount": amount}

        r = requests.post(url, json=data, headers=headers, timeout=10)

        if r.status_code != 200:
            bot.send_message(chat_id, "❌ Ошибка оплаты (API)")
            return

        data = r.json()

        if not data.get("ok"):
            bot.send_message(chat_id, "❌ Ошибка создания счета")
            return

        pay_url = data["result"]["pay_url"]
        invoice_id = data["result"]["invoice_id"]

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💳 Оплатить", url=pay_url))

        bot.send_message(chat_id, f"💰 Оплата: {service}", reply_markup=kb)

        threading.Thread(
            target=check_payment,
            args=(chat_id, invoice_id, service, amount),
            daemon=True
        ).start()

    except Exception as e:
        print("Ошибка оплаты:", e)
        bot.send_message(chat_id, "❌ Ошибка при создании оплаты")

# 🔁 Проверка оплаты
def check_payment(chat_id, invoice_id, service, amount):
    try:
        while True:
            time.sleep(10)

            url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
            headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}

            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            if not data.get("ok"):
                continue

            status = data["result"]["items"][0]["status"]

            if status == "paid":
                bot.send_message(chat_id, f"✅ Оплата получена: {service}")

                if ADMIN_ID:
                    bot.send_message(
                        ADMIN_ID,
                        f"💰 Новый заказ\n👤 {chat_id}\n💵 {amount}\n🛒 {service}"
                    )
                break
    except Exception as e:
        print("Ошибка проверки:", e)

# 📝 Отзыв
def save_review(msg):
    try:
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, f"📝 Отзыв:\n{msg.text}")
        bot.send_message(msg.chat.id, "🙏 Спасибо!")
    except:
        pass

# 📩 Заказ
def send_order(msg):
    try:
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, f"📩 Новый заказ:\n{msg.text}")
        bot.send_message(msg.chat.id, "✅ Отправлено!")
    except:
        pass

# 🔘 Кнопки
@bot.message_handler(func=lambda message: True)
def handle_buttons(msg):
    try:
        text = msg.text

        if text == "📂 Мои работы":
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(
                "🌐 Сайт (Mercury IELTS)",
                url="https://sites.google.com/view/meruryielts9/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
            ))
            kb.add(types.InlineKeyboardButton(
                "🤖 Telegram бот",
                url="https://t.me/fahdesign_bot"
            ))

            bot.send_message(msg.chat.id, "📂 Мои работы 👇", reply_markup=kb)

        elif text == "💼 Услуги":
            bot.send_message(msg.chat.id, "🌐 Сайты\n🤖 Боты\n📊 Презентации")

        elif text == "💰 Цены":
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row("💰 Купить сайт", "🤖 Купить бота")
            kb.row("⬅️ Назад")
            bot.send_message(msg.chat.id, "Выбери 👇", reply_markup=kb)

        elif text == "💰 Купить сайт":
            create_payment(msg.chat.id, "50", "Сайт")

        elif text == "🤖 Купить бота":
            create_payment(msg.chat.id, "12.7", "Бот")

        elif text == "📩 Заказать":
            msg2 = bot.send_message(msg.chat.id, "Напиши заказ:")
            bot.register_next_step_handler(msg2, send_order)

        elif text == "📝 Отзыв":
            msg2 = bot.send_message(msg.chat.id, "Напиши отзыв:")
            bot.register_next_step_handler(msg2, save_review)

        elif text == "⬅️ Назад":
            bot.send_message(msg.chat.id, "Главное меню 👇", reply_markup=main_menu())

        else:
            bot.send_message(msg.chat.id, "Выбери 👇", reply_markup=main_menu())

    except Exception as e:
        print("Ошибка кнопок:", e)

# ▶️ Запуск (анти-краш)
while True:
    try:
        print("🚀 Бот запущен")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print("Перезапуск из-за ошибки:", e)
        time.sleep(5)
