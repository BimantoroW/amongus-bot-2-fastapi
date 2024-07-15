import os
import command as cmd
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from linebot import LineBot
from utils import MessageDB
from chatbot import ChatBotPool
from google import generativeai as genai


load_dotenv()

db = MessageDB("sqlite3.db")
db.create_tables()

model = genai.GenerativeModel("gemini-1.5-flash")

bot_pool = ChatBotPool(5, model, db)

commands = [
    cmd.CockCommand(),
    cmd.LeaveCommand(),
    cmd.NiggaCommand(),
    cmd.ChatCommand(bot_pool),
    cmd.ResetChatCommand(bot_pool),
    cmd.AvatarCommand(),
]

channel_secret = os.getenv("CHANNEL_SECRET")
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
linebot = LineBot(channel_secret, channel_access_token, commands)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.post("/callback")
async def callback(request: Request):
    is_valid_signature = await linebot.is_valid_signature(request)
    if is_valid_signature:
        bot_pool.clean_pool()
        await linebot.execute(request)
        return ""
    else:
        raise HTTPException(status_code=403, detail="Invalid LINE signature")
