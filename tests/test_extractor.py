import responses
from src.extractor import extract_og_image, extract_source_domain


@responses.activate
def test_extract_og_image_returns_url():
    html = """<html><head>
        <meta property="og:image" content="https://example.com/img.jpg">
    </head><body></body></html>"""
    responses.add(responses.GET, "https://example.com/article", body=html, status=200)
    assert extract_og_image("https://example.com/article") == "https://example.com/img.jpg"


@responses.activate
def test_extract_og_image_returns_none_when_missing():
    html = "<html><head></head><body>No image here</body></html>"
    responses.add(responses.GET, "https://example.com/article", body=html, status=200)
    assert extract_og_image("https://example.com/article") is None


@responses.activate
def test_extract_og_image_returns_none_on_error():
    responses.add(responses.GET, "https://example.com/broken", status=404)
    assert extract_og_image("https://example.com/broken") is None


def test_extract_source_domain_strips_www():
    assert extract_source_domain("https://www.theverge.com/article") == "The Verge"


def test_extract_source_domain_plain():
    assert extract_source_domain("https://wired.com/story/ai") == "Wired"
