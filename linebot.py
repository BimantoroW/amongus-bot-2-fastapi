import hmac
import base64
import hashlib
import requests
from fastapi import Request
from pprint import pprint
from command import commands


proxies = {
    "http": "proxy.server:3128",
    "https": "proxy.server:3128"
}

class LineBot:
    def __init__(self, channel_secret: str, access_token: str) -> None:
        self.channel_secret = channel_secret
        self.access_token = access_token
        self.commands = commands
    
    async def is_valid_signature(self, request: Request):
        line_signature = request.headers.get("x-line-signature", None)
        if not line_signature:
            return False
        body = await request.body()
        hash = hmac.new(self.channel_secret.encode(), body, hashlib.sha256).digest()
        signature = base64.b64encode(hash).decode()
        return line_signature == signature
    
    async def execute(self, request: Request):
        body = await request.json()
        for event in body["events"]:
            if event["type"] == "message":
                for cmd in self.commands:
                    cmd.execute(event, self)

    def send_reply(self, reply_token: str, messages: list[dict[str, str]]):
        endpoint = "https://api.line.me/v2/bot/message/reply"
        headers = self.__generate_headers(True, True)
        data = {
            "replyToekn": reply_token,
            "messages": messages
        }
        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            proxies=proxies
        )
        pprint(response.json())
    
    def leave_group(self, group_id: str, is_room: bool = False):
        if is_room:
            endpoint = f"https://api.line.me/v2/bot/room/{group_id}/leave"
        else:
            endpoint = f"https://api.line.me/v2/bot/group/{group_id}/leave"
        headers = self.__generate_headers(False, True)
        response = requests.post(
            endpoint,
            headers=headers,
            proxies=proxies
        )
        pprint(response.json())

    def image_message(content_url: str, preview_url: str | None = None):
        return {
            "type": "image",
            "originalContentUrl": content_url,
            "previewImageUrl": preview_url if not preview_url else content_url
        }
    

    def __generate_headers(self, content_type: bool, authorization: bool):
        headers = {}
        if content_type:
            headers["Content-Type"] = "application/json"
        if authorization:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    