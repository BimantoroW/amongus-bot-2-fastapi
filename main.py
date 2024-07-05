import base64
import hashlib
import hmac
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
channel_secret = os.getenv("CHANNEL_SECRET").encode("utf-8")

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    hash = hmac.new(channel_secret, body, hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode("utf-8")
    x_line_signature = request.headers["x-line-signature"]

    print(f"{signature = }")
    print(f"{x_line_signature = }")
    print(f"is_valid_signature = {signature == x_line_signature}")
    return ("", 200)
