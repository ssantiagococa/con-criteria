# Con CriterIA — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a weekly AI newsletter generator that reads articles from Instapaper, generates HTML with Claude-powered explanations, and publishes to GitHub Pages.

**Architecture:** A Python CLI script reads bookmarks from 4 Instapaper folders, scrapes og:image from each URL, calls the Claude API to generate plain-language "traducción a humano" blocks, and renders everything into a self-contained HTML file via Jinja2. A separate index.html lists all past editions.

**Tech Stack:** Python 3.11+, requests, requests-oauthlib, beautifulsoup4, anthropic SDK, jinja2, pytest, GitHub Pages

---

## File Structure

```
con-criteria/
├── editions/
│   └── .gitkeep
├── templates/
│   ├── newsletter.html.j2      # Full newsletter HTML template
│   └── index.html.j2           # Index page template
├── src/
│   ├── instapaper.py           # Instapaper API client (auth + fetch bookmarks)
│   ├── extractor.py            # og:image scraper
│   ├── translator.py           # Claude API "traducción a humano" generator
│   └── renderer.py             # Jinja2 rendering + file output
├── tests/
│   ├── test_instapaper.py
│   ├── test_extractor.py
│   ├── test_translator.py
│   └── test_renderer.py
├── generate.py                 # Entry point — orchestrates everything
├── config.example.py           # Template for credentials (committed)
├── config.py                   # Actual credentials (in .gitignore)
├── requirements.txt
├── index.html                  # Generated index (committed each week)
└── .gitignore
```

---

## Pre-requisites (do before starting)

- **Instapaper API key:** Request a consumer key/secret at https://www.instapaper.com/api — approval takes 1-2 days. While waiting, tasks 1-5 can be completed.
- **Claude API key:** Get from https://console.anthropic.com
- **Python 3.11+** installed
- **GitHub account** with a new empty repo named `con-criteria`

---

## Task 1: Project setup

**Files:**
- Create: `requirements.txt`
- Create: `config.example.py`
- Create: `config.py` (from example, filled with real keys — NOT committed)
- Create: `.gitignore`
- Create: `editions/.gitkeep`
- Create: `templates/` (empty dir)
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create the project directory structure**

```bash
cd /Users/sarah/newsletter_interna_IA
mkdir -p editions templates src tests
touch src/__init__.py tests/__init__.py editions/.gitkeep
```

- [ ] **Step 2: Create `requirements.txt`**

```
requests==2.31.0
requests-oauthlib==1.3.1
beautifulsoup4==4.12.3
anthropic==0.25.0
jinja2==3.1.3
python-dateutil==2.9.0
pytest==8.1.1
pytest-mock==3.14.0
responses==0.25.0
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages installed without errors.

- [ ] **Step 4: Create `config.example.py`**

```python
# Copy this file to config.py and fill in your credentials
# Never commit config.py

# Instapaper API (request at https://www.instapaper.com/api)
INSTAPAPER_CONSUMER_KEY = "your_consumer_key"
INSTAPAPER_CONSUMER_SECRET = "your_consumer_secret"
INSTAPAPER_USERNAME = "your_instapaper_email"
INSTAPAPER_PASSWORD = "your_instapaper_password"

# Claude API (https://console.anthropic.com)
CLAUDE_API_KEY = "sk-ant-..."

