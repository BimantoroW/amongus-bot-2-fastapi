import chatbot
from typing import Any

class Command:
    def __init__(self, triggers: list[str]) -> None:
        self.triggers = triggers
    
    def can_execute(self, message: str) -> bool:
        pass

    def _extract_message(self, event: dict[str, Any]) -> str:
        return event["message"]["text"]
    
    def _extract_command(self, message: str) -> tuple[str, str | None]:
        try:
            cmd, args = message.split(" ", 1)
            return cmd, args
        except ValueError:
            return message, None

class ReplyCommand(Command):
    def __init__(self, triggers: list[str]) -> None:
        super().__init__(triggers)

    def execute(self, event: dict[str, Any]) -> dict[str, str] | None:
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

class ActionCommand(Command):
    def __init__(self, triggers: list[str]) -> None:
        super().__init__(triggers)
    
    def execute(self, event: dict[str, Any], bot) -> None:
        pass

class CockCommand(ReplyCommand):
    def __init__(self) -> None:
        triggers = ["among us cock"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        return message.lower() == self.triggers[0]
    
    def execute(self, event: dict[str, Any]) -> dict[str, str] | None:
        message = self._extract_message(event)
        if self.can_execute(message):
            cock_url = "https://i.ytimg.com/vi/d94Nz9s3VBc/sddefault.jpg?v=5f73ada9"
            return self._image_message(cock_url)

class LeaveCommand(ActionCommand):
    def __init__(self) -> None:
        triggers = ["/leave", "leave group anjing", "leave anjing"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd = message.split()[0]
        return cmd.lower() == self.triggers[0] or message.lower() == self.triggers[1] or message.lower() == self.triggers[2]
    
    def execute(self, event: dict[str, Any], bot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            bot.leave_group(event)

class NiggaCommand(ReplyCommand):
    def __init__(self) -> None:
        triggers = ["nigga"]
        super().__init__(triggers)
        with open("amongus-bot-2/nword.count", "r") as f:
            self.counter = int(f.read())
    
    def can_execute(self, message: str) -> bool:
        return self.triggers[0] in message.lower()
    
    def execute(self, event: dict[str, Any]) -> dict[str, str]:
        message = self._extract_message(event)
        if self.can_execute(message):
            new_count = message.lower().split().count("nigga")
            self.counter += new_count
            if self.counter % 10 == 0:
                with open("amongus-bot-2/nword.count", "w") as f:
                    f.write(str(self.counter))
            return self._text_message(f"Nigga counter: {self.counter}")

class ChatCommand(ReplyCommand):
    def __init__(self) -> None:
        triggers = ["/chat"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd, args = self._extract_command(message)
        return cmd in self.triggers and args
    
    def execute(self, event: dict[str, Any]) -> dict[str, str]:
        message = self._extract_message(event)
        if self.can_execute(message):
            args = message.lower().split(" ", 1)[1]
            response = chatbot.generate_content(args)
            return self._text_message(response)

commands = [
    CockCommand(),
    LeaveCommand(),
    NiggaCommand(),
    ChatCommand()
]
