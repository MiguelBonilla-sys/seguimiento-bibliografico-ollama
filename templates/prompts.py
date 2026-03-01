"""
Plantillas de prompts académicos optimizados para análisis bibliográfico.
Diseñados para minimizar tokens de salida y facilitar el parsing.
"""

ANALYSIS_SYSTEM_PROMPT = (
    "Eres un asistente académico especializado en análisis de literatura científica. "
    "Responde siempre en español. Sé conciso: máximo 3-4 oraciones por sección. "
    "Usa EXACTAMENTE las etiquetas de tipo XML indicadas (por ejemplo <PROBLEMA>...</PROBLEMA>). "
    "IMPORTANTE: Si no hay abstract, INFIERE el contenido a partir del título, los autores, "
    "la revista y el contexto del proyecto. Nunca respondas 'No disponible' si puedes deducir "
    "algo razonable del título o los metadatos. "
    "Nunca cambies, elimines ni renombres ninguna etiqueta."
)

ANALYSIS_USER_PROMPT = """Analiza el siguiente artículo académico y completa TODAS las 12 secciones sin excepción.
Responde ÚNICAMENTE usando las etiquetas XML mostradas. Escribe 2-3 oraciones por sección para que cada idea se entienda bien.
Si el abstract no está disponible, INFIERE y DEDUCE el contenido de cada sección a partir del título, autores, revista y contexto del proyecto. No dejes secciones vacías ni escribas 'No disponible'.
IMPORTANTE: debes completar TODAS las 12 secciones obligatoriamente.

--- DATOS DEL ARTÍCULO ---
Título: {titulo}
Autores: {autores}
Año: {anio}
Revista/Conferencia: {journal}
Base de datos: {base_datos}

--- ABSTRACT / CONTENIDO ---
{abstract}

--- CONTEXTO DEL PROYECTO (úsalo para las secciones de relación y clasificación) ---
{proyecto_context}

--- FORMATO DE RESPUESTA (respeta exactamente estas 12 etiquetas y su orden) ---

<PROBLEMA>
Describe el problema central que aborda el artículo en 2-3 oraciones.
</PROBLEMA>

<METODOLOGIA>
Describe la metodología o enfoque utilizado en 2-3 oraciones.
</METODOLOGIA>

<RESULTADOS>
Resume los resultados principales obtenidos en 2-3 oraciones.
</RESULTADOS>

<APORTES>
Identifica los aportes más relevantes del artículo en 2-3 oraciones.
</APORTES>

<LIMITACIONES>
Señala las limitaciones identificadas o reconocidas en 2-3 oraciones.
</LIMITACIONES>

<RELACION_CONEXION>
¿Cómo se conecta este artículo con el problema del proyecto? Sé específico en 2-3 oraciones.
</RELACION_CONEXION>

<RELACION_REUTILIZAR>
¿Qué técnicas, modelos, datasets o marcos teóricos se pueden reutilizar en el proyecto? 2-3 oraciones.
</RELACION_REUTILIZAR>

<RELACION_DIFERENCIA>
¿En qué se diferencia o mejora la propuesta del proyecto respecto a este artículo? 2-3 oraciones.
</RELACION_DIFERENCIA>

<NIVEL_RELEVANCIA>
Alta, Media o Baja. Justifica en 1-2 oraciones.
</NIVEL_RELEVANCIA>

<USO_PROYECTO>
Marco teórico, Metodología, Comparación o Múltiple. Justifica en 1-2 oraciones.
</USO_PROYECTO>

<CLASIFICACION_TIPO>
Teórico, Empírico, Revisión Sistemática, Caso de Estudio, Propuesta Metodológica u Otro. Justifica en 1-2 oraciones.
</CLASIFICACION_TIPO>

<OBSERVACIONES>
Notas sobre idioma, disponibilidad de dataset/código, calidad de la fuente, acceso. 2-3 oraciones.
</OBSERVACIONES>"""

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
Autores: Johan Camilo Mesa Rios, Javier Mauricio Plata Párraga
Asesor: Yeison Eduardo Conejo Sandoval

TÍTULO:
Sistema de Gestión de RRHH con IA para startups colombianas:
optimización y cumplimiento normativo.

