from typing import TypedDict

from langchain_core.runnables.config import RunnableConfig
from langchain_huggingface import ChatHuggingFace


class ConfigSchema(TypedDict):
    base_llm: ChatHuggingFace
    base_llm_zero_temp: ChatHuggingFace
    sample: str
    relations_description: str
    fewshot_examples: str


class PolishKGRunnableConfig(RunnableConfig):
    configurable: ConfigSchema
