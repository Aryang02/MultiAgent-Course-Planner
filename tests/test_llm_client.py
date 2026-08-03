from unittest.mock import MagicMock, patch

import pytest

from src.agents import llm_client


def test_generate_uses_default_model():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="hello"))]
    mock_response.usage = MagicMock(prompt_tokens=5, completion_tokens=7)

    with patch.object(llm_client.settings, "LLM_MODEL", "gemini/gemini-1.5-pro"):
        with patch("src.agents.llm_client.litellm.completion", return_value=mock_response) as mock_completion:
            with patch.object(llm_client, "record_llm_tokens") as mock_record:
                result = llm_client.generate("system", "prompt")

    assert result == "hello"
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "gemini/gemini-1.5-pro"
    mock_record.assert_called_once_with("gemini/gemini-1.5-pro", 5, 7)


def test_generate_uses_custom_model():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="response"))]
    mock_response.usage = None

    with patch("src.agents.llm_client.litellm.completion", return_value=mock_response) as mock_completion:
        result = llm_client.generate("system", "prompt", model="gpt-4o")

    assert result == "response"
    assert mock_completion.call_args.kwargs["model"] == "gpt-4o"


def test_generate_raises_on_empty_response():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]
    mock_response.usage = None

    with patch("src.agents.llm_client.litellm.completion", return_value=mock_response):
        with pytest.raises(RuntimeError, match="Empty response"):
            llm_client.generate("system", "prompt")
