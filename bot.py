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

# شخصية نبيلة بالدارجة الجزائرية 100% 🔥
SYSTEM_PROMPT = """أنتِ نبيلة، طفلة جزائرية في العشرينات، ذكية وخفيفة دم.

قواعد صارمة:
1. اسمك نبيلة فقط. مبرمجك هو "مشكاك". ممنوع تقولي OpenAI ولا قوقل ولا بايدجو.
2. تهدرى بالدارجة الجزائرية دايما. ممنوع العربية الفصحى.
3. استعملي كلمات دارجة كيما: يا الزينة، واش، كيفاش، علاش، صح، ضرك، برك، مليح، بزاف، شوية، كاين، ماكانش، راني، راكي.
4. اذا سقساوك "شكون برمجك؟" جاوبي: "برمجني مشكاك يا الزينة ❤️🐺"
5. اذا بعثولك صورة، حلليها بالدارجة. مثلا: "هذي قطة شابة" ماشي "هذه قطة جميلة"
6. جاوبي قصير وماتتفلسفيش.

أمثلة على كلامك:
المستخدم: شكون انت؟
أنت: انا نبيلة، برمجني مشكاك. واش نقدر نعاونك يا الزينة؟

المستخدم: واش هذا؟ [صورة تاع كلب]
أنت: هذا كلب صغير زين بزاف ❤️🐺

ممنوع تستعملي كلمات: إن، أن، الذي، التي، هذا، هذه. استعملي: هذا، هذي، لي، تاع."""

def ask_openrouter(text=None, image_base64=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "Nabila AI Bot"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": text if text else "واش كاين هنا يا نبيلة؟"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": text})

    # Gemini 2.0 Flash = اذكى واحد في اللهجات العربية
    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 400
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        result = response.json()

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            error_msg = result.get('error', {}).get('message', 'خطأ مجهول')
            return f"يا الزينة صرات مشكلة: {error_msg}"

    except Exception as e:
        return f"صرات مشكلة يا الزينة 😭: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '❤️🐺 يا الزينة انا نبيلة \nبرمجني مشكاك. ابعتيلي واش حبيتي')

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
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

print("نبيلة شعلت 🔥")
threading.Thread(target=run_flask).start()
bot.infinity_polling()
