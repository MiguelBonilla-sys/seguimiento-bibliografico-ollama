"""
Plantillas de prompts académicos optimizados para análisis bibliográfico.
Diseñados para minimizar tokens de salida y facilitar el parsing.
"""

ANALYSIS_SYSTEM_PROMPT = (
    "Eres un asistente académico experto en análisis de literatura científica. "
    "REGLA ABSOLUTA: responde EXCLUSIVAMENTE usando las etiquetas XML indicadas. "
    "NUNCA escribas texto fuera de las etiquetas XML. "
    "Responde siempre en español. Máximo 4 oraciones por sección. "
    "No repitas el título ni los metadatos del artículo."
)

ANALYSIS_USER_PROMPT = """Analiza el artículo académico y completa TODAS las etiquetas XML.
IMPORTANTE: NO escribas nada fuera de las etiquetas XML. Empieza directamente con <PROBLEMA>.

DATOS DEL ARTÍCULO:
Título: {titulo}
Autores: {autores}
Año: {anio}
Revista/Conferencia: {journal}
Base de datos: {base_datos}

ABSTRACT:
{abstract}

CONTEXTO DEL PROYECTO (para secciones RELACION y CLASIFICACION):
{proyecto_context}

RESPONDE SOLO CON ESTE FORMATO XML — sin texto adicional antes ni después:

<PROBLEMA>
Problema central que aborda el artículo.
</PROBLEMA>

<METODOLOGIA>
Metodología o enfoque técnico utilizado.
</METODOLOGIA>

<RESULTADOS>
Resultados principales obtenidos.
</RESULTADOS>

<APORTES>
Aportes más relevantes del artículo.
</APORTES>

<LIMITACIONES>
Limitaciones identificadas en el artículo.
</LIMITACIONES>

<RELACION_CONEXION>
Cómo se conecta este artículo con el problema del proyecto. Sé específico.
</RELACION_CONEXION>

<RELACION_REUTILIZAR>
Técnicas, modelos, datasets o marcos teóricos del artículo reutilizables en el proyecto.
</RELACION_REUTILIZAR>

<RELACION_DIFERENCIA>
En qué se diferencia o mejora la propuesta del proyecto respecto a este artículo.
</RELACION_DIFERENCIA>

<NIVEL_RELEVANCIA>
Una sola palabra (Alta, Media o Baja) seguida de una oración de justificación.
</NIVEL_RELEVANCIA>

<USO_PROYECTO>
Uso principal (Marco teórico / Metodología / Comparación / Múltiple) con breve justificación.
</USO_PROYECTO>

<CLASIFICACION_TIPO>
Tipo de artículo (Teórico / Empírico / Revisión Sistemática / Caso de Estudio / Propuesta Metodológica / Otro) con justificación breve.
</CLASIFICACION_TIPO>

<OBSERVACIONES>
Notas adicionales: idioma, dataset o código disponible, calidad de la fuente, acceso abierto o restringido.
</OBSERVACIONES>"""

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
