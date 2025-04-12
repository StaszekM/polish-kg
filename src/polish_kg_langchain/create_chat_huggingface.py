from typing import Union

from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import (PreTrainedModel, PreTrainedTokenizer,
                          PreTrainedTokenizerFast, pipeline)

from polish_kg_langchain.InstructionStripper import InstructionStripper


def create_chat_huggingface(llm: PreTrainedModel, tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast], **kwargs) -> ChatHuggingFace:
    
    args = {
        "model": llm,
        "tokenizer": tokenizer,
        "device": "cuda",
        "max_new_tokens": 1000,
        "do_sample": True,
        "temperature": 0.8,
    }
    args.update(kwargs)
    
    pipe = pipeline(
        "text-generation",
        **args,
    )

    langchain_pipe = HuggingFacePipeline(
        pipeline=pipe,
    )
    chat = ChatHuggingFace(llm=langchain_pipe, callbacks=[InstructionStripper()])

    return chat
