# Gemini Line Bot
這是一個利用google開發的gemini模型的api來連接Line機器人的Chat bot [原專案](https://github.com/bowwowxx/GeminiLineBot)

* 具有短期記憶(記憶句數上限可自訂)

* 能通過爬蟲簡單理解網址內容

運作邏輯可以參考[Gemini Discord Bot專案](https://github.com/imyimang/discord-gemini-chat-bot/blob/main/docs/principles.md)
# 前置作業
將需要的機器人設定填入config.json中
```
pip install -U -r requirements.txt
```
將prompt放入**setting.py**(可略過) [教學](https://github.com/imyimang/discord-gemini-chat-bot/blob/main/docs/q3.md)

設定line webhook

執行 `bot.py`

# 指令

`reset` 清空短期記憶

# 常見問題

### [如何獲取gemini api key](https://github.com/imyimang/discord-gemini-chat-bot/blob/main/docs/q2.md)

### [如何獲取LINE_ACCESS_TOKEN/CHANNEL_SECRET](https://hackmd.io/@littlehsun/linechatbot)

### [如何獲取NGROK_AUTHTOKEN](docs/q1.md)

### [如何設定line webhook](docs/q3.md)

### [Gemini不同模型的選擇](docs/q2.md)


