import telebot
from telebot import types
import os

TOKEN = os.getenv("8656129697:AAH4g6qI-7aRKH7yYEA_1j_CHUJKHhmb5PI")
ADMIN_ID = int(os.getenv("6498779131"))

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()

# ====== ССЫЛКА ОПЛАТЫ ======
PAY_URL = "http://t.me/send?start=IVvH7CqDScaT"

# ====== МЕНЮ ======
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📦 Товары", "⭐ Отзывы", "📞 Поддержка")
    return markup

# ====== СТАРТ ======
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать!",
        reply_markup=main_menu()
    )

# ====== ТОВАРЫ ======
@bot.message_handler(func=lambda m: m.text == "📦 Товары")
def products(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton("🤖 Бот — 1000 сом (~$11)", callback_data="buy_bot"),
        types.InlineKeyboardButton("🌐 Сайт — $50", callback_data="buy_site")
    )

    bot.send_message(message.chat.id, "Выберите товар:", reply_markup=markup)

# ====== ПОКУПКА ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    products = {
        "bot": {"name": "Telegram-бот", "price": "1000 сом (~$11)"},
        "site": {"name": "Сайт", "price": "$50"}
    }

    key = call.data.split("_")[1]
    product = products[key]

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Оплатить", url=PAY_URL))

    bot.send_message(
        call.message.chat.id,
        f"🛒 {product['name']}\n💰 Цена: {product['price']}\n\n"
        f"После оплаты напишите 'оплатил'",
        reply_markup=markup
    )

    bot.send_message(
        ADMIN_ID,
        f"🆕 Новый заказ\n"
        f"👤 {call.from_user.id}\n"
        f"📦 {product['name']}\n"
        f"💰 {product['price']}"
    )

# ====== ПОДТВЕРЖДЕНИЕ ======
@bot.message_handler(func=lambda m: m.text.lower() == "оплатил")
def paid(message):
    bot.send_message(
        ADMIN_ID,
        f"💸 Пользователь {message.from_user.id} написал 'оплатил'"
    )

    bot.send_message(
        message.chat.id,
        "⏳ Ожидайте проверки администратором"
    )

# ====== ОТЗЫВЫ ======
@bot.message_handler(func=lambda m: m.text == "⭐ Отзывы")
def reviews(message):
    msg = bot.send_message(message.chat.id, "Напишите отзыв:")
    bot.register_next_step_handler(msg, save_review)

def save_review(message):
    bot.send_message(
        ADMIN_ID,
        f"⭐ Отзыв от {message.from_user.id}:\n{message.text}"
    )
    bot.send_message(message.chat.id, "Спасибо ❤️")

# ====== ПОДДЕРЖКА ======
@bot.message_handler(func=lambda m: m.text == "📞 Поддержка")
def support(message):
    msg = bot.send_message(message.chat.id, "Напишите сообщение:")
    bot.register_next_step_handler(msg, to_admin)

def to_admin(message):
    bot.send_message(
        ADMIN_ID,
        f"📩 Сообщение от {message.from_user.id}:\n{message.text}"
    )
    bot.send_message(message.chat.id, "Отправлено ✅")

# ====== ЗАПУСК ======
while True:
    try:
        print("Бот работает...")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print("Ошибка:", e)
