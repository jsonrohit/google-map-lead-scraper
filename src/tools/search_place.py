import os
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool

load_dotenv()

@tool
def search_place(query: str):
    '''Search for a place using the Serper API and return the JSON response.'''
    API_KEY = os.getenv("SERPER_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }

    payload = {
        "q": query
    }

    response = requests.post("https://google.serper.dev/places", headers=headers, json=payload)
    return response.json()