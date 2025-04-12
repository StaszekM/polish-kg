from typing import Literal

from git import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace
from langgraph.types import Command

from polish_kg_langchain import PolishKGRunnableConfig, State


def validate_did_format_correctly(
    state: State,
    config: Optional[PolishKGRunnableConfig] = None,
) -> Command[Literal["to_evaluation", "correct_triple"]]:
    if config is None:
        raise ValueError("Config must be provided")
    chat: ChatHuggingFace = config["configurable"].get("base_llm")

    # this prompt needs improvement and possibly splitting into checking and correcting
    response = state["messages"][-1].content
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Oceń, czy podany tekst jest dokładnie w formacie [[Obiekt1, Relacja, Obiekt2]]. Jeśli tekst jest w poprawnym formacie, odpowiedz 'Tak'. Jeśli nie jest, odpowiedz 'Nie'. Nie podawaj żadnych innych informacji ani wyjaśnień.
Tekst jest w poprawnym formacie, jeśli:
1. Zawiera dokładnie jedną trójkę Obiekt1, Relacja, Obiekt2.
2. Tekst zaczyna się podwójnym nawiasem kwadratowym '[['.
3. Tekst kończy się podwójnym nawiasem kwadratowym ']]'.
4. Obiekt1, Relacja i Obiekt2 są oddzielone przecinkami ','.
5. Obiekt1, Relacja i Obiekt2 nie są otoczone pojedynczymi ani podwójnymi cudzysłowami.

Przykłady niepoprawnych formatów wraz z odpowiedziami:
Tekst: [Obiekt1, Relacja, Obiekt2]
Odpowiedź: Nie

Tekst: [[Obiekt1, Relacja, Obiekt2]
Odpowiedź: Nie

Tekst: ['Obiekt1', 'Relacja', 'Obiekt2']
Odpowiedź: Nie

Tekst: [(Obiekt1, Relacja, Obiekt2)]
Odpowiedź: Nie

Tekst: ["Obiekt1", "Relacja", "Obiekt2"]
Odpowiedź: Nie

Przykłady poprawnych formatów:
Tekst: [[Obiekt1, Relacja, Obiekt2]]
Odpowiedź: Tak""",
            ),
            ("user", "Tekst: {response}\nOdpowiedź:"),
        ]
    )

    prompt = template.invoke(
        {
            "response": response,
        }
    )

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
            "format_checker_messages": [*prompt.messages, result], # type:ignore
            "has_correct_format": has_correct_format,
        },
        goto=goto,
    )
