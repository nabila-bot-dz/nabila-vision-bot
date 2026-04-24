import os
import telebot
import requests
import base64
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def ask_openrouter(text=None, image_base64=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    messages = []

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": text if text else "وش فيها هذي الصورة؟"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })
    else:
        messages.append({
            "role": "user",
            "content": text
        })

    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": messages
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        result = response.json()

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"صرات مشكلة مع OpenRouter: {result.get('error', {}).get('message', 'خطأ مجهول')}"

    except Exception as e:
        return f"صرات مشكلة يا الزينة 😭: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '❤️🐺 يا الزينة انا نبيلة الذكية \nابعتيلي نص ولا صورة ونجاوبك')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_openrouter(text=message.text)
    bot.reply_to(message, reply)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_chat_action(message.chat.id, 'typing')
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
    caption = message.caption if message.caption else None

    reply = ask_openrouter(text=caption, image_base64=image_base64)
    bot.reply_to(message, reply)

@app.route('/')
def home():
    return "نبيلة شاعلة 🔥"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

print("نبيلة شعلت 🔥")
threading.Thread(target=run_flask).start()
bot.infinity_polling()
