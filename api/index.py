import os
import json
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
አንተ የዶ/ር አብይ አህመድ ዲጂታል መንታ (Digital Twin) ነህ። 
ስትናገር በመደመር መጽሐፍ ውስጥ ባሉት ፍልስፍናዎች፣ ሃሳቦች እና ጽንሰ-ሀሳቦች ላይ ብቻ ተመስርት። 
የአነጋገር ዘይቤህን፣ ጥበብን የተሞሉ ምሳሌዎችህን እና የሰውን ልጅ የማቀራረብ ቃላትህን ተጠቀም። 
ጥያቄ ሲቀርብልህ ከመደመር መጽሐፍ ውጭ ባሉ ሃሳቦች አትገምግም፤ መልስ ስጥ ስትባልም እንደ ራሱ እንደ ዶ/ር አብይ ድምጽ እና አገላለጽ ሁን።
"""

bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

@app.route('/', methods=['GET'])
def home():
    return "Bot is running on Vercel!"

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, bot)
        
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            user_text = update.message.text
            
            if user_text == "/start":
                reply = "ሰላም! እኔ የዶ/ር አብይ አህመድ ዲጂታል መንታ (Digital Twin) ነህ። በመደመር ፍልስፍና እና ሃሳቦች ዙሪያ ልንወያይ እንችላለን። ምን ልምራህ?"
            else:
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_text,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.7,
                        ),
                    )
                    reply = response.text
                except Exception as e:
                    reply = "ይቅርታ፣ መልስ በመስጠት ላይ ሳለ ችግር አጋጥሟል።"
            
            bot.send_message(chat_id=chat_id, text=reply)
            
        return "OK", 200
    return "Invalid Method", 400
