import chatbot
import aiofiles
import httpx
from typing import Any

class Command:
    def __init__(self, triggers: list[str]) -> None:
        self.triggers = triggers
    
    def can_execute(self, message: str) -> bool:
        pass

    async def execute(self, event: dict[str, Any], bot = None) -> dict[str, str] | None:
        pass

    def _image_message(self, content_url: str, preview_url: str | None = None) -> dict[str, str]:
        return {
            "type": "image",
            "originalContentUrl": content_url,
            "previewImageUrl": preview_url if preview_url else content_url
        }
    
    def _text_message(self, text: str) -> dict[str, str]:
        return {
            "type": "text",
            "text": text
        }

    def _extract_message(self, event: dict[str, Any]) -> str:
        return event["message"]["text"]
    
    def _extract_command(self, message: str) -> tuple[str, str | None]:
        try:
            cmd, args = message.split(" ", 1)
            return cmd, args
        except ValueError:
            return message, None

class CockCommand(Command):
    def __init__(self) -> None:
        triggers = ["among us cock"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        return message.lower() == self.triggers[0]
    
    async def execute(self, event: dict[str, Any], bot = None) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            cock_url = "https://i.ytimg.com/vi/d94Nz9s3VBc/sddefault.jpg?v=5f73ada9"
            return self._image_message(cock_url)

class LeaveCommand(Command):
    def __init__(self) -> None:
        triggers = ["/leave", "leave group anjing", "leave anjing"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd = message.split()[0]
        return cmd.lower() == self.triggers[0] or message.lower() == self.triggers[1] or message.lower() == self.triggers[2]
    
    async def execute(self, event: dict[str, Any], bot = None) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            await bot.leave_group(event)

class NiggaCommand(Command):
    def __init__(self) -> None:
        triggers = ["nigga"]
        super().__init__(triggers)
        with open("amongus-bot-2/nword.count", "r") as f:
            self.counter = int(f.read())
    
    def can_execute(self, message: str) -> bool:
        return self.triggers[0] in message.lower()
    
    async def execute(self, event: dict[str, Any], bot = None) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            split = message.lower().split()
            new_count = split.count("nigga") + split.count("niggas")
            self.counter += new_count
            if self.counter % 10 == 0:
                async with aiofiles.open("amongus-bot-2/nword.count", "w") as f:
                    await f.write(str(self.counter))
            return self._text_message(f"Nigga counter: {self.counter}")

class ChatCommand(Command):
    def __init__(self) -> None:
        triggers = ["/chat"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd, args = self._extract_command(message)
        return cmd in self.triggers
    
    async def execute(self, event: dict[str, Any], bot = None) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            cmd, args = self._extract_command(message)
            quote_id = event["message"].get("quotedMessageId", None)
            if quote_id:
                await bot.get_content(quote_id)
            response = await chatbot.generate_content(args)
            return self._text_message(response)

class AvatarCommand(Command):
    def __init__(self) -> None:
        triggers = ["/avatar"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd, args = self._extract_command(message)
        return cmd in self.triggers
    
    async def execute(self, event: dict[str, Any], bot=None) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            mention = event["message"].get("mention", None)
            if mention:
                user_id = mention["mentionees"][0]["userId"]
            else:
                user_id = event["source"]["userId"]

            profile = await bot.get_profile(event, user_id)
            pfp_url = profile.get("pictureUrl", None)
            if pfp_url:
                return self._image_message(pfp_url)
            else:
                return self._text_message("No profile picture set")

commands = [
    CockCommand(),
    LeaveCommand(),
    NiggaCommand(),
    ChatCommand(),
    AvatarCommand()
]
