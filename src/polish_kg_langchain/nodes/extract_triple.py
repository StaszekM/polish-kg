from git import Optional

from polish_kg_langchain import PolishKGRunnableConfig, State


def extract_triple(state: State, config: Optional[PolishKGRunnableConfig] = None) -> State:
    if config is None:
        raise ValueError("Config must be provided")
    chat = config['configurable'].get('base_llm')
    result = chat.invoke(state["messages"])
    return {"messages": [result]}  # type: ignore
