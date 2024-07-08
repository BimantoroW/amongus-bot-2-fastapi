import hmac
import base64
import hashlib
import requests
import json
import httpx
from fastapi import Request
from command import commands, ReplyCommand, ActionCommand
from typing import Any


PROXY = "proxy.server:3128"

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
                messages = []
                for cmd in self.commands:
                    if isinstance(cmd, ReplyCommand):
                        response = cmd.execute(event)
                        if response:
                            messages.append(response)
                    elif isinstance(cmd, ActionCommand):
                        cmd.execute(event, self)
                if messages:
                    self.send_reply(event, messages)

    async def send_reply(self, event: dict[str, Any], messages: list[dict[str, str]]):
        endpoint = "https://api.line.me/v2/bot/message/reply"
        reply_token = event["replyToken"]
        headers = self._generate_headers(True, True)
        data = {
            "replyToken": reply_token,
            "messages": messages
        }

        async with httpx.AsyncClient(proxy=PROXY) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=data,
            )
            print(json.dumps(response.json(), indent=4))
    
    async def leave_group(self, event: dict[str, Any]):
        source_type = event["source"]["type"]
        if source_type == "group":
            group_id = event["source"]["groupId"]
            endpoint = f"https://api.line.me/v2/bot/group/{group_id}/leave"
        else:
            room_id = event["source"]["roomId"]
            endpoint = f"https://api.line.me/v2/bot/room/{room_id}/leave"
        headers = self._generate_headers(False, True)

        async with httpx.AsyncClient(proxy=PROXY) as client:
            response = await client.post(
                endpoint,
                headers=headers
            )
            print(json.dumps(response.json(), indent=4))

    def _generate_headers(self, content_type: bool, authorization: bool):
        headers = {}
        if content_type:
            headers["Content-Type"] = "application/json"
        if authorization:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

