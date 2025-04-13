from langgraph.graph import END, START, StateGraph

from polish_kg_langchain import ConfigSchema, State
from polish_kg_langchain.nodes import (
    create_node_correct_triple,
    create_node_extract_triple,
    create_node_validate_did_format_correctly,
    create_node_validate_did_refuse_to_answer,
    extract_triple_bielik,
    noop,
)


class PolishKGLangchainGraph:
    def __init__(self, with_syntax_validation: bool = True) -> None:
        graph_builder = StateGraph(State, ConfigSchema)
        graph_builder.add_node(
            "extract_triple",
            create_node_extract_triple(
                prompt_location="data/polish_kg_langchain/prompt_extract_triple.txt"
            ),
        )
        graph_builder.add_edge(START, "extract_triple")
        graph_builder.add_edge("extract_triple", "validate_did_refuse_to_answer")

        graph_builder.add_node(
            "validate_did_refuse_to_answer",
            create_node_validate_did_refuse_to_answer(
                prompt_location="data/polish_kg_langchain/prompt_validate_did_refuse_to_answer.txt"
            ),
        )
        graph_builder.add_node(
            "validate_did_format_correctly",
            (
                create_node_validate_did_format_correctly(
                    prompt_location="data/polish_kg_langchain/prompt_validate_did_format_correctly.txt"
                )
                if with_syntax_validation
                else noop
            ),
        )
        graph_builder.add_node(
            "correct_triple",
            create_node_correct_triple(
                prompt_location="data/polish_kg_langchain/prompt_correct_triple.txt"
            ),
        )
        graph_builder.add_node("extract_triple_bielik", extract_triple_bielik)

        graph_builder.add_edge("correct_triple", END)
        graph_builder.add_edge("extract_triple_bielik", END)

        self.graph = graph_builder.compile()
