from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

print("KEY FOUND:", key[:20] if key else "NO KEY")