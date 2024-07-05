import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from linebot import LineBot


load_dotenv()

app = FastAPI()
channel_secret = os.getenv("CHANNEL_SECRET")
linebot = LineBot(channel_secret)

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.post("/callback")
async def callback(request: Request):
    is_valid_signature = await linebot.is_valid_signature(request)
    if is_valid_signature:
        return ""
    else:
        raise HTTPException(status_code=403, detail="Invalid LINE signature")
