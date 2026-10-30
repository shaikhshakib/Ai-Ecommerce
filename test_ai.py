from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model = "gpt-4.1-mini",
    input = "Reply with only: Celeste Rose Ai is working" 
)

print(response.output_text)