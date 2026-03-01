"""
Plantillas de prompts académicos optimizados para análisis bibliográfico.
Diseñados para minimizar tokens de salida y facilitar el parsing.
"""

ANALYSIS_SYSTEM_PROMPT = (
    "Eres un asistente académico especializado en análisis de literatura científica. "
    "Responde siempre en español. Sé conciso: máximo 3-4 oraciones por sección. "
    "Usa el formato de etiquetas delimitadoras indicado. No repitas el título ni los metadatos."
)

ANALYSIS_USER_PROMPT = """Analiza el siguiente artículo académico y completa TODAS las secciones.
Responde ÚNICAMENTE usando las etiquetas delimitadoras mostradas. Sé conciso (3-4 oraciones por sección).

--- DATOS DEL ARTÍCULO ---
Título: {titulo}
Autores: {autores}
Año: {anio}
Revista/Conferencia: {journal}
Base de datos: {base_datos}

--- ABSTRACT / CONTENIDO ---
{abstract}

--- CONTEXTO DEL PROYECTO ---
{proyecto_context}

--- FORMATO DE RESPUESTA (respeta exactamente estas etiquetas) ---

[PROBLEMA]
Describe el problema central que aborda el artículo.
[/PROBLEMA]

[METODOLOGIA]
Describe la metodología o enfoque utilizado.
[/METODOLOGIA]

[RESULTADOS]
Resume los resultados principales obtenidos.
[/RESULTADOS]

[APORTES]
Identifica los aportes más relevantes del artículo.
[/APORTES]

[LIMITACIONES]
Señala las limitaciones identificadas o reconocidas.
[/LIMITACIONES]

[RELACION_PROYECTO]
Explica cómo se relaciona este artículo con el proyecto descrito.
[/RELACION_PROYECTO]

[CLASIFICACION]
Clasifica el artículo en UNA de estas categorías: Teórico, Empírico, Revisión Sistemática, Caso de Estudio, Propuesta Metodológica, Otro.
Justifica brevemente.
[/CLASIFICACION]"""

# Secciones esperadas en la respuesta del LLM, en orden
EXPECTED_SECTIONS = [
    "PROBLEMA",
    "METODOLOGIA",
    "RESULTADOS",
    "APORTES",
    "LIMITACIONES",
    "RELACION_PROYECTO",
    "CLASIFICACION",
]

DEFAULT_PROJECT_CONTEXT = (
    "El proyecto investiga técnicas y herramientas para la revisión sistemática "
    "de literatura académica, con énfasis en automatización y procesamiento "
    "eficiente de grandes volúmenes de publicaciones científicas."
)