# Newsletter settings
ARCHIVE_AFTER_GENERATE = True  # Set to False to keep bookmarks in folders after generating
```

- [ ] **Step 5: Create `config.py`** (fill in real credentials)

```bash
cp config.example.py config.py
# Now open config.py and fill in your real keys
```

- [ ] **Step 6: Create `.gitignore`**

```
config.py
__pycache__/
*.pyc
.pytest_cache/
.superpowers/
*.egg-info/
dist/
.DS_Store
```

- [ ] **Step 7: Initialize git and make first commit**

```bash
git init
git add requirements.txt config.example.py .gitignore editions/.gitkeep src/__init__.py tests/__init__.py
git commit -m "feat: project setup"
```

---

## Task 2: Instapaper API client

**Files:**
- Create: `src/instapaper.py`
- Create: `tests/test_instapaper.py`

The Instapaper API uses xAuth (OAuth 1.0a simplified). We authenticate once with username/password to get an access token, then use that token for all requests.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_instapaper.py
import pytest
import responses
from src.instapaper import InstapaperClient


@responses.activate
def test_authenticate_returns_token():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    client = InstapaperClient(
        consumer_key="key", consumer_secret="secret",
        username="user@example.com", password="pass"
    )
    assert client.token == "mytoken"
    assert client.token_secret == "mytokensecret"


@responses.activate
def test_get_folder_id_returns_correct_id():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/folders/list",
        json=[
            {"folder_id": 1234, "title": "hot-topic"},
            {"folder_id": 5678, "title": "aprende"},
        ],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    assert client.get_folder_id("hot-topic") == 1234
    assert client.get_folder_id("aprende") == 5678


@responses.activate
def test_get_bookmarks_returns_list():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/list",
        json=[
            {"type": "bookmark", "bookmark_id": 1, "title": "Article 1",
             "url": "https://example.com/1", "description": "Excerpt 1"},
            {"type": "user"},  # API includes a user object — should be filtered out
        ],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    bookmarks = client.get_bookmarks(folder_id=1234, limit=3)
    assert len(bookmarks) == 1
    assert bookmarks[0]["title"] == "Article 1"


@responses.activate
def test_archive_bookmark():
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=mytoken&oauth_token_secret=mytokensecret",
        status=200,
    )
    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/archive",
        json=[{"type": "bookmark", "bookmark_id": 42}],
        status=200,
    )
    client = InstapaperClient("key", "secret", "user@example.com", "pass")
    client.archive_bookmark(42)  # Should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_instapaper.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `InstapaperClient` doesn't exist yet.

- [ ] **Step 3: Implement `src/instapaper.py`**

```python
from urllib.parse import parse_qs
import requests
from requests_oauthlib import OAuth1


class InstapaperClient:
    BASE_URL = "https://www.instapaper.com/api/1"

    def __init__(self, consumer_key, consumer_secret, username, password):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token, self.token_secret = self._authenticate(username, password)

    def _authenticate(self, username, password):
        auth = OAuth1(self.consumer_key, self.consumer_secret)
        response = requests.post(
            f"{self.BASE_URL}/oauth/access_token",
            auth=auth,
            data={
                "x_auth_username": username,
                "x_auth_password": password,
                "x_auth_mode": "client_auth",
            },
        )
        response.raise_for_status()
        params = parse_qs(response.text)
        return params["oauth_token"][0], params["oauth_token_secret"][0]

    def _auth(self):
        return OAuth1(
            self.consumer_key, self.consumer_secret,
            self.token, self.token_secret
        )

    def get_folder_id(self, folder_name):
        response = requests.post(
            f"{self.BASE_URL}/folders/list", auth=self._auth()
        )
        response.raise_for_status()
        for folder in response.json():
            if folder.get("title") == folder_name:
                return folder["folder_id"]
        raise ValueError(f"Folder '{folder_name}' not found in Instapaper")

    def get_bookmarks(self, folder_id, limit=10):
        response = requests.post(
            f"{self.BASE_URL}/bookmarks/list",
            auth=self._auth(),
            data={"folder_id": folder_id, "limit": limit},
        )
        response.raise_for_status()
        return [b for b in response.json() if b.get("type") == "bookmark"]

    def archive_bookmark(self, bookmark_id):
        response = requests.post(
            f"{self.BASE_URL}/bookmarks/archive",
            auth=self._auth(),
            data={"bookmark_id": bookmark_id},
        )
        response.raise_for_status()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_instapaper.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/instapaper.py tests/test_instapaper.py
git commit -m "feat: instapaper API client with xAuth"
```

---

## Task 3: og:image extractor

**Files:**
- Create: `src/extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_extractor.py
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
    assert extract_source_domain("https://wired.com/story/ai") == "wired.com"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_extractor.py -v
```

Expected: `ImportError` — module doesn't exist yet.

- [ ] **Step 3: Implement `src/extractor.py`**

```python
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Known domains → readable names
KNOWN_DOMAINS = {
    "theverge.com": "The Verge",
    "wired.com": "Wired",
    "technologyreview.com": "MIT Technology Review",
    "nytimes.com": "The New York Times",
    "bloomberg.com": "Bloomberg",
    "techcrunch.com": "TechCrunch",
    "venturebeat.com": "VentureBeat",
    "towardsdatascience.com": "Towards Data Science",
    "medium.com": "Medium",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "linkedin.com": "LinkedIn",
    "noema.com": "Noema Magazine",
    "noemamag.com": "Noema Magazine",
    "xataka.com": "Xataka",
    "elespanol.com": "El Español",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ConCriterIA/1.0)"}


