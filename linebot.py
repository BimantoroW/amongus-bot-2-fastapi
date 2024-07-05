import hmac
import base64
import hashlib
import requests
from fastapi import Request
from pprint import pprint

class LineBot:
    def __init__(self, channel_secret: str, access_token: str) -> None:
        self.channel_secret = channel_secret
        self.access_token = access_token
    
    async def is_valid_signature(self, request: Request):
        line_signature = request.headers.get("x-line-signature", None)
        if not line_signature:
            return False
        body = await request.body()
        hash = hmac.new(self.channel_secret.encode(), body, hashlib.sha256).digest()
        signature = base64.b64encode(hash).decode()
        return line_signature == signature
    
    async def execute(self, request: Request):
        endpoint = "https://api.line.me/v2/bot/message/reply"
        body = await request.json()

        for event in body["events"]:
            if event["type"] == "message":
                reply_token = event["replyToken"]
                message = event["message"]["text"]

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }
                data = {
                    "replyToken": reply_token,
                    "messages": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }

                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=data
                )
                pprint(response.json())