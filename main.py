from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

# Initialize FastAPI
app = FastAPI()

# LINE API credentials
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# OpenAI API Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Choose model here (ex: "gpt-4o", "gpt-4", "gpt-3.5-turbo")
OPENAI_MODEL = "gpt-3.5-turbo"

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "Chatbot is running"}

# LINE Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get('X-Line-Signature')
    handler.handle(body.decode('utf-8'), signature)
    return "OK"

# Handle incoming message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    try:
        # Call OpenAI GPT for response
        gpt_response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "คุณคือแชทบอทที่ช่วยตรวจสอบวันลาของพนักงาน"},
                {"role": "user", "content": user_text},
            ],
            max_tokens=500,
            temperature=0.5
        )

        # Extract GPT reply
        reply_text = gpt_response.choices[0].message.content.strip()

    except Exception as e:
        # Handle error and send a friendly message back to user
        reply_text = f"ขออภัยค่ะ เกิดข้อผิดพลาด: {str(e)}"

    # Reply to LINE user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