def extract_og_image(url):
    """Fetch URL and return og:image content, or None if not found."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
        return None
    except Exception:
        return None


def extract_source_domain(url):
    """Return a readable source name from a URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.removeprefix("www.")
    return KNOWN_DOMAINS.get(domain, domain)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_extractor.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/extractor.py tests/test_extractor.py
git commit -m "feat: og:image extractor and domain parser"
```

---

## Task 4: Claude API "traducción a humano" generator

**Files:**
- Create: `src/translator.py`
- Create: `tests/test_translator.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_translator.py
import pytest
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_translator.py -v
```

Expected: `ImportError` — module doesn't exist yet.

- [ ] **Step 3: Implement `src/translator.py`**

```python
import anthropic

SYSTEM_PROMPT = """Eres el asistente editorial de la newsletter "Con CriterIA", 
interna del equipo de Soulsight, una consultora independiente de estrategia 
para directivos y grandes empresas con enfoque humanista a la hora de abordar 
los grandes desafíos de las organizaciones.

Tu misión es escribir la sección "traducción a humano" de cada artículo: 
3-4 líneas que expliquen el contenido de forma clara y cercana para personas 
sin conocimientos técnicos. Usa metáforas cotidianas, ejemplos concretos y, 
cuando sea relevante, menciona qué implicación práctica puede tener para un 
equipo como el de Soulsight. Tono directo, sin jerga, con personalidad."""

USER_TEMPLATE = """Artículo: {title}
Fuente: {source}
Descripción: {excerpt}

Escribe la "traducción a humano" en 3-4 líneas. Solo el texto, sin títulos ni etiquetas."""


