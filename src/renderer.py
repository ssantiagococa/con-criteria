import os
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

VIDEO_DOMAINS = {"youtube.com", "youtu.be", "vimeo.com"}


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
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def render_index(editions, output_path):
    """Render index.html with list of all editions."""
    env = _get_env()
    template = env.get_template("index.html.j2")
    html = template.render(editions=editions)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
