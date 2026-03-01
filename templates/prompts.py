"""
Plantillas de prompts académicos optimizados para análisis bibliográfico.
Diseñados para minimizar tokens de salida y facilitar el parsing.
"""

ANALYSIS_SYSTEM_PROMPT = (
    "Eres un asistente académico especializado en análisis de literatura científica. "
    "Responde siempre en español. Sé conciso: máximo 5-6 oraciones por sección. "
    "Usa el formato de etiquetas delimitadoras indicado. No repitas el título ni los metadatos."
)

ANALYSIS_USER_PROMPT = """Analiza el siguiente artículo académico y completa TODAS las secciones.
Responde ÚNICAMENTE usando las etiquetas delimitadoras mostradas. Sé conciso (5-6 oraciones por sección).

--- DATOS DEL ARTÍCULO ---
Título: {titulo}
Autores: {autores}
Año: {anio}
Revista/Conferencia: {journal}
Base de datos: {base_datos}

--- ABSTRACT / CONTENIDO ---
{abstract}

--- CONTEXTO DEL PROYECTO (úsalo para responder las secciones 5 y 6) ---
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

[RELACION_CONEXION]
¿Cómo se conecta este artículo con el problema del proyecto descrito? Sé específico y concreto.
[/RELACION_CONEXION]

[RELACION_REUTILIZAR]
¿Qué técnicas, modelos, datasets, métricas o marcos teóricos del artículo se pueden reutilizar directamente en el proyecto?
[/RELACION_REUTILIZAR]

[RELACION_DIFERENCIA]
¿En qué se diferencia o mejora la propuesta del proyecto respecto a lo que plantea este artículo?
[/RELACION_DIFERENCIA]

[NIVEL_RELEVANCIA]
Indica SOLO una palabra: Alta, Media o Baja. Luego justifica en una oración.
[/NIVEL_RELEVANCIA]

[USO_PROYECTO]
Indica el uso principal: Marco teórico, Metodología, Comparación o Múltiple. Justifica brevemente.
[/USO_PROYECTO]

[CLASIFICACION_TIPO]
Clasifica el artículo en UNA de estas categorías: Teórico, Empírico, Revisión Sistemática, Caso de Estudio, Propuesta Metodológica, Otro. Justifica en una oración.
[/CLASIFICACION_TIPO]

[OBSERVACIONES]
Notas adicionales relevantes: idioma, disponibilidad de dataset o código fuente, calidad de la fuente, restricciones de acceso, etc.
[/OBSERVACIONES]"""

# Secciones esperadas en la respuesta del LLM, en orden
EXPECTED_SECTIONS = [
    "PROBLEMA",
    "METODOLOGIA",
    "RESULTADOS",
    "APORTES",
    "LIMITACIONES",
    "RELACION_CONEXION",
    "RELACION_REUTILIZAR",
    "RELACION_DIFERENCIA",
    "NIVEL_RELEVANCIA",
    "USO_PROYECTO",
    "CLASIFICACION_TIPO",
    "OBSERVACIONES",
]

DEFAULT_PROJECT_CONTEXT = """PROYECTO DE GRADO

TÍTULO:
Sistema de Gestión de RRHH con IA para startups colombianas: optimización y cumplimiento normativo.

PROBLEMA QUE RESUELVE:
Las startups colombianas dependen de procesos manuales y sistemas fragmentados para gestionar
nómina y selección de personal. Esto genera errores en pagos, sesgos en contratación,
incumplimiento de la Ley 1581 de 2012 (protección de datos personales) y sanciones de la UGPP.
El 67% de las organizaciones colombianas usan sistemas desconectados y el 74% de los empleadores
reportan dificultades para encontrar talento adecuado.

OBJETIVO GENERAL:
Diseñar un sistema de inteligencia artificial para los procesos de selección de personal en
empresas colombianas, evaluando su impacto en la eficiencia operativa y la calidad de las
contrataciones.

TÉCNICAS Y ENFOQUE TÉCNICO:
- Metodología mixta (cualitativa + cuantitativa) combinada con desarrollo ágil Scrum.
- Machine Learning: algoritmos de clasificación y preselección de currículos.
- Procesamiento de Lenguaje Natural (PLN/NLP): evaluación de competencias de candidatos
  y programación automatizada de entrevistas.
- Componente cuantitativo: medición de indicadores de eficiencia, precisión en nómina
  y cumplimiento normativo.

TECNOLOGÍAS PRINCIPALES:
- IA/ML: algoritmos de clasificación y preselección de perfiles.
- PLN (NLP): análisis de competencias y automatización de entrevistas.
- Modelo de despliegue SaaS en la nube.
- Contexto de integración con plataformas como SAP, Workday y Microsoft Teams.

LIMITACIONES DEL PROYECTO:
- Dirigido exclusivamente a startups; no aplica a grandes corporaciones.
- Alcance restringido a empresas colombianas; no generalizable a otros países sin ajuste normativo.
- No garantiza integración sin fricción en startups con infraestructura tecnológica deficiente.
- No aborda la resistencia cultural al cambio organizacional.
- Stack tecnológico específico (lenguaje, framework ML, proveedor cloud) aún por definir formalmente.

USUARIOS FINALES:
- Profesionales de RRHH de startups colombianas: selección de personal y administración de nómina.
- Dirección de startups: supervisión de cumplimiento normativo y eficiencia operativa.
- Candidatos: beneficiados indirectamente por un proceso de selección más transparente y objetivo."""
