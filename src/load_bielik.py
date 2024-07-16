from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer
import torch
from typing import Tuple, cast

model_name = "speakleash/Bielik-7B-Instruct-v0.1"


def load_bielik() -> Tuple[PreTrainedTokenizer, AutoModelForCausalLM]:
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, cache_dir="models/bielik_tokenizer"
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name, cache_dir="models/bielik_model", torch_dtype=torch.bfloat16
    )
    return cast(PreTrainedTokenizer, tokenizer), model
