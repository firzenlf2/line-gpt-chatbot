from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# แก้ตรงส่วนนี้
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    gpt_response = client.chat.completions.create(
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
