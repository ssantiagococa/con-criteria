# Contexto del Proyecto: Con CriterIA

> Última actualización: 2026-04-06

## Descripción general

Newsletter interna semanal de contenidos sobre Inteligencia Artificial. Nombre: **Con CriterIA**. Voz editorial cercana, directa y con personalidad — no un agregador sino una curaduría con criterio humano.

## Objetivos

- Mantener al equipo al día sobre IA de forma digerible y con personalidad
- Periodicidad semanal
- Distribuir por email + Slack con enlace a HTML alojado en GitHub Pages
- Preservar ediciones anteriores accesibles en el repositorio

## Arquitectura

- **Curación:** Instapaper (4 folders: `hot-topic`, `aprende`, `profundidad`, `funny`)
- **Generación:** script Python local (`generate.py`) que lee Instapaper API y produce HTML
- **Hosting:** GitHub Pages (repo nuevo por crear)
- **Distribución:** manual — enlace enviado por email y Slack cada semana

## Secciones

| Label | Nombre | Folder | Contenido |
|---|---|---|---|
| 🌶️ | lo pepper | `hot-topic` | 3 noticias calientes de la semana |
| ✦ | lo needy | `aprende` | 2 recursos para aprender |
| ◎ | lo deepy | `profundidad` | 1 lectura larga para reflexionar |
| 😄 | lo goofy | `funny` | 1 viñeta o imagen graciosa |

## Diseño visual

- Estilo: **warm editorial** con brand corporativo
- Colores principales: Beige `#e8e4d9`, Negro `#181008`, Coral `#ff6f4d`, Salmón `#ffc294`, Marrón `#4c2f12`
- Tipografía (Google Fonts): DM Sans (titulares), Lora (cuerpo), JetBrains Mono (metadatos)
- Imágenes: `og:image` extraída automáticamente por el script de cada artículo
- Cada artículo incluye un bloque **"✦ traducción a humano"** generado por la API de Claude: 3-4 líneas sencillas con metáforas y ejemplos para un equipo no técnico

## Estado actual

- [x] Diseño visual aprobado (mockup en `.superpowers/brainstorm/`)
- [x] Spec técnico escrito (`docs/superpowers/specs/2026-04-06-con-criteria-design.md`)
- [ ] Plan de implementación
- [ ] Repositorio GitHub creado
- [ ] Script generador implementado

## Decisiones técnicas relevantes

- Pocket cerró en julio 2025 → se usa **Instapaper** como gestor de contenidos
- Generación **semi-automática**: el script genera el HTML pero el editor lo revisa y hace el `git push` manualmente
- Las fuentes corporativas (Acid Grotesk, Gestura Text, Aeonik Mono) son propietarias → se usan equivalentes de Google Fonts
- Imágenes referenciadas por URL (no alojadas en el repo)

## Ficheros relevantes

- `docs/superpowers/specs/2026-04-06-con-criteria-design.md` — spec completo
- `.superpowers/brainstorm/` — mockups visuales (ignorado por git)
