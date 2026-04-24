import os
import telebot
import requests
import base64

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def ask_openrouter(prompt, image_base64=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "user", "content": []}]

    if image_base64:
        messages[0]["content"] = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    else:
        messages[0]["content"] = [{"type": "text", "text": prompt}]

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "max_tokens": 1000
    }

    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
    return r.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "يا الزينة انا نبيلة الذكية 🐺❤️\nابعتيلي نص ولا صورة ونجاوبك")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_base64 = base64.b64encode(downloaded_file).decode('utf-8')

        caption = message.caption or "وش كاين في هذي الصورة؟ اشرحيلي بالدارجة"
        reply = ask_openrouter(caption, image_base64)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"صرات مشكلة يا الزينة 😭\n{e}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = ask_openrouter(f"جاوبي بالدارجة الجزائرية: {message.text}")
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"صرات مشكلة يا الزينة 😭\n{e}")

print("نبيلة شعلت 🔥")
bot.infinity_polling()
