import os
import telebot
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_KEY = os.environ.get("GROQ_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_KEY)

user_histories = {}

SYSTEM_PROMPT = "Ты — универсальный AI ассистент. Отвечай чётко, полезно и дружелюбно. Используй язык пользователя (казахский, русский или английский)."

@bot.message_handler(commands=['start'])
def start(message):
    user_histories[message.chat.id] = []
    bot.reply_to(message, "👋 Салем! Мен — универсалды AI ассистент!\nПривет! Я — универсальный AI ассистент!\nЗадавайте любые вопросы на любом языке 🚀")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_histories[message.chat.id] = []
    bot.reply_to(message, "✅ История очищена! Начинаем заново.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id not in user_histories:
        user_histories[chat_id] = []
    bot.send_chat_action(chat_id, 'typing')
    user_histories[chat_id].append({"role": "user", "content": message.text})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[chat_id],
            max_tokens=1000
        )
        reply = response.choices[0].message.content
        user_histories[chat_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    print("🤖 Бот запущен!")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            import time
            time.sleep(5)
