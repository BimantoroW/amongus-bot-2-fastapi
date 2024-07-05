import hmac
import base64
import hashlib
import requests
from fastapi import Request
from pprint import pprint


proxies = {
    "http": "proxy.server:3128",
    "https": "proxy.server:3128"
}

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
                message = event["message"]["text"]
                if message.lower() == "among us cock":
                    reply_token = event["replyToken"]
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.access_token}"
                    }
                    data = {
                        "replyToken": reply_token,
                        "messages": [
                            {
                                "type": "image",
                                "originalContentUrl": "https://i.ytimg.com/vi/d94Nz9s3VBc/sddefault.jpg?v=5f73ada9",
                                "previewImageUrl": "https://i.ytimg.com/vi/d94Nz9s3VBc/sddefault.jpg?v=5f73ada9"
                            }
                        ]
                    }

                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=data,
                        proxies=proxies
                    )
                    pprint(response.json())
                elif message.lower() == "/leave":
                    type = event["source"]["type"]
                    if type == "group":
                        group_id = event["source"]["groupId"]
                        endpoint = f"https://api.line.me/v2/bot/group/{group_id}/leave"
                        headers = {
                            "Authorization": f"Bearer {self.access_token}"
                        }
                        response = requests.post(
                            endpoint,
                            headers=headers,
                            proxies=proxies
                        )
                        pprint(reponse.json())
                    elif type == "room":
                        room_id = event["source"]["roomId"]
                        endpoint = f"https://api.line.me/v2/bot/room/{room_id}/leave"
                        headers = {
                            "Authorization": f"Bearer {self.access_token}"
                        }
                        response = requests.post(
                            endpoint,
                            headers=headers,
                            proxies=proxies
                        )
                        pprint(reponse.json())
