# type: ignore
import os
from abc import ABC, abstractmethod

import torch
from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel

load_dotenv()

class Extractor(ABC):
    def __init__(self, device=str):
        super().__init__()

    @abstractmethod
    def get_memory_footprint(self) -> int:
        pass

    @abstractmethod
    def create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        pass

    @abstractmethod
    def get_response_text(self, messages_template: list) -> str:
        pass


class BielikExtractor(Extractor):
    def __init__(self, device: str):
        super().__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(
            "speakleash/Bielik-11B-v2.2-Instruct"
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "speakleash/Bielik-11B-v2.2-Instruct", torch_dtype=torch.float16
        )
        self.model.to(device)
        self.device = device

    def get_memory_footprint(self) -> int:
        footprint_in_bytes = self.model.get_memory_footprint()
        footprint_in_gigabytes = footprint_in_bytes / 1024**3
        return footprint_in_gigabytes

    def create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def get_response_text(self, messages_template: list):
        input_ids = self.tokenizer.apply_chat_template(
            messages_template, return_tensors="pt", add_generation_prompt=True
        )

        response = self.__generate_response(input_ids)
        response = self.__extract_model_response(response)
        return response

    def __generate_response(self, input_ids: torch.Tensor) -> str:
        with torch.no_grad():
            input_ids = input_ids.to(self.device)
            generated_ids = self.model.generate(
                input_ids, max_new_tokens=1000, do_sample=True
            )
            decoded = self.tokenizer.batch_decode(generated_ids)
            return decoded[0]

    def __extract_model_response(self, decoded: str) -> str:
        beginning = "<|im_start|> assistant"
        end = "<|im_end|>"
        return decoded.split(beginning)[-1].split(end)[0].strip()

class PllumExtractor(Extractor):
    def __init__(self, device: str):
        super().__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(
            "CYFRAGOVPL/Llama-PLLuM-8B-instruct"
        )
        self.model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            "CYFRAGOVPL/Llama-PLLuM-8B-instruct", torch_dtype=torch.float16
        )
        self.model.to(device)
        self.device = device

    def get_memory_footprint(self) -> int:
        footprint_in_bytes = self.model.get_memory_footprint()
        footprint_in_gigabytes = footprint_in_bytes / 1024**3
        return footprint_in_gigabytes

    def create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def get_response_text(self, messages_template: list):
        input_dict = self.tokenizer.apply_chat_template(
            messages_template, add_generation_prompt=True, return_dict=True, return_tensors="pt"
        )

        response = self.__generate_response(input_dict)
        response = self.__extract_model_response(response)
        return response

    def __generate_response(self, input_dict: dict) -> str:
        with torch.no_grad():
            input_ids = input_dict['input_ids'].to(self.device)
            attn_mask = input_dict['attention_mask'].to(self.device)
            generated_ids = self.model.generate(
                input_ids, max_new_tokens=1000, do_sample=True, attention_mask=attn_mask, pad_token_id=self.tokenizer.pad_token_id
            )
            decoded = self.tokenizer.batch_decode(generated_ids)
            return decoded[0]

    def __extract_model_response(self, decoded: str) -> str:
        beginning = "[/INST]"
        end = "<|end_of_text|>"
        return decoded.split(beginning)[-1].split(end)[0].strip()

class OpenAISequentialExtractor(Extractor):
    def __init__(self, device):
        super().__init__()

        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def get_memory_footprint(self) -> int:
        return 0

    def create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def get_response_text(self, messages_template: list) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_template
        )

        return completion.choices[0].message.content or ''


class DummyExtractor(Extractor):
    def __init__(self, device: str):
        super().__init__()

    def get_memory_footprint(self) -> int:
        return 42

    def create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def get_response_text(self, messages_template: list):
        return "[[Subj, Relation, Obj]]"
