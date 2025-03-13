# main.py

from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import httpx
import os
import asyncio

# Initialize FastAPI
app = FastAPI()

# LINE API credentials from environment variables
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# DeepSeek API credentials
DEEPSEEK_API_KEY = os.getenv("OPENAI_API_KEY")  # Use your DeepSeek key here
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"  # ✅ Corrected endpoint!

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

# Handle incoming LINE messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # Run DeepSeek API call asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    reply_text = loop.run_until_complete(call_deepseek_api(user_text))
    loop.close()

    # Reply back to LINE user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# Function to call DeepSeek API
async def call_deepseek_api(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",  # ✅ Ensure model is correct
        "messages": [
            {"role": "user", "content": prompt}  # ✅ Minimal history for speed
        ],
        "max_tokens": 200,  # ✅ Limit length for faster response
        "temperature": 0.3,  # ✅ Low creativity for speed
        "stream": False  # ✅ Start with False for now (simpler); can enable later
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:  # ✅ Reduced timeout to 20s
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract and return reply
            return data['choices'][0]['message']['content'].strip()

    except httpx.HTTPStatusError as e:
        print(f"DeepSeek API error: {e.response.status_code} - {e.response.text}")
        return "ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์ DeepSeek"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return "ขออภัยค่ะ เกิดข้อผิดพลาดที่ไม่คาดคิด"
