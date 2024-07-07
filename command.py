from linebot import LineBot
from typing import Any

class Command:
    def __init__(self, triggers: list[str]) -> None:
        self.triggers = triggers
    
    def can_execute(self, message: str) -> bool:
        pass

    def execute(self, event: dict[str, Any], bot: LineBot) -> None:
        pass

    def _extract_reply_token(self, event: dict[str, Any]) -> str:
        return event["reply_token"]
    
    def _extract_message(self, event: dict[str, any]) -> str:
        return event["message"]["text"]

class CockCommand(Command):
    def __init__(self) -> None:
        triggers = ["among us cock"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        return message.lower() == self.triggers[0]
    
    def execute(self, event: dict[str, Any], bot: LineBot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            cock_url = "https://i.ytimg.com/vi/d94Nz9s3VBc/sddefault.jpg?v=5f73ada9"
            messages = [bot.image_message(cock_url)]
            reply_token = self._extract_reply_token(event)
            bot.send_reply(reply_token, messages)

class LeaveCommand(Command):
    def __init__(self) -> None:
        triggers = ["/leave", "leave group anjing"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        cmd = message.split()[0]
        return cmd.lower() == self.triggers[0] or message.lower() == self.triggers[1]
    
    def execute(self, event: dict[str, Any], bot: LineBot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            source_type = event["source"]["type"]
            if source_type == "group":
                group_id = event["source"]["groupId"]
                bot.leave_group(group_id)
            elif source_type == "room":
                room_id = event["source"]["roomId"]
                bot.leave_group(room_id, True)

commands = [
    CockCommand(),
    LeaveCommand()
]