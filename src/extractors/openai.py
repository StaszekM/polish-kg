import json
import os
from typing import List, TypedDict

from dotenv import load_dotenv
from openai import OpenAI
from openai.types import Batch, FileObject

load_dotenv()

def add_suffix_to_filename(filepath:str, suffix:str) -> str:
    base, ext = os.path.splitext(filepath)
    return f"{base}{suffix}{ext}"

class Request(TypedDict):
    custom_id: str
    method: str
    url: str
    body: dict

class MessagesTemplate(TypedDict):
    role: str
    content: str

class OpenAIExtractor:
    def __init__(self, model_name: str, batch_input_file_location: str, batch_size: int = 600):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.batch_input_file_location = batch_input_file_location
        self.batch_size = batch_size
        self.requests: List[Request] = []
        self.batches: List[Batch] = []
        self.batch_files_locations: List[str] = []

        self.batch_input_files: List[FileObject] = []

    def add_request_to_batch(self, system_content: str, prompt_content: str):
        template = self.__create_messages_template(system_content, prompt_content)
        custom_id = f"request-{len(self.requests)}"
        request = self.__create_single_request(custom_id, template)
        self.requests.append(request)

    def run_batch(self, run_description: str) -> None:
        chunk_requests = self.__chunk_requests()

        for idx, chunk in enumerate(chunk_requests):
            filename_suffix = f"-chunk-{idx}"
            file_location = add_suffix_to_filename(self.batch_input_file_location, filename_suffix)
            with open(file_location, "w") as file:
                for request in chunk:
                    file.write(f"{json.dumps(request, ensure_ascii=False)}\n")

            with open(file_location, "rb") as file:
                client_file = self.client.files.create(
                    file=file,
                    purpose="batch"
                )

                self.batch_input_files.append(client_file)

                batch = self.client.batches.create(
                    input_file_id=client_file.id,
                    endpoint="/v1/chat/completions",
                    completion_window="24h",
                    metadata={
                        "description": run_description
                    }
                )

                self.batches.append(batch)
                self.batch_files_locations.append(file_location)

    def get_batches(self) -> List[Batch]:
        batch_responses: List[Batch] = []
        for batch in self.batches:
            batch_responses.append(self.client.batches.retrieve(batch.id))
        
        return batch_responses
    
    def remove_batch_files(self) -> None:
        for file_location in self.batch_files_locations:
            os.remove(file_location)

    def __create_messages_template(
        self, system_content: str, prompt_content: str
    ) -> List[MessagesTemplate]:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": prompt_content},
        ]

    def __create_single_request(self, custom_id: str, messages_template: List[MessagesTemplate]) -> Request:
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model_name,
                "messages": messages_template,
            },
        }
    
    def __chunk_requests(self) -> List[List[Request]]:
        """
        Chunk the requests into batches of size self.batch_size.

        Returns:
            list: A list of batches, where each batch contains self.batch_size number of requests.
        """
        return [self.requests[i:i + self.batch_size] for i in range(0, len(self.requests), self.batch_size)]

