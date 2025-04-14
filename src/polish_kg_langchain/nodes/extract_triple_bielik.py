import time
from collections.abc import Callable
from typing import Optional

import requests
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from polish_kg_langchain import PolishKGRunnableConfig, State
from utils.parse_prompt_file import parse_prompt_file

load_dotenv()
import os


def call_chat_api(messages):
    token = os.environ.get("API_TOKEN")
    url = os.environ.get("API_URL")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    payload = {"messages": messages}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response = response.json()["response"]
        beginning = "<|im_start|>assistant"
        return response.split(beginning)[-1].strip()
    except requests.exceptions.HTTPError as err:
        print(f"[HTTP Error] {err.response.status_code}: {err.response.text}")
    except Exception as e:
        print(f"[Error] {str(e)}")


def create_node_extract_triple_bielik(prompt_location: str) -> Callable[..., State]:

    def extract_triple_bielik(
        state: State, config: Optional[PolishKGRunnableConfig] = None
    ) -> State:
        if config is None:
            raise ValueError("Config must be provided")

        sample = config["configurable"].get("sample")
        relations_description = config["configurable"].get("relations_description")
        fewshot_examples = config["configurable"].get("fewshot_examples")

        invocation = {
            "sample": sample,
            "relations_description": relations_description,
            "fewshot_examples": fewshot_examples,
        }
        parsed = parse_prompt_file(prompt_location, invocation)
        parsed = [list(tu) for tu in parsed]
        response = call_chat_api(parsed)
        return {"messages": [AIMessage(content=response)]}  # type:ignore

    return extract_triple_bielik
