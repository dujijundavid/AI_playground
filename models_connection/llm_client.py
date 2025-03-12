from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, Dict, Any, Generator

# Load environment variables once
load_dotenv()

class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""
    
    @abstractmethod
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.client = None  # To be initialized in subclasses
        self.default_params = {
            'temperature': 0.7,
            'max_tokens': 2048,
            **kwargs
        }
    
    @abstractmethod
    def create_chat_completion(
        self,
        messages: list,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Abstract method for creating chat completions"""
        pass

    def _merge_params(self, **kwargs) -> Dict:
        """Helper to merge default and request-specific parameters"""
        return {**self.default_params, **kwargs}

class OpenAIClient(BaseLLMClient):
    """Client for standard OpenAI API endpoints"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or "https://api.openai.com/v1"
        )

    def create_chat_completion(self, messages: list, stream: bool = False, **kwargs):
        params = self._merge_params(**kwargs)
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            **params
        )

class DeepSeekClient(OpenAIClient):
    """Client for DeepSeek specialized API"""
    
    def __init__(self, model: str = "deepseek-chat", **kwargs):
        super().__init__(
            model=model,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            **kwargs
        )

from openai import AzureOpenAI  # 导入正确的Azure客户端类

class AzureClient(BaseLLMClient):
    """Client for Azure OpenAI deployments"""
    
    def __init__(self, model: str, api_version: str, **kwargs):
        super().__init__(model, **kwargs)
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            api_version=api_version,
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        )
        self.azure_deployment = model  # 存储部署名称
    
    def create_chat_completion(self, messages: list, stream: bool = False, **kwargs):
        params = self._merge_params(**kwargs)
        return self.client.chat.completions.create(
            model=self.azure_deployment,  # 使用存储的部署名称
            messages=messages,
            stream=stream,
            **params
        )

class VolcanoClient(BaseLLMClient):
    """Client for Volcano Engine's API"""
    
    def __init__(self, model: str="deepseek-r1-250120", **kwargs):
        super().__init__(model, **kwargs)
        self.client = OpenAI(
            api_key=os.getenv("ARK_API_KEY"),
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )

    def create_chat_completion(self, messages: list, stream: bool = False, **kwargs):
        params = self._merge_params(**kwargs)
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            **params
        )

class LLMClientFactory:
    """Factory class for creating appropriate LLM clients"""
    
    @staticmethod
    def create_client(provider: str, **kwargs) -> BaseLLMClient:
        providers = {
            'openai': OpenAIClient,
            'deepseek': DeepSeekClient,
            'azure': AzureClient,
            'volcano': VolcanoClient
        }
        
        if provider not in providers:
            raise ValueError(f"Unsupported provider: {provider}")
            
        return providers[provider](**kwargs)

# Usage examples
if __name__ == "__main__":
    # Example 1: Using DeepSeek
    deepseek = LLMClientFactory.create_client(
        provider="deepseek",
        model="deepseek-chat"
    )
    
    # Example 2: Using Azure
    azure_client = LLMClientFactory.create_client(
        provider="azure",
        model="gpt-4o",
        api_version="2024-06-01"
    )
    
    # Example 3: Standard OpenAI
    openai_client = LLMClientFactory.create_client(
        provider="openai",
        model="gpt-4o-mini"
    )
   
    volcano_client = LLMClientFactory.create_client(
        provider="volcano",
        model = "deepseek-r1-250120"
    )
        
    # Universal usage pattern
    def query_llm(client: BaseLLMClient, prompt: str):
        response = client.create_chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    # Streaming example
    def stream_response(client: BaseLLMClient, prompt: str) -> Generator:
        stream = client.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices:
                yield chunk.choices[0].delta.content or ""
                

    prompt = "告诉我你是那个模型"
    # print("deepseek:" , query_llm(deepseek,prompt))
    # print("MB azure:" , query_llm(azure_client,prompt))
    # print("Openai:" , query_llm(openai_client,prompt))
    print("volcano:" , query_llm(volcano_client,prompt))