from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list['BaseMessage'], add_messages]

    attempt_checker_messages: Annotated[list['BaseMessage'], add_messages]
    did_attempt_to_answer: bool

    format_checker_messages: Annotated[list['BaseMessage'], add_messages]
    has_correct_format: bool
