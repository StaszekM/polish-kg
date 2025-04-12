from langgraph.graph import END, START, StateGraph

from polish_kg_langchain import ConfigSchema, State
from polish_kg_langchain.nodes import (extract_triple,
                                       validate_did_format_correctly,
                                       validate_did_refuse_to_answer)


def to_evaluation(state: State) -> None:
    print("To evaluation: ", state)
    return None


def correct_triple(state: State) -> None:
    print("Correct triple: ", state)
    return None


def extract_triple_bielik(state: State) -> None:
    print("Extract triple bielik: ", state)
    return None


class PolishKGLangchainGraph():
    def __init__(self) -> None:
        graph_builder = StateGraph(State, ConfigSchema)
        graph_builder.add_node("extract_triple", extract_triple)
        graph_builder.add_edge(START, "extract_triple")
        graph_builder.add_edge("extract_triple", "validate_did_refuse_to_answer")

        graph_builder.add_node("validate_did_refuse_to_answer", validate_did_refuse_to_answer)
        graph_builder.add_node("validate_did_format_correctly", validate_did_format_correctly)
        graph_builder.add_node("to_evaluation", to_evaluation)
        graph_builder.add_node("correct_triple", correct_triple)
        graph_builder.add_node("extract_triple_bielik", extract_triple_bielik)

        graph_builder.add_edge("correct_triple", END)
        graph_builder.add_edge("extract_triple_bielik", END)
        graph_builder.add_edge("to_evaluation", END)

        self.graph = graph_builder.compile()


    
