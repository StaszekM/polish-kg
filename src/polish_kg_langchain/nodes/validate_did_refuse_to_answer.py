from typing import Literal

from git import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace
from langgraph.types import Command

from polish_kg_langchain import PolishKGRunnableConfig, State


def validate_did_refuse_to_answer(
    state: State,
    config: Optional[PolishKGRunnableConfig] = None,
) -> Command[Literal["validate_did_format_correctly", "extract_triple_bielik"]]:
    if config is None:
        raise ValueError("Config must be provided")
    response = state["messages"][-1].content

    chat: ChatHuggingFace = config["configurable"].get("base_llm")  

    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Oceń, czy w podanym tekście odmówiono odpowiedzi. Jeśli odmówiono, odpowiedz 'Tak'. Jeśli nie odmówiono, odpowiedz 'Nie'. Odpowiedz wyłącznie 'Tak' lub 'Nie', bez podawania innych informacji. Przykładowo: Odmowa ma treść 'nie ma relacji', 'nie umiem odpowiedzieć', 'nie wiem', 'nie ma związku', 'brakuje informacji' i podobne zaprzeczenia.",
            ),
            ("user", "Tekst: {response}"),
        ]
    )
    prompt = template.invoke(
        {
            "response": response,
        }
    )

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
            "attempt_checker_messages": [*prompt.messages, result], #type:ignore
            "did_attempt_to_answer": did_attempt_to_answer,
        },
        goto=goto,
    )
