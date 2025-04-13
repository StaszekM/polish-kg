from langchain_core.messages import AIMessage

from polish_kg_langchain import State


def extract_triple_bielik(state: State) -> State:
    return {"messages": [AIMessage(content="Odpowiedź z Bielika")]}  # type:ignore
