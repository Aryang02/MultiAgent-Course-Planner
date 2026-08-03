from unittest.mock import patch

from src.llm import embeddings


def test_get_embeddings_gemini():
    with patch.object(embeddings.settings, "EMBEDDING_MODEL", "gemini/gemini-embedding-001"):
        with patch("src.llm.embeddings.GoogleGenerativeAIEmbeddings") as mock_cls:
            embeddings.get_embeddings()
            mock_cls.assert_called_once()
            assert mock_cls.call_args.kwargs["model"] == "gemini-embedding-001"


def test_get_embeddings_openai():
    with patch.object(
        embeddings.settings,
        "EMBEDDING_MODEL",
        "openai/text-embedding-3-small",
    ):
        with patch("src.llm.embeddings.OpenAIEmbeddings") as mock_cls:
            embeddings.get_embeddings()
            mock_cls.assert_called_once_with(model="text-embedding-3-small")
