from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from src.settings import settings


def _gemini_model_name() -> str:
    model = settings.EMBEDDING_MODEL
    if model.startswith("gemini/"):
        return model.split("/", 1)[1]
    return model


def get_embeddings() -> Embeddings:
    model = settings.EMBEDDING_MODEL
    if model.startswith("openai/") or model.startswith("text-embedding"):
        openai_model = model.split("/", 1)[1] if "/" in model else model
        return OpenAIEmbeddings(model=openai_model)
    return GoogleGenerativeAIEmbeddings(
        google_api_key=SecretStr(settings.GOOGLE_API_KEY) if settings.GOOGLE_API_KEY else None,
        model=_gemini_model_name(),
    )
