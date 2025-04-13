import requests
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from polish_kg_langchain import State

load_dotenv()
import os


def call_chat_api(
    messages,
    token,
):
    token = os.environ.get("API_TOKEN")
    url = os.environ.get("API_URL")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    payload = {"messages": messages}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.HTTPError as err:
        print(f"[HTTP Error] {err.response.status_code}: {err.response.text}")
    except Exception as e:
        print(f"[Error] {str(e)}")


def extract_triple_bielik(state: State) -> State:
    return {"messages": [AIMessage(content="Odpowiedź z Bielika")]}  # type:ignore
