import anthropic

SYSTEM_PROMPT = """Eres el asistente editorial de la newsletter "Con CriterIA", \
una newsletter interna de una consultora independiente de estrategia \
para directivos y grandes empresas con enfoque humanista a la hora de abordar \
los grandes desafíos de las organizaciones.

Tu misión es escribir la sección "traducción a humano" de cada artículo: \
3-4 líneas que expliquen el contenido de forma clara y cercana para personas \
sin conocimientos técnicos. Usa metáforas cotidianas, ejemplos concretos y, \
cuando sea relevante, menciona qué implicación práctica puede tener para este equipo. \
Tono directo, sin jerga, con personalidad."""

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