def generate_translation(api_key, title, source, excerpt):
    """Call Claude API and return a plain-language explanation of the article."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_TEMPLATE.format(
                    title=title, source=source, excerpt=excerpt or ""
                ),
            }
        ],
    )
    return message.content[0].text.strip()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_translator.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/translator.py tests/test_translator.py
git commit -m "feat: claude API translator for 'traducción a humano'"
```

---

## Task 5: Jinja2 newsletter HTML template

**Files:**
- Create: `templates/newsletter.html.j2`

This is the full HTML template based on the approved mockup. No tests needed — visual output is verified by opening the file.

- [ ] **Step 1: Create `templates/newsletter.html.j2`**

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Con CriterIA · Edición #{{ edition_num }}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Lora:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #d4cfc4; font-family: 'Lora', Georgia, serif; padding: 40px 20px; }
.newsletter { max-width: 620px; margin: 0 auto; background: #e8e4d9; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 32px rgba(24,16,8,0.15); }

/* HEADER */
.header { background: #181008; padding: 36px 40px 28px; border-bottom: 3px solid #ff6f4d; }
.header-meta { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #86897c; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; }
.header-title { font-family: 'DM Sans', sans-serif; font-size: 36px; font-weight: 600; color: #e8e4d9; letter-spacing: -0.5px; margin-bottom: 8px; }
.header-title span { color: #ff6f4d; }
.header-tagline { font-family: 'Lora', serif; font-style: italic; font-size: 14px; color: #abb4ba; line-height: 1.5; }

/* INTRO */
.intro { padding: 24px 40px; border-bottom: 1px solid #d4cfc4; }
.intro p { font-size: 15px; color: #4c2f12; line-height: 1.7; }

/* SECTIONS */
.section { padding: 28px 40px; border-bottom: 1px solid #d4cfc4; }
.section-label-text { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; border-radius: 2px; margin-bottom: 10px; }
.label-pepper { background: #ff6f4d; color: #fff; }
.label-needy { background: #ffb655; color: #181008; }
.label-deepy { background: #59583c; color: #e8e4d9; }
.label-goofy { background: #ffc294; color: #181008; }
.section-title { font-family: 'DM Sans', sans-serif; font-size: 20px; font-weight: 600; color: #181008; margin-bottom: 6px; }
.section-desc { font-family: 'Lora', serif; font-style: italic; font-size: 13px; color: #86897c; line-height: 1.6; margin-bottom: 22px; }

/* ARTICLES (pepper) */
.article { display: flex; gap: 16px; padding: 18px 0; border-top: 1px solid #d4cfc4; align-items: flex-start; }
.article:first-of-type { border-top: none; padding-top: 0; }
.article-left { display: flex; gap: 12px; flex: 1; min-width: 0; }
.article-num { font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 500; color: #ffc294; min-width: 28px; line-height: 1.2; flex-shrink: 0; }
.article-body { flex: 1; min-width: 0; }
.article-source { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #86897c; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
.article-title { font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 600; color: #181008; margin-bottom: 5px; line-height: 1.35; }
.article-title a { color: inherit; text-decoration: none; }
.article-title a:hover { text-decoration: underline; }
.article-desc { font-size: 13px; color: #59583c; line-height: 1.6; margin-bottom: 10px; }
.article-thumb { width: 80px; height: 60px; border-radius: 3px; object-fit: cover; flex-shrink: 0; filter: sepia(15%); }

/* TRADUCCIÓN A HUMANO */
.ai-explain { background: #fff9f2; border-left: 3px solid #ffb655; border-radius: 0 3px 3px 0; padding: 10px 12px; margin-top: 2px; }
.ai-explain-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; color: #b24b28; margin-bottom: 5px; }
.ai-explain-text { font-family: 'Lora', serif; font-size: 13px; color: #4c2f12; line-height: 1.65; }

/* NEEDY */
.needy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.needy-card { background: #fff9f2; border-radius: 3px; overflow: hidden; border: 1px solid #ffc294; }
.needy-img { width: 100%; height: 110px; object-fit: cover; display: block; filter: sepia(20%); }
.needy-card-body { padding: 14px; }
.needy-type { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; color: #b24b28; margin-bottom: 6px; }
.needy-title { font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 600; color: #181008; line-height: 1.35; margin-bottom: 5px; }
.needy-title a { color: inherit; text-decoration: none; }
.needy-title a:hover { text-decoration: underline; }
.needy-source { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #86897c; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
.needy-explain { border-top: 1px solid #ffc294; padding-top: 10px; }
.needy-explain-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; color: #b24b28; margin-bottom: 5px; }
.needy-explain-text { font-family: 'Lora', serif; font-size: 12px; color: #4c2f12; line-height: 1.6; font-style: italic; }

/* DEEPY */
.deepy-img { width: 100%; height: 180px; object-fit: cover; display: block; border-radius: 3px 3px 0 0; filter: sepia(30%) brightness(0.85); }
.deepy-card { background: #181008; border-radius: 0 0 3px 3px; padding: 22px; }
.deepy-quote { font-family: 'Lora', serif; font-style: italic; font-size: 15px; color: #ffc294; line-height: 1.6; margin-bottom: 14px; border-left: 3px solid #ff6f4d; padding-left: 14px; }
.deepy-title { font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.deepy-title a { color: #e8e4d9; text-decoration: none; }
.deepy-title a:hover { text-decoration: underline; }
.deepy-desc { font-size: 13px; color: #86897c; line-height: 1.6; margin-bottom: 12px; }
.deepy-source { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #59583c; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 14px; }
.deepy-explain { border-top: 1px solid #2d2010; padding-top: 14px; }
.deepy-explain-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; color: #ffb655; margin-bottom: 6px; }
.deepy-explain-text { font-family: 'Lora', serif; font-size: 13px; color: #ffc294; line-height: 1.65; font-style: italic; }

/* GOOFY */
.goofy-img { width: 100%; max-height: 300px; object-fit: cover; display: block; border-radius: 3px; margin-bottom: 12px; }
.goofy-caption { font-family: 'Lora', serif; font-style: italic; font-size: 13px; color: #86897c; text-align: center; line-height: 1.6; }

/* FOOTER */
.footer { background: #4c2f12; padding: 24px 40px; text-align: center; }
.footer p { font-family: 'Lora', serif; font-style: italic; font-size: 13px; color: #ffc294; line-height: 1.6; }
.footer-meta { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #86897c; letter-spacing: 1px; margin-top: 10px; }
.footer-meta a { color: #86897c; }
</style>
</head>
<body>
<div class="newsletter">

  <div class="header">
    <div class="header-meta">Semana {{ week }} · {{ date }} · Edición #{{ edition_num }}</div>
    <div class="header-title">Con Criter<span>IA</span></div>
    <div class="header-tagline">Lo que necesitas saber esta semana sobre inteligencia artificial — con criterio.</div>
  </div>

  <div class="intro">
    <p>{{ intro }}</p>
  </div>

  <!-- LO PEPPER -->
  <div class="section">
    <div><span class="section-label-text label-pepper">🌶️ lo pepper</span></div>
    <div class="section-title">noticias calientes</div>
    <div class="section-desc">curadas por una humana con el corazón igual de hot</div>

    {% for article in pepper %}
    <div class="article">
      <div class="article-left">
        <div class="article-num">0{{ loop.index }}</div>
        <div class="article-body">
          <div class="article-source">{{ article.source }}</div>
          <div class="article-title"><a href="{{ article.url }}">{{ article.title }}</a></div>
          {% if article.excerpt %}<div class="article-desc">{{ article.excerpt }}</div>{% endif %}
          <div class="ai-explain">
            <div class="ai-explain-label">✦ traducción a humano</div>
            <div class="ai-explain-text">{{ article.translation }}</div>
          </div>
        </div>
      </div>
      {% if article.image_url %}
      <img class="article-thumb" src="{{ article.image_url }}" alt="">
      {% endif %}
    </div>
    {% endfor %}
  </div>

  <!-- LO NEEDY -->
  <div class="section">
    <div><span class="section-label-text label-needy">✦ lo needy</span></div>
    <div class="section-title">aprendizajes de la semana</div>
    <div class="section-desc">hacks, cositas que necesitamos aprender para estar en la cresta de la ola (o al menos disimular)</div>

    <div class="needy-grid">
      {% for article in needy %}
      <div class="needy-card">
        {% if article.image_url %}
        <img class="needy-img" src="{{ article.image_url }}" alt="">
        {% endif %}
        <div class="needy-card-body">
          <div class="needy-type">{{ article.content_type }}</div>
          <div class="needy-title"><a href="{{ article.url }}">{{ article.title }}</a></div>
          <div class="needy-source">{{ article.source }}</div>
          <div class="needy-explain">
            <div class="needy-explain-label">✦ traducción a humano</div>
            <div class="needy-explain-text">{{ article.translation }}</div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- LO DEEPY -->
  <div class="section">
    <div><span class="section-label-text label-deepy">◎ lo deepy</span></div>
    <div class="section-title">para leer sin prisa</div>
    <div class="section-desc">lo que no puedes leer entre reunión y reunión porque requiere contexto, reflexión y dejar que el criterio tome forma</div>

    {% if deepy.image_url %}
    <img class="deepy-img" src="{{ deepy.image_url }}" alt="">
    {% endif %}
    <div class="deepy-card">
      {% if deepy.excerpt %}
      <div class="deepy-quote">{{ deepy.excerpt }}</div>
      {% endif %}
      <div class="deepy-title"><a href="{{ deepy.url }}">{{ deepy.title }}</a></div>
      <div class="deepy-source">{{ deepy.source }}</div>
      <div class="deepy-explain">
        <div class="deepy-explain-label">✦ traducción a humano</div>
        <div class="deepy-explain-text">{{ deepy.translation }}</div>
      </div>
    </div>
  </div>

  <!-- LO GOOFY -->
  <div class="section">
    <div><span class="section-label-text label-goofy">😄 lo goofy</span></div>
    <div class="section-title">el postre</div>
    <div class="section-desc">unas risas después de tocar fondo en medio de tanta movida artificial</div>

    {% if goofy.image_url %}
    <img class="goofy-img" src="{{ goofy.image_url }}" alt="">
    {% endif %}
    <div class="goofy-caption">{{ goofy.title }}</div>
  </div>

  <div class="footer">
    <p>"La inteligencia sin criterio es ruido.<br>Con CriterIA, intentamos que sea señal."</p>
    <div class="footer-meta">
      <a href="../index.html">Ediciones anteriores</a> · Equipo Soulsight
    </div>
  </div>

</div>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add templates/newsletter.html.j2
git commit -m "feat: jinja2 newsletter template"
```

---

## Task 6: Index page template

**Files:**
- Create: `templates/index.html.j2`

- [ ] **Step 1: Create `templates/index.html.j2`**

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Con CriterIA — Todas las ediciones</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Lora:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #d4cfc4; font-family: 'Lora', serif; padding: 60px 20px; }
.container { max-width: 560px; margin: 0 auto; }
.header { margin-bottom: 48px; }
.title { font-family: 'DM Sans', sans-serif; font-size: 32px; font-weight: 600; color: #181008; margin-bottom: 6px; }
.title span { color: #ff6f4d; }
.subtitle { font-style: italic; color: #86897c; font-size: 15px; }
.edition-list { list-style: none; }
.edition-item { border-bottom: 1px solid #c8c4b9; }
.edition-link { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; text-decoration: none; color: #181008; }
.edition-link:hover .edition-title { text-decoration: underline; }
.edition-num { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #86897c; letter-spacing: 1px; }
.edition-title { font-family: 'DM Sans', sans-serif; font-size: 15px; font-weight: 500; }
.edition-date { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #86897c; }
.footer { margin-top: 48px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #86897c; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="title">Con Criter<span>IA</span></div>
    <div class="subtitle">Newsletter interna de IA · Soulsight</div>
  </div>
  <ul class="edition-list">
    {% for edition in editions | reverse %}
    <li class="edition-item">
      <a class="edition-link" href="editions/{{ edition.filename }}">
        <span class="edition-num">#{{ edition.num }}</span>
        <span class="edition-title">Semana {{ edition.week }}, {{ edition.year }}</span>
        <span class="edition-date">{{ edition.date }}</span>
      </a>
    </li>
    {% endfor %}
  </ul>
  <div class="footer">{{ editions | length }} edición{% if editions | length != 1 %}es{% endif %} publicadas</div>
</div>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add templates/index.html.j2
git commit -m "feat: index page template"
```

---

## Task 7: Renderer module

**Files:**
- Create: `src/renderer.py`
- Create: `tests/test_renderer.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_renderer.py
import os
import pytest
from src.renderer import render_newsletter, render_index, infer_content_type


def test_infer_content_type_youtube():
    assert infer_content_type("https://youtube.com/watch?v=abc") == "▶ Video"


def test_infer_content_type_default():
    assert infer_content_type("https://medium.com/some-post") == "📄 Artículo"


def test_render_newsletter_creates_file(tmp_path):
    data = {
        "edition_num": 1,
        "week": 14,
        "year": 2026,
        "date": "7 de abril de 2026",
        "intro": "Esta semana ha sido intensa.",
        "pepper": [
            {"title": "Noticia 1", "url": "https://example.com/1",
             "source": "The Verge", "excerpt": "Resumen.", "image_url": None,
             "translation": "Explicación sencilla."},
        ],
        "needy": [
            {"title": "Tutorial 1", "url": "https://youtube.com/watch?v=1",
             "source": "YouTube", "excerpt": "", "image_url": None,
             "translation": "Aprende esto.", "content_type": "▶ Video"},
        ],
        "deepy": {
            "title": "Ensayo largo", "url": "https://noema.com/essay",
            "source": "Noema Magazine", "excerpt": "Una cita.", "image_url": None,
            "translation": "Reflexión profunda.",
        },
        "goofy": {
            "title": "Pie de foto gracioso", "url": "https://example.com/meme",
            "image_url": None,
        },
    }
    output_path = tmp_path / "2026-W14.html"
    render_newsletter(data, output_path=str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "Con CriterIA" in content
    assert "Noticia 1" in content
    assert "traducción a humano" in content


def test_render_index_creates_file(tmp_path):
    editions = [
        {"num": 1, "week": 14, "year": 2026, "date": "7 abr 2026",
         "filename": "2026-W14.html"},
    ]
    output_path = tmp_path / "index.html"
    render_index(editions, output_path=str(output_path))
    assert output_path.exists()
    content = output_path.read_text()
    assert "2026-W14.html" in content
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_renderer.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement `src/renderer.py`**

```python
import os
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

VIDEO_DOMAINS = {"youtube.com", "youtu.be", "vimeo.com"}
CAROUSEL_KEYWORDS = ["carrusel", "carousel", "slides", "thread", "hilo"]


def infer_content_type(url):
    """Infer content type badge from URL."""
    domain = urlparse(url).netloc.removeprefix("www.")
    if domain in VIDEO_DOMAINS:
        return "▶ Video"
    return "📄 Artículo"


def _get_env():
    return Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


def render_newsletter(data, output_path):
    """Render newsletter HTML and write to output_path."""
    env = _get_env()
    template = env.get_template("newsletter.html.j2")
    html = template.render(**data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def render_index(editions, output_path):
    """Render index.html with list of all editions."""
    env = _get_env()
    template = env.get_template("index.html.j2")
    html = template.render(editions=editions)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_renderer.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Run all tests to confirm nothing is broken**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/renderer.py tests/test_renderer.py
git commit -m "feat: jinja2 renderer for newsletter and index"
```

---

## Task 8: Main `generate.py` script

**Files:**
- Create: `generate.py`

This is the entry point. It orchestrates all modules and accepts CLI arguments.

- [ ] **Step 1: Create `generate.py`**

```python
#!/usr/bin/env python3
"""
Con CriterIA — Newsletter generator

