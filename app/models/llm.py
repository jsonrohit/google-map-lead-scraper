from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json

load_dotenv()

def get_llm():
    '''Initialize and return a Groq LLM instance.'''

    # Initialize Groq LLM
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.7
    )
    
    return llm

    # result = chain.invoke({"input": description})
    # print(json.dumps(result, indent=2))