PROBLEMA QUE RESUELVE:
Las startups colombianas enfrentan ineficiencias críticas en la gestión de recursos humanos
debido a procesos manuales, sistemas desconectados y dificultades para cumplir normativas
como la Ley 1581 de 2012 y las exigencias de la UGPP. Esto genera errores en nómina,
problemas de seguridad de datos y sesgos en la selección de personal que afectan a grupos
históricamente desfavorecidos. Adicionalmente, el 67% de las organizaciones colombianas
usan procesos manuales en al menos una operación de RRHH, y el 74% reporta dificultades
para encontrar talento adecuado. Las soluciones actuales no están integradas ni adaptadas
a las particularidades culturales y económicas del mercado colombiano emergente.

PREGUNTA DE INVESTIGACIÓN:
¿Cómo puede la implementación de inteligencia artificial mejorar la eficiencia en los
procesos de selección de personal y administración de nómina en empresas colombianas,
y qué barreras tecnológicas y culturales enfrentan para su adopción?

OBJETIVO GENERAL:
Diseñar un sistema de inteligencia artificial para los procesos de selección de personal
en empresas colombianas, evaluando su impacto en la eficiencia operativa y la calidad
de las contrataciones.

OBJETIVOS ESPECÍFICOS:
- Evaluar el uso de herramientas de IA en la selección de personal en empresas colombianas,
  identificando ventajas y desafíos percibidos por profesionales de RRHH.
- Examinar la relación entre automatización del proceso de selección y la reducción de
  tiempos y costos en contratación.
- Determinar el impacto de la IA en la eliminación de sesgos, mejorando la equidad en
  la toma de decisiones.
- Proponer estrategias para la integración efectiva de IA en prácticas de RRHH basadas
  en los resultados obtenidos.

COMPONENTES CLAVE DEL SISTEMA:
- Selección de Personal: Algoritmos de IA para análisis y preselección de currículos,
  automatización de programación de entrevistas y análisis de competencias.
- Administración de Nómina: Sistema de IA para gestión automatizada con cumplimiento
  normativo, precisión en pagos y protección de datos (Ley 1581 de 2012).
- Cumplimiento Normativo: Garantía de cumplimiento de normativas laborales y de
  protección de datos colombianas (UGPP, Superintendencia de Industria y Comercio).
- Optimización de Procesos: Reducción de tiempos operativos y mejora en toma de
  decisiones mediante herramientas analíticas basadas en IA.

TÉCNICAS Y ENFOQUE TÉCNICO:
- Machine Learning: clasificación y preselección de currículos, análisis de candidatos.
- Procesamiento de Lenguaje Natural (PLN): análisis semántico de perfiles y competencias.
- Algoritmos anti-sesgo: reducción de discriminación por género, etnia o edad.
- Metodología mixta (cuali-cuantitativa): análisis organizacional + validación de KPIs.
- Scrum (desarrollo ágil): iteración continua con retroalimentación del usuario.
- Análisis de datos: indicadores de eficiencia, precisión en nómina y cumplimiento normativo.

TECNOLOGÍAS PRINCIPALES:
- Plataforma: SaaS en la nube
- Módulo de selección: algoritmos de ML + PLN
- Módulo de nómina: automatización con cumplimiento normativo
- Integración con: SAP, Workday, Microsoft Teams y otras plataformas de gestión

LIMITACIONES DEL PROYECTO:
- Enfoque exclusivo en startups colombianas; no contempla grandes corporaciones
  ni empresas fuera de Colombia.
- Sujeto a la infraestructura tecnológica existente en cada startup, pudiendo requerir
  actualizaciones o adaptaciones previas.
- Enfrenta barreras culturales de resistencia al cambio dentro de las organizaciones.
- Riesgo de discriminación algorítmica si los datos de entrenamiento contienen sesgos
  preexistentes.
- Falta de regulación jurídica clara sobre IA en contratación laboral en Colombia.
- Dependencia de conectividad y adopción tecnológica por parte de las empresas objetivo.
- Generalización limitada: validado en el contexto colombiano; resultados pueden no
  ser directamente transferibles a otros mercados.

USUARIOS FINALES:
- Profesionales de RRHH en startups: automatizan selección de personal y nómina.
- Candidatos y empleados: beneficiarios de procesos más equitativos y precisos.
- Administradores y gerentes: toman decisiones estratégicas con dashboards analíticos.
- Área legal/compliance: monitorean cumplimiento normativo (Ley 1581, UGPP)."""