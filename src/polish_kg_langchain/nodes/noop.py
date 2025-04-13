from typing import Literal

from langgraph.types import Command

from polish_kg_langchain import State


def noop(state: State) -> Command[Literal["correct_triple"]]:
    return Command(goto="correct_triple")
