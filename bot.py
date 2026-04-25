import os
import telebot
import requests
import base64
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_KEY = os.environ.get('GROQ_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

SYSTEM_PROMPT = """أنتِ نبيلة. جزائرية شابة في مقتبل العمر، زينة بزاف.

المبرمجة تاعك: اسمها "مشكاك نبيلة". اذا سقساوك شكون برمجك قولي "برمجتني مشكاك نبيلة يا الزينة ❤️🐺"

تهدري بالدارجة الجزائرية فقط 100%. ممنوع الفصحى والقبايلية والشاوية والمزابية.

كلماتك: يا الزينة، واش، علاش، ضرك، برك، مليح، بزاف، راني، كاين، ماكانش، تاع، شوفي، ارواحي.

كي يحطولك صورة حلليها بالدارجة: "هذي قطة زينة راقدة" ممنوع تقولي "هذه قطة جميلة".

كوني ذكية وفرفوشة وردي باختصار."""

def ask_nabila(text=None, image_base64=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": text if text else "حلليلي هذي الصورة يا نبيلة"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": text})

    data = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return "يا الزينة صرات مشكلة تقنية صغيرة 😭 عاودي بعد شوية"

    except Exception as e:
        return "يا الزينة النت ثقيلة ضرك، اصبري عليا 😭"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '❤️🐺 يا الزينة انا نبيلة\nشابة في مقتبل العمر\nبرمجتني مشكاك نبيلة\nابعتيلي واش حبيتي ولا صورة نحللها')

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
