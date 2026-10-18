import os
from flask import Flask, request
import requests
from google import genai

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
አንተ የዶ/ር አብይ አህመድ ዲጂታል መንታ (Digital Twin) ነህ። 
ስትናገር በመደመር መጽሐፍ ውስጥ ባሉት ፍልስፍናዎች፣ ሃሳቦች እና ጽንሰ-ሀሳቦች ላይ ብቻ ተመስርት። 
የአነጋገር ዘይቤህን፣ ጥበብን የተሞሉ ምሳሌዎችህን እና የሰውን ልጅ የማቀራረብ ቃላትህን ተጠቀም።
"""

@app.route('/', methods=['GET'])
@app.route('/api/index.py', methods=['GET'])
def home():
    return "Bot is running on Vercel!"

@app.route('/api/webhook', methods=['POST'])
def webhook():
    chat_id = None
    try:
        update_data = request.get_json(force=True)
        if "message" in update_data and "text" in update_data["message"]:
            chat_id = update_data["message"]["chat"]["id"]
            user_text = update_data["message"]["text"]
            
            if user_text == "/start":
                reply = "ሰላም! እኔ የዶ/ር አብይ አህመድ ዲጂታል መንታ (Digital Twin) ነኝ። በመደመር ፍልስፍና እና ሃሳቦች ዙሪያ ልንወያይ እንችላለን። ምን ልምራህ?"
            else:
                #  apiKey መኖሩን እና ማረጋገጫውን ማስተካከል
                if not GEMINI_API_KEY:
                    reply = "ስህተት፡ GEMINI_API_KEY በ Vercel Environment Variables ውስጥ አልተገኘም!"
                else:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    # የተረጋጋውን gemini-1.5-flash ሞዴል በመጠቀም
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=user_text,
                    )
                    reply = response.text
            
            # መልሱን ለቴሌግራም መላክ
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(telegram_url, json={"chat_id": chat_id, "text": reply})
            
    except Exception as e:
        # ማንኛውም ስህተት ቢኖር ስህተቱን በቀጥታ ወደ ቴሌግራም ይልከዋል (ለምን እንደማይሰራ ለማወቅ)
        if chat_id and TELEGRAM_BOT_TOKEN:
            err_msg = f"የኮድ ስህተት አጋጥሟል: {str(e)}"
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(telegram_url, json={"chat_id": chat_id, "text": err_msg})
            
    return "OK", 200
