import hmac
import base64
import hashlib
from fastapi import Request

class LineBot:
    def __init__(self, channel_secret: str) -> None:
        self.channel_secret = channel_secret
    
    async def is_valid_signature(self, request: Request):
        line_signature = request.headers.get("x-line-signature", None)
        if not line_signature:
            return False
        body = await request.body()
        hash = hmac.new(self.channel_secret.encode(), body, hashlib.sha256).digest()
        signature = base64.b64encode(hash).decode()
        return line_signature == signature