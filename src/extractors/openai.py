from openai import OpenAI
from openai.types import Batch
from dotenv import load_dotenv
import os
import json

load_dotenv()


class OpenAIExtractor:
    def __init__(self, model_name: str, batch_input_file_location: str):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.batch_input_file_location = batch_input_file_location
        self.requests = []

        self.batch_input_file = None

    def add_request_to_batch(self, system_content: str, prompt_content: str):
        template = self.__create_messages_template(system_content, prompt_content)
        custom_id = f"request-{len(self.requests)}"
        request = self.__create_single_request(custom_id, template)
        self.requests.append(request)

    def run_batch(self, run_description: str) -> Batch:
        with open(self.batch_input_file_location, "w") as file:
            for request in self.requests:
                file.write(f"{json.dumps(request, ensure_ascii=False)}\n")

        with open(self.batch_input_file_location, "rb") as file:
            self.batch_input_file = self.client.files.create(
                file=file,
                purpose="batch"
            )
        
        return self.client.batches.create(
            input_file_id=self.batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": run_description
            }
        )

    def get_batch(self, batch_id: str) -> Batch:
        return self.client.batches.retrieve(batch_id)

    def __create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def __create_single_request(self, custom_id: str, messages_template: list):
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model_name,
                "messages": messages_template,
            },
        }
