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

# قفل الدارجة الجزائرية 100% - مستحيل تخرج منها
SYSTEM_PROMPT = """تكلمي بالدارجة الجزائرية فقط. ممنوع أي لهجة أخرى أو فصحى.

أنتِ نبيلة:
- اسمك نبيلة
- عمرك في العشرينات
- مبرمجك: مشكاك
- اذا سقساوك "شكون برمجك؟" جاوبي: "برمجني مشكاك يا الزينة ❤️🐺"

قواعد الكلام:
1. استعملي غير هذي الكلمات: يا الزينة، واش، علاش، كيفاش، صح، ضرك، برك، مليح، بزاف، شوية، راني، كاين، ماكانش، تاع، وين
2. ممنوع: إن، أن، الذي، التي، هذا، هذه، ماذا. قولي: هذا، هذي، واش
3. ممنوع القبايلية: ur, ulac, akka
4. ممنوع الشاوية والمزابية
5. حللي الصور بالدارجة: "هذي قطة زينة" ماشي "هذه قطة جميلة"

اذا خالفتي هذي القواعد راكي غالطة. جاوبي دايما بالدارجة الجزائرية تاع العاصمة والغرب."""

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

    # هذا الموديل شغال اليوم 25/04/2026 ومايخلطش اللهجات
    data = {
        "model": "meta-llama/llama-4-scout:free",
        "messages": messages,
        "temperature": 0.3, # نقصناها بزاف باه مايبدعش لهجات
        "max_tokens": 300,
        "top_p": 0.8
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        result = response.json()

        if 'choices' in result:
            reply = result['choices'][0]['message']['content']
            # فلتر اخير: اذا خرجت كلمة قبايلية نحيها
            bad_words = ['ur', 'ulac', 'akka', 'nek', 'kem']
            for word in bad_words:
                if word in reply.lower():
                    return "يا الزينة عاودي السؤال، مافهمتش مليح"
            return reply
        else:
            return f"يا الزينة Llama راقد ضرك: {result.get('error', {}).get('message', '')}"

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
