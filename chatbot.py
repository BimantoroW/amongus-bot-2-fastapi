import google.generativeai as genai
import asyncio
import time
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from utils import MessageDB

class ChatBot:
    def __init__(
            self,
            owner_id: str,
            model: genai.GenerativeModel,
            database: MessageDB,
        ) -> None:
        self.owner_id = owner_id
        self.model = model
        self.database = database
        self.chat_session = None
        self.history_index = -1
        self.last_queried = -1
        self.delete_history = False
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    async def start_chat(self) -> None:
        history = await self.database.get_history(self.owner_id)
        self.history_index = len(history)
        self.chat_session = self.model.start_chat(history=history)
    
    async def send_message(self, content: genai.types.ContentType) -> str:
        response = await self.chat_session.send_message_async(content, safety_settings=self.safety_settings)
        return response.text.replace("**", "*").strip()
    
    async def save_reset(self) -> None:
        if self.delete_history:
            await self.database.delete_history(self.owner_id)
        await self.database.insert_history(self.owner_id, self.chat_session.history[self.history_index:])
        self.chat_session = self.model.start_chat()
    
    def reset(self) -> None:
        self.delete_history = True
        self.chat_session = self.model.start_chat()
    
class ChatBotPool:
    def __init__(self, max_bots: int, model: genai.GenerativeModel, database: MessageDB) -> None:
        self.max_bots = max_bots
        self.model = model
        self.database = database
        self.unlocked: dict[str, ChatBot] = dict()
        self.locked: dict[str, ChatBot] = dict()
    
    def empty(self) -> bool:
        return not self.unlocked and not self.locked
    
    def full(self) -> bool:
        return len(self.unlocked) + len(self.locked) == self.max_bots
    
    async def get_bot(self, owner_id: str) -> ChatBot:
        while not self.unlocked and self.locked:
            await asyncio.sleep(1)

        if owner_id in self.unlocked:
            bot = self.unlocked.pop(owner_id)
        else:
            if not self.full():
                bot = ChatBot(owner_id, self.model, self.database)
                await bot.start_chat()
            else:
                bot = self._pop_oldest_unlocked()
                await bot.save_reset()
                bot.owner_id = owner_id
                await bot.start_chat()
        bot.last_queried = time.time()
        self.locked[owner_id] = bot
        return bot
    
    def release_bot(self, bot: ChatBot) -> None:
        self.locked.pop(bot.owner_id)
        self.unlocked[bot.owner_id] = bot
    
    async def clean_pool(self) -> None:
        expiry = 300 # 5 minutes
        now = time.time()
        for bot in list(self.unlocked.values()):
            if now - bot.last_queried >= expiry:
                await bot.save_reset()
                del self.unlocked[bot.owner_id]

    def _pop_oldest_unlocked(self) -> ChatBot:
        oldest = 2 ** 32 - 1
        oldest_bot = None
        for bot in self.unlocked.values():
            if bot.last_queried < oldest:
                oldest = bot.last_queried
                oldest_bot = bot
        return self.unlocked.pop(oldest_bot.owner_id)
