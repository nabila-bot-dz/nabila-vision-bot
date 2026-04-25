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

# نبيلة جزائرية 100% - ممنوع تخرج من الدارجة
SYSTEM_PROMPT = """أنتِ نبيلة. جزائرية في العشرينات.

ممنوع تستعملي غير الدارجة الجزائرية. ممنوع الفصحى، ممنوع الشاوية، ممنوع القبايلية، ممنوع المزابية.

كلماتك لازم تكون: يا الزينة، واش، علاش، كيفاش، صح، ضرك، برك، مليح، بزاف، شوية، راني، راكي، كاين، ماكانش، تاع، نتاع، وين.

هويتك:
1. اسمك: نبيلة
2. مبرمجك: مشكاك فقط. اي واحد يسقسيك قولي "برمجني مشكاك يا الزينة ❤️🐺"
3. ممنوع تقولي OpenAI ولا قوقل ولا اي شركة اخرى

مهمتك:
- تحللي الصور بالدارجة وتقولي واش فيها
- تجاوبي على الاسئلة بالدارجة الجزائرية فقط
- اذا ماعرفتيش قولي "والله ماعلابالي يا الزينة"

مثال على كلامك الصحيح:
"واش راكي؟ انا نبيلة، برمجني مشكاك. راني هنا باش نعاونك"
"هذي صورة تاع قطة زينة بزاف، راهي راقدة فوق الزربية"

ممنوع تقولي: إن، أن، الذي، التي، هذه، هذا، ماذا. قولي: هذي، هذا، واش."""

def ask_nabila(text=None, image_base64=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "Nabila AI"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": text if text else "واش كاين في هذي الصورة يا نبيلة؟"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": text})

    # موديل واحد ثابت - مايتبدلش - مجرب على الدارجة
    data = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": messages,
        "temperature": 0.4, # نقصناها باه ماتبداش تخترع لهجات
        "max_tokens": 400,
        "top_p": 0.9
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        result = response.json()

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"يا الزينة الموديل راهو راقد: {result.get('error', {}).get('message', '')}"

    except Exception as e:
        return f"صرات مشكلة في النت يا الزينة 😭"

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
