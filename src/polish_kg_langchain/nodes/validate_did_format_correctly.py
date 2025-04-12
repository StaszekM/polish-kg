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


def create_node_validate_did_format_correctly(
    prompt_location: str,
) -> Callable[..., Command]:
    def validate_did_format_correctly(
        state: State,
        config: Optional[PolishKGRunnableConfig] = None,
    ) -> Command[Literal["to_evaluation", "correct_triple"]]:
        if config is None:
            raise ValueError("Config must be provided")

        response = state["messages"][-1].content
        parsed = parse_prompt_file(prompt_location)

        template = ChatPromptTemplate.from_messages(parsed)
        invocation = {
            "response": response,
        }
        validate_interpolation(str(parsed), invocation)

        prompt: ChatPromptValue = template.invoke(invocation)  # type:ignore

        chat: ChatHuggingFace = config["configurable"].get("base_llm")
        result = chat.invoke(prompt)
        result_cleaned = str(result.content)

        has_correct_format: bool
        goto: str
        if result_cleaned.lower().startswith("tak"):
            has_correct_format = True
            goto = "to_evaluation"
        elif result_cleaned.lower().startswith("nie"):
            has_correct_format = False
            goto = "correct_triple"
        else:
            raise ValueError(
                f"Unexpected response from the model: {result_cleaned}. Expected 'Tak' or 'Nie'."
                "validate_did_format_correctly"
            )

        return Command(
            update={
                "format_checker_messages": [*prompt.messages, result],  # type:ignore
                "has_correct_format": has_correct_format,
            },
            goto=goto,
        )

    return validate_did_format_correctly
