# Following along here:
# https://python.langchain.com/docs/modules/model_io/models/llms/how_to/custom_llm

from typing import Any, List, Mapping, Optional
import json

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

from schemallm.models.jsonschema import JsonSchema, parse_json_schema
from schemallm.client.http_api_client import JsonLlmClient, DEFAULT_BASE_URL


class BaseJsonLlmLLM(LLM):
    base_url: str = DEFAULT_BASE_URL
    api_client: JsonLlmClient = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.api_client = JsonLlmClient(base_url=self.base_url)


class JsonSchemaLLM(BaseJsonLlmLLM):
    # TODO(j.swannack): could use a validator here to cast the dict to a JsonSchema
    schema_restriction: JsonSchema | dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.schema_restriction, dict):
            self.schema_restriction = parse_json_schema(self.schema_restriction)

    @property
    def _llm_type(self) -> str:
        return "jsonllm_json_schema"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "schema_restriction": self.schema_restriction.dict(),
            "base_url": self.base_url,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        result_obj = self.api_client.completion_with_schema(
            prompt=prompt,
            schema=self.schema_restriction.dict(),
            stop=stop,
        )
        return json.dumps(result_obj.completion)


class CfgLLM(BaseJsonLlmLLM):
    cfg: str

    @property
    def _llm_type(self) -> str:
        return "jsonllm_cfg"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "cfg": self.cfg,
            "base_url": self.base_url,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return self.api_client.completion_with_cfg(
            prompt=prompt,
            cfg=self.cfg,
            stop=stop,
        ).completion


class ReLLM(BaseJsonLlmLLM):
    pattern: str

    @property
    def _llm_type(self) -> str:
        return "jsonllm_re"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "pattern": self.pattern,
            "base_url": self.base_url,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return self.api_client.completion_with_regex(
            prompt=prompt,
            pattern=self.pattern,
            stop=stop,
        ).completion


class StandardLLM(BaseJsonLlmLLM):
    @property
    def _llm_type(self) -> str:
        return "jsonllm_standard"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "base_url": self.base_url,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return self.api_client.completion_standard(
            prompt=prompt,
            stop=stop,
        ).completion
