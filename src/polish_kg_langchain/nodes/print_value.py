from polish_kg_langchain.State import State


def print_value(state: State) -> State:
    response = state["messages"][-1].content 
    print(response)
    return state
