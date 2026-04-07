from unittest.mock import MagicMock, patch
from src.translator import generate_translation


def make_mock_client(response_text):
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_generate_translation_returns_string():
    mock_client = make_mock_client("Esta es la explicación sencilla del artículo.")
    with patch("src.translator.anthropic.Anthropic", return_value=mock_client):
        result = generate_translation(
            api_key="fake-key",
            title="GPT-5 llega con razonamiento extendido",
            source="The Verge",
            excerpt="OpenAI presenta su modelo más capaz."
        )
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_translation_calls_api_with_correct_model():
    mock_client = make_mock_client("Explicación.")
    with patch("src.translator.anthropic.Anthropic", return_value=mock_client):
        generate_translation(
            api_key="fake-key",
            title="Test title",
            source="Test source",
            excerpt="Test excerpt"
        )
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
    assert call_kwargs["max_tokens"] == 300


def test_generate_translation_includes_context_in_prompt():
    mock_client = make_mock_client("Explicación.")
    with patch("src.translator.anthropic.Anthropic", return_value=mock_client):
        generate_translation(
            api_key="fake-key",
            title="Mi título",
            source="Mi fuente",
            excerpt="Mi excerpt"
        )
    prompt = mock_client.messages.create.call_args[1]["messages"][0]["content"]
    assert "Mi título" in prompt
    assert "Mi fuente" in prompt
    assert "Mi excerpt" in prompt
