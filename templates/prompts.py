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

DEFAULT_PROJECT_CONTEXT = """PROYECTO DE GRADO — Universidad de San Buenaventura
Autores: Juan Sebastián Fandiño Novoa, Miguel Ángel Bonilla Torres

TÍTULO:
Desarrollo de una plataforma PaaS para la detección de ataques de phishing basados
en homografía IDN en entornos académicos mediante sistemas multiagente de IA.

PROBLEMA QUE RESUELVE:
La Universidad de San Buenaventura carece de una herramienta específica para detectar
phishing en correos institucionales. Los estudiantes no están concientizados sobre ataques
avanzados como la homografía IDN, donde caracteres Unicode visualmente idénticos crean
dominios falsos casi indetectables. Las soluciones existentes son monolíticas, no explican
sus decisiones y no están adaptadas a entornos educativos.

OBJETIVO GENERAL:
Desarrollar una plataforma PaaS basada en un sistema multiagente de IA que detecte ataques
de phishing con énfasis en homografía IDN en correos institucionales de estudiantes
universitarios, integrando componentes educativos y de concientización.

TÉCNICAS Y ENFOQUE TÉCNICO:
- Sistemas Multiagente (MAS): orquestación de agentes especializados en análisis paralelo.
- Agente de URLs / IDN: detección de homografía con mapeo Unicode + ML.
- LLMs (Large Language Models): análisis semántico del contenido del correo.
- Fusión de evidencias: combina salidas de todos los agentes para un veredicto final.
- XAI (SHAP / LIME): explicabilidad de decisiones al usuario final.
- Deep Learning (BiLSTM, CNN): análisis de URLs y contenido textual.
- Diseño cuasi-experimental: validación estadística multiagente vs. modelo monolítico baseline.
- Scrum (6 sprints): marco de desarrollo ágil e iterativo.

TECNOLOGÍAS PRINCIPALES:
- Backend / API: Python + FastAPI
- Frontend (Dashboard Admin): React.js
- Canal de análisis (usuario): Extensión de navegador Chrome / Firefox
- Orquestación e infraestructura: Docker / Kubernetes
- Base de datos relacional: correos, resultados, incidentes
- Almacenamiento vectorial: embeddings para búsqueda semántica
- Modelos de lenguaje: LLMs tipo GPT para análisis semántico

LIMITACIONES DEL PROYECTO:
- Solo analiza correos visualizados desde el navegador (vía extensión); no cubre clientes
  de escritorio, móviles u otras interfaces.
- Análisis bajo demanda (no monitoreo pasivo continuo); requiere interacción activa.
- Latencia inherente a la cadena multiagente (múltiples llamadas a API).
- Cobertura restringida al correo institucional de estudiantes USB.
- Dashboard de solo visualización; sin respuesta automatizada (bloqueo/cuarentena).
- Requiere conectividad constante a internet para operar.
- Validado únicamente con datos de la USB; generalización a otras instituciones no garantizada.
- Optimizado para homografía IDN y análisis semántico; no cubre redirecciones encadenadas,
  acortadores múltiples, contenido JS dinámico ni phishing por adjuntos.

USUARIOS FINALES:
- Estudiantes universitarios (USB): reciben alertas, análisis explicados y módulo educativo.
- Administradores de seguridad: monitoreo en dashboard (incidentes, trazas, estadísticas).
- Docentes: acceso a métricas del módulo educativo."""
