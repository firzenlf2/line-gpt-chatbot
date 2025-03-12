# main.py
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = FastAPI()

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def read_root():
    return {"status": "Chatbot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "คุณคือแชทบอทที่ช่วยตรวจสอบวันลาของพนักงาน"},
            {"role": "user", "content": user_text},
        ]
    )
    reply = gpt_response.choices[0].message.content
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
