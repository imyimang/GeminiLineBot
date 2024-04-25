from line_bot_base import LineBot
from linebot.models import (
   TextSendMessage, ImageMessage,
)
import google.generativeai as genai
from pyngrok import ngrok, conf
from PIL import Image
from io import BytesIO
from setting import history
from setting import generation_config
from setting import safety_settings
import json

data = json.load(open("config.json", encoding="utf-8"))
log = {} 

GEMINI_API_KEY = data["GEMINI_API_KEY"]
ACCESS_TOKEN = data["ACCESS_TOKEN"]
CHANNEL_SECRET = data["CHANNEL_SECRET"]
NGROK_AUTHTOKEN = data["NGROK_AUTHTOKEN"]

# ngrok
conf.get_default().auth_token = NGROK_AUTHTOKEN
ngrok_tunnel = ngrok.connect(8888)
print("Ngrok Tunnel URL:", ngrok_tunnel.public_url)


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

modelv = genai.GenerativeModel(model_name="gemini-pro-vision", generation_config=generation_config, safety_settings=safety_settings)

class GeminiLineBot(LineBot):
    def handle_text_message(self, event):
        user_id = event.source.user_id
        print(user_id)
        user_message = f"使用者:{event.message.text}"
        update_message_history(user_id, user_message)
        response = model.start_chat(history=history).send_message(get_formatted_message_history(user_id))
        reply_text = response.text
        update_message_history(user_id, reply_text)

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

def update_message_history(channel_id, text): 
    if channel_id in log:  
        log[channel_id].append(text)  
        if len(log[channel_id]) > data["memory_max"]:
            log[channel_id].pop(0) 
    else:
        log[channel_id] = [text] 

def get_formatted_message_history(channel_id):
    if channel_id in log: 
        return '\n\n'.join(log[channel_id]) 

if __name__ == "__main__":
    bot = GeminiLineBot(ACCESS_TOKEN, CHANNEL_SECRET)
    app = bot.create_app()
    app.run(host='0.0.0.0',port=8888)

