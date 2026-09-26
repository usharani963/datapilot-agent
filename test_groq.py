import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


response = llm.invoke(
    "Explain in one sentence what an AI agent is."
)


print(response.content)