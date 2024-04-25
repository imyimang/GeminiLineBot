from line_bot_base import LineBot
from linebot.models import (
   TextSendMessage, ImageMessage,
)
import google.generativeai as genai
from pyngrok import ngrok, conf
from PIL import Image
from io import BytesIO
from setting import history,generation_config,safety_settings
from spider import islink,gettitle
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

        if event.message.text.lower() == "reset": #如果訊息內容="reset"
            if user_id in log:
                del log[user_id] #清空短期記憶
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="已清空短期記憶"),
                )        
                
            else:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="尚無儲存的短期記憶"),
                )      
            return
        
        links = islink(event.message.text)
        #如果訊息內容有連結
        if links:
            links = '\n'.join(links)
            title = gettitle(links) #取得連結中的title
            if title:
                word = event.message.text.replace(links, f"(一個網址，網址標題是:'{title}')")
                reply_text =f"使用者說:'{word}'"  #將連結網站的title放入短期記憶
            else:
                word = event.message.text.replace(links, "(一個網址，網址無法辨識)")
                reply_text = f"使用者說:'{word}'"

            update_message_history(user_id, reply_text)
            response = model.start_chat(history=history).send_message(get_formatted_message_history(user_id))
            self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response.text),
        )
            return

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

