import os
import json
import logging
from flask import Flask, request
from telegram import Bot
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

@app.route('/', methods=['GET'])
@app.route('/api/index.py', methods=['GET'])
def home():
    return "Bot is running on Vercel!"

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            update_data = request.get_json(force=True)
            
            if "message" in update_data and "text" in update_data["message"]:
                chat_id = update_data["message"]["chat"]["id"]
                user_text = update_data["message"]["text"]
                
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                
                if user_text == "/start":
                    reply = "ሰላም! እኔ የዶ/ር አብይ አህመድ ዲጂታል መንታ (Digital Twin) ነኝ። በመደመር ፍልስፍና እና ሃሳቦች ዙሪያ ልንወያይ እንችላለን። ምን ልምራህ?"
                else:
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=user_text,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_INSTRUCTION,
                                temperature=0.7,
                            ),
                        )
                        reply = response.text
                    except Exception as gen_err:
                        reply = f"ይቅርታ፣ በ Gemini API በኩል ችግር አጋጥሟል፦ {str(gen_err)}"
                
                bot.send_message(chat_id=chat_id, text=reply)
        except Exception as e:
            print(f"Error: {e}")
            
        return "OK", 200
    return "Invalid Method", 400
