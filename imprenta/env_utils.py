import os
from typing import Optional

_PLACEHOLDER_VALUES = {
    "",
    "test",
    "changeme",
    "your_api_key_here",
    "your-openai-api-key",
    "your_api_key",
    "api_key",
    "placeholder",
    "token",
    "your_token_here",
    "<your-api-key>",
    "sk-test",
    "ghp_example",
}


def _looks_like_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return True

    if normalized in _PLACEHOLDER_VALUES:
        return True

    return any(token in normalized for token in ["your", "example", "placeholder", "changeme", "test"])


def get_openai_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GITHUB_TOKEN")
    if not api_key:
        raise EnvironmentError(
            "Falta la variable de entorno OPENAI_API_KEY o GITHUB_TOKEN."
        )
    if _looks_like_placeholder(api_key):
        raise EnvironmentError(
            "La clave configurada parece un valor de ejemplo o placeholder. Define una clave real de OpenAI o un token válido en tu archivo .env o en la sesión de terminal."
        )
    return api_key


def get_openai_api_base() -> Optional[str]:
    return os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
