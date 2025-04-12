from collections.abc import Callable
from typing import Optional

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate

from polish_kg_langchain import PolishKGRunnableConfig, State
from utils.parse_prompt_file import parse_prompt_file
from utils.validate_interpolation import validate_interpolation


def create_node_extract_triple(prompt_location: str) -> Callable[..., State]:
    def extract_triple(state: State, config: Optional[PolishKGRunnableConfig] = None) -> State:
        if config is None:
            raise ValueError("Config must be provided")

        parsed = parse_prompt_file(prompt_location)

        template = ChatPromptTemplate.from_messages(
            parsed
        )

        sample = config["configurable"].get("sample")
        relations_description = config["configurable"].get("relations_description")
        fewshot_examples = config["configurable"].get("fewshot_examples")

        invocation = {
            "sample": sample,
            "relations_description": relations_description,
            "fewshot_examples": fewshot_examples,
        }
        validate_interpolation(str(parsed), invocation)

        prompt: ChatPromptValue = template.invoke(invocation)  # type:ignore

        chat = config['configurable'].get('base_llm')
        result = chat.invoke(prompt.messages)
        return {"messages": [*prompt.messages, result]}  # type: ignore

    return extract_triple