Usage:
    python generate.py              # Generate current week's edition
    python generate.py --week 14    # Generate specific week
    python generate.py --no-archive # Don't archive bookmarks after generating
    python generate.py --dry-run    # Generate HTML without calling Claude API (uses placeholders)
"""
import argparse
import json
import os
import sys
from datetime import date

import config
from src.instapaper import InstapaperClient
from src.extractor import extract_og_image, extract_source_domain
from src.translator import generate_translation
from src.renderer import render_newsletter, render_index, infer_content_type

PLACEHOLDER_TRANSLATION = "[traducción a humano — ejecuta sin --dry-run para generarla con IA]"

FOLDERS = {
    "pepper": ("hot-topic", 3),
    "needy": ("aprende", 2),
    "deepy": ("profundidad", 1),
    "goofy": ("funny", 1),
}


def fetch_articles(client, folder_name, limit, dry_run):
    """Fetch bookmarks from a folder and enrich with image + translation."""
    folder_id = client.get_folder_id(folder_name)
    bookmarks = client.get_bookmarks(folder_id=folder_id, limit=limit)
    articles = []
    for bm in bookmarks:
        url = bm["url"]
        title = bm["title"]
        excerpt = bm.get("description", "")
        source = extract_source_domain(url)
        image_url = extract_og_image(url)
        if dry_run:
            translation = PLACEHOLDER_TRANSLATION
        else:
            translation = generate_translation(
                api_key=config.CLAUDE_API_KEY,
                title=title,
                source=source,
                excerpt=excerpt,
            )
        articles.append({
            "title": title,
            "url": url,
            "source": source,
            "excerpt": excerpt,
            "image_url": image_url,
            "translation": translation,
            "content_type": infer_content_type(url),
            "bookmark_id": bm["bookmark_id"],
        })
    return articles, folder_id


def load_edition_index(index_path):
    """Load existing edition list from a JSON sidecar file."""
    if os.path.exists(index_path):
        with open(index_path) as f:
            return json.load(f)
    return []


def save_edition_index(editions, index_path):
    with open(index_path, "w") as f:
        json.dump(editions, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate Con CriterIA newsletter")
    parser.add_argument("--week", type=int, default=None, help="ISO week number (default: current week)")
    parser.add_argument("--year", type=int, default=None, help="Year (default: current year)")
    parser.add_argument("--no-archive", action="store_true", help="Don't archive bookmarks after generating")
    parser.add_argument("--dry-run", action="store_true", help="Skip Claude API calls (use placeholders)")
    args = parser.parse_args()

    today = date.today()
    year = args.year or today.isocalendar()[0]
    week = args.week or today.isocalendar()[1]
    edition_filename = f"{year}-W{week:02d}.html"
    output_path = os.path.join("editions", edition_filename)

    print(f"Generating Con CriterIA · Semana {week}, {year}...")

    client = InstapaperClient(
        consumer_key=config.INSTAPAPER_CONSUMER_KEY,
        consumer_secret=config.INSTAPAPER_CONSUMER_SECRET,
        username=config.INSTAPAPER_USERNAME,
        password=config.INSTAPAPER_PASSWORD,
    )

    # Fetch all sections
    pepper, pepper_fid = fetch_articles(client, "hot-topic", 3, args.dry_run)
    needy, needy_fid = fetch_articles(client, "aprende", 2, args.dry_run)
    deepy_list, deepy_fid = fetch_articles(client, "profundidad", 1, args.dry_run)
    goofy_list, goofy_fid = fetch_articles(client, "funny", 1, args.dry_run)

    if not pepper:
        print("ERROR: No articles found in 'hot-topic' folder. Aborting.")
        sys.exit(1)

    # Load edition index to get edition number
    index_path = "editions/.index.json"
    editions = load_edition_index(index_path)
    edition_num = len(editions) + 1

    # Format date in Spanish
    months = ["enero","febrero","marzo","abril","mayo","junio",
              "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    date_str = f"{today.day} de {months[today.month - 1]} de {today.year}"

    data = {
        "edition_num": edition_num,
        "week": week,
        "year": year,
        "date": date_str,
        "intro": f"Semana {week} lista. Aquí tienes lo más relevante del mundo de la IA — curado con criterio.",
        "pepper": pepper,
        "needy": needy,
        "deepy": deepy_list[0] if deepy_list else {},
        "goofy": goofy_list[0] if goofy_list else {},
    }

    render_newsletter(data, output_path=output_path)
    print(f"✓ Newsletter generada: {output_path}")

    # Update index
    editions.append({
        "num": edition_num,
        "week": week,
        "year": year,
        "date": date_str,
        "filename": edition_filename,
    })
    save_edition_index(editions, index_path)
    render_index(editions, output_path="index.html")
    print("✓ index.html actualizado")

    # Archive bookmarks
    should_archive = not args.no_archive and getattr(config, "ARCHIVE_AFTER_GENERATE", True)
    if should_archive and not args.dry_run:
        all_bookmark_ids = (
            [a["bookmark_id"] for a in pepper] +
            [a["bookmark_id"] for a in needy] +
            [a["bookmark_id"] for a in deepy_list] +
            [a["bookmark_id"] for a in goofy_list]
        )
        for bid in all_bookmark_ids:
            client.archive_bookmark(bid)
        print(f"✓ {len(all_bookmark_ids)} bookmarks archivados en Instapaper")

    print(f"\nListo. Abre {output_path} en tu navegador para revisarlo.")
    print(f"Cuando estés conforme: git add editions/ index.html && git push")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test with dry-run (no Instapaper key needed yet)**

Once you have Instapaper credentials in `config.py`, run:

```bash
python generate.py --dry-run
```

Expected output:
```
Generating Con CriterIA · Semana XX, 2026...
✓ Newsletter generada: editions/2026-WXX.html
✓ index.html actualizado
Listo. Abre editions/2026-WXX.html en tu navegador para revisarlo.
```

Open `editions/2026-WXX.html` in a browser and verify the layout matches the approved mockup.

- [ ] **Step 3: Test full run (with all API keys)**

```bash
python generate.py
```

Expected: same output + `✓ X bookmarks archivados en Instapaper`

- [ ] **Step 4: Commit**

```bash
git add generate.py editions/.gitkeep
git commit -m "feat: main generate.py entry point"
```

---

## Task 9: GitHub Pages setup

**Files:** no new files — GitHub configuration

- [ ] **Step 1: Create GitHub repository**

Go to https://github.com/new and create a repository named `con-criteria` (public or private — Pages works on both with the right plan).

- [ ] **Step 2: Add remote and push**

```bash
git remote add origin https://github.com/TU_USUARIO/con-criteria.git
git branch -M main
git push -u origin main
```

Replace `TU_USUARIO` with your GitHub username.

- [ ] **Step 3: Enable GitHub Pages**

1. Go to your repo on GitHub → Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Click Save

GitHub will show the URL: `https://TU_USUARIO.github.io/con-criteria/`

- [ ] **Step 4: Verify index page loads**

Open `https://TU_USUARIO.github.io/con-criteria/` in a browser.

Expected: the index page with the list of editions loads correctly.

- [ ] **Step 5: Test a full edition URL**

Open `https://TU_USUARIO.github.io/con-criteria/editions/2026-WXX.html`

Expected: the newsletter renders correctly.

---

## Weekly workflow (after setup)

Each Monday:

```bash
# 1. Ensure you have articles in Instapaper folders: hot-topic, aprende, profundidad, funny

# 2. Generate the newsletter
python generate.py

# 3. Open and review the HTML
open editions/$(ls editions/ | sort | tail -1)

# 4. Publish
git add editions/ index.html
git commit -m "newsletter: semana XX"
git push

# 5. Share the link
# https://TU_USUARIO.github.io/con-criteria/editions/2026-WXX.html
```

---

## Self-review

**Spec coverage:**
- ✅ Instapaper API with 4 folders → Task 2
- ✅ og:image extraction → Task 3
- ✅ Claude API "traducción a humano" → Task 4
- ✅ Jinja2 HTML template with all 4 sections + brand → Task 5
- ✅ Index page → Task 6 + 7
- ✅ generate.py entry point with --dry-run, --no-archive flags → Task 8
- ✅ GitHub Pages setup → Task 9
- ✅ Archive bookmarks (optional) → Task 8

**Placeholder scan:** No TBDs. All code blocks are complete.

**Type consistency:** `article` dict keys (`title`, `url`, `source`, `excerpt`, `image_url`, `translation`, `content_type`, `bookmark_id`) are consistent across `generate.py`, `test_renderer.py`, and `newsletter.html.j2`.
