"""
Plantillas de prompts académicos optimizados para análisis bibliográfico.
Diseñados para minimizar tokens de salida y facilitar el parsing.
"""

ANALYSIS_SYSTEM_PROMPT = (
    "Eres un asistente académico. Responde siempre en español. "
    "Usa EXACTAMENTE las 12 etiquetas XML indicadas, en orden, sin omitir ninguna. "
    "Si no hay abstract, INFIERE de título, autores, revista y contexto del proyecto. "
    "NUNCA escribas 'No disponible'. SIEMPRE deduce algo útil de los datos que tienes. "
    "Escribe 2-3 oraciones por sección."
)

ANALYSIS_USER_PROMPT = """Analiza este artículo y completa las 12 secciones. 2-3 oraciones por sección.
REGLAS: (1) Completa TODAS las 12 secciones sin excepción. (2) Si no hay abstract, infiere del título y contexto. (3) NUNCA dejes una sección vacía. (4) NUNCA escribas "No disponible".

Título: {titulo}
Autores: {autores}
Año: {anio}
Revista: {journal}
Base de datos: {base_datos}
Abstract: {abstract}

Contexto del proyecto: {proyecto_context}

Responde EXACTAMENTE con estas 12 etiquetas en este orden:
<PROBLEMA>Problema central del artículo</PROBLEMA>
<METODOLOGIA>Metodología o enfoque utilizado</METODOLOGIA>
<RESULTADOS>Resultados principales obtenidos</RESULTADOS>
<APORTES>Aportes más relevantes</APORTES>
<LIMITACIONES>Limitaciones identificadas</LIMITACIONES>
<RELACION_CONEXION>Conexión con el proyecto descrito</RELACION_CONEXION>
<RELACION_REUTILIZAR>Técnicas/modelos/datasets reutilizables en el proyecto</RELACION_REUTILIZAR>
<RELACION_DIFERENCIA>Diferencias entre este artículo y la propuesta del proyecto</RELACION_DIFERENCIA>
<NIVEL_RELEVANCIA>Alta/Media/Baja + justificación</NIVEL_RELEVANCIA>
<USO_PROYECTO>Marco teórico/Metodología/Comparación/Múltiple + justificación</USO_PROYECTO>
<CLASIFICACION_TIPO>Teórico/Empírico/Revisión Sistemática/Caso de Estudio/Propuesta Metodológica/Otro + justificación</CLASIFICACION_TIPO>
<OBSERVACIONES>Idioma, dataset, código fuente, calidad, acceso</OBSERVACIONES>"""

# --------------------------------------------------------------------------- #
# Prompt compacto para modo CPU: menos tokens de entrada = respuesta más rápida
# --------------------------------------------------------------------------- #

CPU_ANALYSIS_USER_PROMPT = """Artículo: "{titulo}" por {autores} ({anio}), en {journal}. Base: {base_datos}.
Abstract: {abstract}
Proyecto: {proyecto_context}

Completa las 12 secciones. Escribe 2-3 oraciones por sección para explicar bien cada idea. Infiere del título si no hay abstract. IMPORTANTE: debes completar TODAS las 12 secciones sin excepción.
<PROBLEMA>2-3 oraciones</PROBLEMA>
<METODOLOGIA>2-3 oraciones</METODOLOGIA>
<RESULTADOS>2-3 oraciones</RESULTADOS>
<APORTES>2-3 oraciones</APORTES>
<LIMITACIONES>2-3 oraciones</LIMITACIONES>
<RELACION_CONEXION>2-3 oraciones</RELACION_CONEXION>
<RELACION_REUTILIZAR>2-3 oraciones</RELACION_REUTILIZAR>
<RELACION_DIFERENCIA>2-3 oraciones</RELACION_DIFERENCIA>
<NIVEL_RELEVANCIA>Alta/Media/Baja. Justifica en 1-2 oraciones.</NIVEL_RELEVANCIA>
<USO_PROYECTO>Marco teórico/Metodología/Comparación/Múltiple. Justifica.</USO_PROYECTO>
<CLASIFICACION_TIPO>Teórico/Empírico/Revisión Sistemática/Caso de Estudio/Propuesta Metodológica/Otro. Justifica.</CLASIFICACION_TIPO>
<OBSERVACIONES>2-3 oraciones</OBSERVACIONES>"""

CPU_PROJECT_CONTEXT = (
    "Sistema de Gestión de RRHH con IA para startups colombianas. "
    "Usa ML y PLN para selección de personal y nómina automatizada. "
    "Cumplimiento normativo colombiano (Ley 1581, UGPP). "
    "Busca reducir sesgos en contratación y mejorar eficiencia operativa."
)

# --------------------------------------------------------------------------- #
# Secciones esperadas
# --------------------------------------------------------------------------- #

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