import os
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
