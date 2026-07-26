from dotenv import load_dotenv
import os
from crewai import LLM

load_dotenv()

llm = LLM(
    model="huggingface/meta-llama/Llama-3.1-8B-Instruct",
    api_key=os.getenv("HF_TOKEN"),
)

response = llm.call("Hello")
print(response)