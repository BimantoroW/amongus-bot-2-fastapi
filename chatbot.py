import google.generativeai as genai
import os
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold


load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

async def generate_content(prompt: str) -> str:
    try:
        response = await model.generate_content_async(prompt, safety_settings=safety_settings)
        return response.text.replace("**", "*")
    except ValueError as e:
        return str(e)
