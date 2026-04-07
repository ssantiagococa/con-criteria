# Con CriterIA

Newsletter interna semanal de Inteligencia Artificial.

👉 **[Ver todas las ediciones](https://ssantiagococa.github.io/con-criteria/)**

---

## Cómo funciona

Cada semana se guardan artículos en **Instapaper** organizados en 4 carpetas. Un script Python lee esos artículos, genera una explicación sencilla para cada uno usando la API de Claude, y produce un HTML listo para publicar en GitHub Pages.


### Carpetas de Instapaper

| Carpeta | Sección | Contenido |
|---|---|---|
| `hot-topic` | 🌶️ lo pepper | 3 noticias de la semana |
| `aprende` | ✦ lo needy | 2 recursos para aprender |
| `profundidad` | ◎ lo deepy | 1 lectura larga |
| `funny` | 😄 lo goofy | 1 viñeta o imagen graciosa |

---

## Setup inicial

**1. Instala las dependencias**

```bash
pip3 install -r requirements.txt
```

**2. Configura las credenciales**

```bash
cp config.example.py config.py
```

Edita `config.py` con tus credenciales:
- `INSTAPAPER_CONSUMER_KEY` / `INSTAPAPER_CONSUMER_SECRET` — de [instapaper.com/api](https://www.instapaper.com/api)
- `INSTAPAPER_USERNAME` / `INSTAPAPER_PASSWORD` — tu cuenta de Instapaper
- `CLAUDE_API_KEY` — de [console.anthropic.com](https://console.anthropic.com)

---

## Flujo semanal

**1. Durante la semana** — guarda artículos en Instapaper en las carpetas correspondientes.

**2. El día de publicación** — genera la newsletter:

```bash
python3 generate.py
```

Opciones útiles:
```bash
python3 generate.py --dry-run        # Sin Instapaper ni Claude (datos de ejemplo)
python3 generate.py --no-translate   # Lee Instapaper real, sin llamar a Claude
python3 generate.py --no-archive     # No archiva los bookmarks tras generar
python3 generate.py --week 14        # Genera una semana específica
```

**3. Revisa el HTML** generado en `editions/`:

```bash
open editions/2026-W15.html
```

**4. Publica:**

```bash
git add editions/ index.html
git commit -m "newsletter: semana 15"
git push
```

**5. Comparte el enlace** por email y Slack:
```
https://ssantiagococa.github.io/con-criteria/editions/2026-W15.html
```

---

## Estructura del proyecto

```
con-criteria/
├── editions/          # HTMLs de cada edición (publicados vía GitHub Pages)
├── templates/         # Plantillas Jinja2
│   ├── newsletter.html.j2
│   └── index.html.j2
├── src/
│   ├── instapaper.py  # Cliente API de Instapaper
│   ├── extractor.py   # Extracción de og:image
│   ├── translator.py  # Generación de "traducción a humano" con Claude
│   └── renderer.py    # Renderizado HTML con Jinja2
├── tests/             # Tests unitarios
├── generate.py        # Script principal
├── config.example.py  # Plantilla de credenciales
└── index.html         # Índice de ediciones (generado automáticamente)
```

---

> *"La inteligencia sin criterio es ruido. Con CriterIA, intentamos que sea señal."*
