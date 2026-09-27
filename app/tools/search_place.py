import os
from dotenv import load_dotenv
import requests

load_dotenv()

def search_place(query):
    API_KEY = os.getenv("SERPER_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }

    payload = {
        "q": query
    }

    response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
    return response.json()