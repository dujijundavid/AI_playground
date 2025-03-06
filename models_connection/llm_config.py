from llm_client import LLMClientFactory

LLM_PROFILES = {
    "default": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    },
    "deepseek": {
        "provider": "deepseek",
        "model": "deepseek-chat"
    },
    "azure_gpt4": {
        "provider": "azure",
        "model": "gpt-4o",
        "api_version": "2024-06-01"
    }
}

def get_llm_client(profile_name="default"):
    profile = LLM_PROFILES.get(profile_name, LLM_PROFILES["default"])
    return LLMClientFactory.create_client(**profile)