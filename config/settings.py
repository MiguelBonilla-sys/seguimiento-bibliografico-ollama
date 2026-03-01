"""
Configuración centralizada del sistema de seguimiento bibliográfico.
Todos los parámetros ajustables están aquí para facilitar mantenimiento.
"""

import os
from pathlib import Path

# --- Rutas del proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_INPUT_DIR = BASE_DIR / "data" / "input"
DATA_OUTPUT_DIR = BASE_DIR / "data" / "output"
LOGS_DIR = BASE_DIR / "logs"

# --- Ollama / LLM ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = 0.3
LLM_TOP_P = 0.9
LLM_REPEAT_PENALTY = 1.1
LLM_NUM_THREAD = os.cpu_count() or 4  # cores lógicos; Ollama usa físicos internamente
LLM_MAX_OUTPUT_TOKENS = 1024

# Valores por defecto CPU (se sobrescriben si se detecta GPU)
LLM_NUM_CTX = 2048
LLM_REQUEST_TIMEOUT = 600  # segundos (10 min en CPU; 2 min en GPU)
LLM_NUM_GPU = None  # None = auto; 99 = todas las capas en GPU

# --- Límites de texto ---
MAX_INPUT_WORDS = 1500
MAX_ABSTRACT_WORDS = 800

# --- APIs de metadatos ---
CROSSREF_BASE_URL = "https://api.crossref.org/works"
CROSSREF_MAILTO = os.getenv("CROSSREF_MAILTO", "")  # email opcional para polite pool
OPENALEX_BASE_URL = "https://api.openalex.org/works"
OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "")
API_TIMEOUT = 15  # segundos
API_MAX_RETRIES = 3
API_BACKOFF_FACTOR = 2  # segundos base para backoff exponencial

# --- PDF ---
PDF_MAX_PAGES = 2  # solo las primeras N páginas para abstract

# --- Monitoreo ---
MEMORY_CHECK_INTERVAL = 10  # cada N documentos, verificar RSS
MEMORY_ALERT_THRESHOLD_MB = 500  # alerta si crece más de esto desde el inicio

# --- Documento de salida ---
DOCX_FONT_NAME = "Calibri"
DOCX_FONT_SIZE_NORMAL = 11
DOCX_FONT_SIZE_HEADING1 = 14
DOCX_FONT_SIZE_HEADING2 = 12

# Placeholder para modo sin_llm
PLACEHOLDER_TEXT = "[Pendiente de análisis con LLM]"
