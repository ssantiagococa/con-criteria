from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

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
    "elpais.com": "El País",
    "elconfidencial.com": "El Confidencial",
    "hbr.org": "Harvard Business Review",
    "substack.com": "Substack",
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
