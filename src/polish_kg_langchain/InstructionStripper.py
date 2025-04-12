from typing import Any, Union
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class InstructionStripper(BaseCallbackHandler):
    """Callback handler to strip passed instructions from the output of the LLM."""
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Union[UUID, None] = None,
        **kwargs: Any
    ) -> Any:
        for generation_list in response.generations:
            for generation in generation_list:
                if generation.message.content.__contains__("[/INST]"):  # type: ignore
                    generation.message.content = generation.message.content.split(  # type: ignore
                        "[/INST]"
                    )[
                        -1
                    ].strip()  # type: ignore

        return super().on_llm_end(
            response, run_id=run_id, parent_run_id=parent_run_id, **kwargs
        )