# Con CriterIA — Spec de diseño

**Fecha:** 2026-04-06  
**Estado:** Aprobado

---

## 1. Descripción general

Newsletter interna semanal de contenidos sobre Inteligencia Artificial para el equipo de Soulsight. El nombre es **Con CriterIA**. La voz editorial es cercana, directa y con personalidad propia — no un agregador de noticias sino una curaduría con criterio humano.

---

## 2. Flujo de trabajo

### Curación de contenidos
- Herramienta: **Instapaper**
- El editor guarda artículos en Instapaper durante la semana organizándolos en 4 carpetas (folders):
  - `hot-topic` → sección lo pepper (3 artículos)
  - `aprende` → sección lo needy (2 artículos)
  - `profundidad` → sección lo deepy (1 artículo)
  - `funny` → sección lo goofy (1 viñeta o imagen)

### Generación del HTML
- Cada semana se ejecuta un **script Python local** (`generate.py`)
- El script lee los artículos de Instapaper vía **API oficial** por folder
- Para cada artículo extrae: título, URL, descripción/excerpt, imagen `og:image`
- Genera un fichero HTML completo (`editions/YYYY-WXX.html`) listo para publicar
- El editor revisa el HTML generado antes de publicar

### Publicación
- El HTML se sube a un **repositorio GitHub** nuevo (a crear)
- El repositorio usa **GitHub Pages** para servir los ficheros estáticamente
- URL pública: `[usuario].github.io/con-criteria/editions/YYYY-WXX.html`
- Las ediciones anteriores permanecen accesibles en el mismo repositorio

### Distribución
- Cada semana el editor envía manualmente el enlace a la edición por:
  - **Email** (Gmail u Outlook)
  - **Slack** (canal del equipo)

---

## 3. Estructura del proyecto

```
con-criteria/
├── editions/
│   └── YYYY-WXX.html        # Una por semana (ej. 2026-W14.html)
├── index.html               # Listado de todas las ediciones
├── generate.py              # Script generador
├── config.py                # Credenciales Instapaper API (en .gitignore)
├── requirements.txt
└── .gitignore
```

---

## 4. Diseño visual

### Estilo
Warm editorial con brand Soulsight. Tono humano, cálido y accesible.

### Paleta de colores
| Nombre | HEX | Uso |
|---|---|---|
| Beige | `#e8e4d9` | Fondo principal |
| Negro enriquecido | `#181008` | Cabecera, fondo deepy |
| Coral | `#ff6f4d` | Acento principal, borde cabecera |
| Salmón | `#ffc294` | Numeración artículos |
| Naranja oscuro | `#b24b28` | Labels tipo de contenido |
| Amarillo | `#ffb655` | Label lo needy |
| Marrón | `#4c2f12` | Footer |
| Verde pálido | `#86897c` | Texto secundario, metadatos |
| Verde oscuro | `#59583c` | Label lo deepy, texto cuerpo |
| Gris | `#abb4ba` | Tagline cabecera |

### Tipografía
Las fuentes corporativas (Acid Grotesk, Gestura Text, Aeonik Mono) son propietarias. En el HTML se usan equivalentes de Google Fonts:

| Uso | Fuente corporativa | Google Font |
|---|---|---|
| Titulares | Acid Grotesk Medium | DM Sans 600 |
| Cuerpo | Gestura Text Extralight | Lora 400 (italic) |
| Metadatos / labels | Aeonik Mono Regular | JetBrains Mono 400 |

### Estructura del HTML por edición

1. **Cabecera** — fondo negro, título "Con CriterIA" con la IA en coral, tagline en gris, borde inferior coral
2. **Intro** — párrafo editorial libre escrito por la curadora
3. **🌶️ lo pepper** — 3 artículos con thumbnail derecho, número, fuente, título y descripción
4. **✦ lo needy** — 2 cards en grid 2 columnas, imagen superior, tipo de recurso (video/artículo/carrusel), título y fuente
5. **◎ lo deepy** — imagen panorámica superior + bloque oscuro con cita, título, descripción y fuente
6. **😄 lo goofy** — imagen a ancho completo + pie de foto con tono humorístico
7. **Footer** — fondo marrón, tagline fija, enlace a ediciones anteriores

### Imágenes
- Cada artículo usa la imagen `og:image` extraída automáticamente por el script
- Si un artículo no tiene `og:image`, se usa un placeholder neutro
- Las imágenes se referencian por URL (no se descargan ni alojan en el repo)

---

## 5. Script generador (`generate.py`)

### Responsabilidades
1. Autenticarse en la API de Instapaper con credenciales desde `config.py`
2. Leer los bookmarks de cada folder (`hot-topic`, `aprende`, `profundidad`, `funny`)
3. Para cada bookmark: extraer título, URL, excerpt y `og:image` (via scraping de la URL o metadatos de Instapaper)
4. Renderizar el template HTML con los datos extraídos
5. Guardar el fichero en `editions/YYYY-WXX.html`
6. Opcionalmente, marcar los bookmarks procesados como archivados en Instapaper (configurable en `config.py` para que no aparezcan en la siguiente edición)

### Inputs
- Credenciales Instapaper (OAuth consumer key/secret + token de usuario)
- Año y número de semana (por defecto: semana actual)

### Output
- `editions/YYYY-WXX.html` — edición completa lista para publicar

### Dependencias Python
- `requests` — llamadas HTTP a la API de Instapaper
- `beautifulsoup4` — extracción de `og:image` de las URLs
- `jinja2` — templating HTML
- `python-dateutil` — cálculo de número de semana

---

## 6. Índice de ediciones (`index.html`)

Página estática generada o actualizada por el script con un listado de todas las ediciones publicadas, enlazando a cada `editions/YYYY-WXX.html`.

---

## 6b. Bloque "traducción a humano"

Cada artículo incluye un bloque generado automáticamente por la **API de Claude** con 3-4 líneas de explicación sencilla del contenido, pensada para un equipo no técnico. Usa metáforas, ejemplos y comparativas cotidianas.

### Apariencia visual
- Label: `✦ traducción a humano` (en JetBrains Mono, color naranja oscuro `#b24b28`)
- Fondo: `#fff9f2` con borde izquierdo amarillo `#ffb655`
- Texto en Lora, tono cálido

### Cómo se genera
El script llama a la API de Claude pasando:
- Título del artículo
- Fuente
- Excerpt / descripción

Con un prompt del tipo:
> "Explica este artículo en 3-4 líneas para alguien sin conocimientos técnicos. Usa metáforas cotidianas y, si es relevante, menciona qué implicación práctica puede tener para un equipo de una consultora independiente de estrategia para directivos y grandes empresas con enfoque humanista a la hora de abordar los grandes desafíos de las organizaciones. Tono cercano, sin jerga."

### Aparece en
- Cada artículo de **lo pepper** (3 bloques)
- Cada card de **lo needy** (2 bloques)
- El artículo de **lo deepy** (1 bloque, sobre fondo oscuro en color salmón)
- **No aparece** en lo goofy (es humor, se entiende solo)

---

## 7. Lo que queda fuera del alcance (v1)

- Envío automático de email o Slack (el editor lo hace manualmente)
- Sistema de suscripción
- Estadísticas de lectura
- Comentarios o feedback inline
- Traducción al inglés

---

## 8. Próximos pasos

Ver plan de implementación en `docs/superpowers/plans/`.
