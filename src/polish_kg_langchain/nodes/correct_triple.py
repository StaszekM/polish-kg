from collections.abc import Callable
from typing import Optional

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace

from polish_kg_langchain import PolishKGRunnableConfig, State
from utils.parse_prompt_file import parse_prompt_file
from utils.validate_interpolation import validate_interpolation


def create_node_correct_triple(
    prompt_location: str,
) -> Callable[..., State]:
    def correct_triple(
        state: State, config: Optional[PolishKGRunnableConfig] = None
    ) -> State:
        if config is None:
            raise ValueError("Config must be provided")
        parsed = parse_prompt_file(prompt_location)
        template = ChatPromptTemplate.from_messages(parsed)
        response = state["messages"][-1].content

        invocation = {"response": response}
        validate_interpolation(str(parsed), invocation)

        prompt: ChatPromptValue = template.invoke(invocation)  # type:ignore

        chat: ChatHuggingFace = config["configurable"].get("base_llm_zero_temp")
        result = chat.invoke(prompt)

        return {"messages": [result]}  # type: ignore

    return correct_triple
