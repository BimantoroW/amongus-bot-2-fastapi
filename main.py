import base64
import hashlib
import hmac
import os
from fastapi import FastAPI, Request
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
    is_valid_signature = await linebot.is_valid_signature()
    if is_valid_signature:
        return ("", 200)
    else:
        return ("Invalid LINE signature", 403)
