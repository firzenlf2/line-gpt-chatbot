from fastapi import FastAPI, Request, BackgroundTasks

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="ขอเวลาประมวลผลสักครู่...")
    )
    # ประมวลผล DeepSeek ใน background
    background_tasks.add_task(process_with_deepseek, event.source.user_id, user_text)

def process_with_deepseek(user_id, user_text):
    reply = call_deepseek_api(user_text)
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=reply)
    )
