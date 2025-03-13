import os
import httpx
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Initialize FastAPI
app = FastAPI()

# LINE API
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "Chatbot is running"}

# LINE Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return "OK"

# Handle incoming message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    reply = call_deepseek_api(user_text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ----------------------
# Call DeepSeek API
# ----------------------
def call_deepseek_api(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",  # ใช้ model ที่ DeepSeek แนะนำ
        "messages": [
            {"role": "system", "content": "คุณคือแชทบอทสำหรับช่วยตรวจสอบวันลาพนักงาน"},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = httpx.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"DeepSeek Error: {e}")
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล"
