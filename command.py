from typing import Any
from dotenv import load_dotenv
import google.generativeai as genai
import os


load_dotenv()

api_key = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

class Command:
    def __init__(self, triggers: list[str]) -> None:
        self.triggers = triggers
    
    def can_execute(self, message: str) -> bool:
        pass

    def execute(self, event: dict[str, Any], bot) -> None:
        pass

    def _extract_reply_token(self, event: dict[str, Any]) -> str:
        return event["replyToken"]
    
    def _extract_message(self, event: dict[str, any]) -> str:
        return event["message"]["text"]

class CockCommand(Command):
    def __init__(self) -> None:
        triggers = ["among us cock"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        return message.lower() == self.triggers[0]
    
    def execute(self, event: dict[str, Any], bot) -> None:
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
    
    def execute(self, event: dict[str, Any], bot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            source_type = event["source"]["type"]
            if source_type == "group":
                group_id = event["source"]["groupId"]
                bot.leave_group(group_id)
            elif source_type == "room":
                room_id = event["source"]["roomId"]
                bot.leave_group(room_id, True)

class NiggaCommand(Command):
    def __init__(self) -> None:
        triggers = ["nigga"]
        super().__init__(triggers)
        with open("amongus-bot-2/nword.count", "r") as f:
            self.counter = int(f.read())
    
    def can_execute(self, message: str) -> bool:
        return self.triggers[0] in message.lower()
    
    def execute(self, event: dict[str, Any], bot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            new_count = message.lower().split().count("nigga")
            self.counter += new_count
            reply_token = self._extract_reply_token(event)
            messages = [bot.text_message(f"Nigga counter: {self.counter}")]
            bot.send_reply(reply_token, messages)
            if self.counter % 10 == 0:
                with open("amongus-bot-2/nword.count", "w") as f:
                    f.write(str(self.counter))

class ChatCommand(Command):
    def __init__(self) -> None:
        triggers = ["/chat"]
        super().__init__(triggers)
    
    def can_execute(self, message: str) -> bool:
        try:
            cmd, args = message.lower().split(" ", 1)
            return cmd in self.triggers and args != ""
        except ValueError:
            return False
    
    def execute(self, event: dict[str, Any], bot) -> None:
        message = self._extract_message(event)
        if self.can_execute(message):
            args = message.lower().split(" ", 1)[1]
            response = model.generate_content(args)
            reply_token = self._extract_reply_token(event)
            messages = [bot.text_message(response.text)]
            bot.send_reply(reply_token, messages)

commands = [
    CockCommand(),
    LeaveCommand(),
    NiggaCommand(),
    ChatCommand()
]
