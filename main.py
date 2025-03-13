from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = FastAPI()  # <<< สำคัญมาก

# LINE Bot API
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.get("/")
def read_root():
    return {"status": "Chatbot is running"}


@app.post("/webhook")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers.get('X-Line-Signature', '')

    try:
        handler.handle(body.decode('utf-8'), signature)
    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"message": "Invalid signature"}, status_code=400)
    return JSONResponse(content={"message": "OK"}, status_code=200)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    print(f"User: {user_text}")  # Log ข้อความที่พิมพ์

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "คุณคือแชทบอทที่ช่วยตรวจสอบวันลาของพนักงาน"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("OpenAI Error:", e)
        reply_text = "ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล"

    # ส่งกลับไปหา LINE User
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
