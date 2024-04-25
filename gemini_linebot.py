# gemini_linebot.py
from line_bot_base import LineBot
from linebot.models import (
   TextSendMessage, ImageMessage,
)
import google.generativeai as genai
import os
from pyngrok import ngrok, conf
from PIL import Image
from io import BytesIO
import json
data = json.load(open("config.json", encoding="utf-8"))

GEMINI_API_KEY = data["GEMINI_API_KEY"]
ACCESS_TOKEN = data["ACCESS_TOKEN"]
CHANNEL_SECRET = data["CHANNEL_SECRET"]
NGROK_AUTHTOKEN = data["NGROK_AUTHTOKEN"]
# ngrok
conf.get_default().auth_token = NGROK_AUTHTOKEN
ngrok_tunnel = ngrok.connect(8888)
print("Ngrok Tunnel URL:", ngrok_tunnel.public_url)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')
modelv = genai.GenerativeModel('gemini-pro-vision')
class GeminiLineBot(LineBot):
    def handle_text_message(self, event):
        user_message = "(zh-tw) {}".format(event.message.text)
        response = model.start_chat().send_message(user_message)
        reply_text = response.text

        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text),
        )

    def handle_image_message(self, event):
        message_content = self.line_bot_api.get_message_content(event.message.id)
        image_data = message_content.content
        try:
            img = Image.open(BytesIO(image_data))
        except Exception as e:
            print(f"Error processing image: {e}")
        response = modelv.generate_content(["Use traditional Chinese to describe the content based on this image", img], stream=True)
        response.resolve()            
        reply_text = response.text

        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text),
        )

if __name__ == "__main__":
    bot = GeminiLineBot(ACCESS_TOKEN, CHANNEL_SECRET)
    app = bot.create_app()
    app.run(host='0.0.0.0',port=8888)
