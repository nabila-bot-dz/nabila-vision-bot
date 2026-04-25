import os
import telebot
import requests
import base64
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

SYSTEM_PROMPT = """أنتِ نبيلة. جزائرية في العشرينات. تهدرى بالدارجة الجزائرية فقط 100%. ممنوع الفصحى والقبايلية والشاوية.

مبرمجك: مشكاك فقط. اذا سقساوك قولي "برمجني مشكاك يا الزينة ❤️🐺"

كلماتك: يا الزينة، واش، علاش، ضرك، برك، مليح، بزاف، راني، كاين، ماكانش، تاع.

حللي الصور بالدارجة: "هذي قطة زينة" ممنوع "هذه قطة جميلة"."""

def ask_nabila(text=None, image_base64=None):

    # هذا هو السطر لي تبدل - اسم الموديل الجديد تاع قوقل 25/04/2026
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

    headers = {"Content-Type": "application/json"}

    parts = [{"text": SYSTEM_PROMPT + "\n\nسؤال المستخدم: " + text}]

    if image_base64:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_base64
            }
        })

    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 400
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()

        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = result.get('error', {}).get('message', 'خطأ مجهول')
            return f"يا الزينة قوقل قال: {error_msg}"

    except Exception as e:
        return f"صرات مشكلة يا الزينة 😭: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '❤️🐺 يا الزينة انا نبيلة\nشابة في العشرينات. برمجني مشكاك\nابعتيلي واش حبيتي')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_nabila(text=message.text)
    bot.reply_to(message, reply)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_chat_action(message.chat.id, 'typing')
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
    caption = message.caption if message.caption else None
    reply = ask_nabila(text=caption, image_base64=image_base64)
    bot.reply_to(message, reply)

@app.route('/')
def home():
    return "نبيلة شاعلة 🔥"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

print("نبيلة شعلت 🔥")
threading.Thread(target=run_flask).start()
bot.infinity_polling()
