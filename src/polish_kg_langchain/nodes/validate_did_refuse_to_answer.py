from collections.abc import Callable
from typing import Literal

from git import Optional
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace
from langgraph.types import Command

from polish_kg_langchain import PolishKGRunnableConfig, State
from utils.parse_prompt_file import parse_prompt_file
from utils.validate_interpolation import validate_interpolation


def create_node_validate_did_refuse_to_answer(
    prompt_location: str,
) -> Callable[..., Command]:
    def validate_did_refuse_to_answer(
        state: State,
        config: Optional[PolishKGRunnableConfig] = None,
    ) -> Command[Literal["validate_did_format_correctly", "extract_triple_bielik"]]:
        if config is None:
            raise ValueError("Config must be provided")
        response = state["messages"][-1].content
        parsed = parse_prompt_file(prompt_location)

        chat: ChatHuggingFace = config["configurable"].get("base_llm")

        template = ChatPromptTemplate.from_messages(parsed)
        invocation = {
            "response": response,
        }
        validate_interpolation(str(parsed), invocation)
        prompt: ChatPromptValue = template.invoke(invocation)  # type:ignore

        result = chat.invoke(prompt)
        result_cleaned = str(result.content)

        did_attempt_to_answer: bool
        goto: str
        if result_cleaned.lower().startswith("tak"):
            goto = "extract_triple_bielik"
            did_attempt_to_answer = False
        elif result_cleaned.lower().startswith("nie"):
            goto = "validate_did_format_correctly"
            did_attempt_to_answer = True
        else:
            raise ValueError(
                f"Unexpected response from the model: {result_cleaned}. Expected 'Tak' or 'Nie'."
                "validate_did_refuse_to_answer"
            )

        return Command(
            update={
                "attempt_checker_messages": [*prompt.messages, result],  # type:ignore
                "did_attempt_to_answer": did_attempt_to_answer,
            },
            goto=goto,
        )

    return validate_did_refuse_to_answer
