"""
Extracción ligera de abstracts desde PDFs académicos usando PyMuPDF.
Solo carga las primeras páginas para minimizar uso de memoria.
"""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF

from config.settings import MAX_ABSTRACT_WORDS, PDF_MAX_PAGES

logger = logging.getLogger("bibliografias")

# Patrones comunes para detectar inicio y fin del abstract
_ABSTRACT_START = re.compile(
    r"\b(abstract|resumen|summary)\b", re.IGNORECASE
)
_ABSTRACT_END = re.compile(
    r"\b(keywords?|palabras\s*clave|introduction|1\.\s*introduction"
    r"|index\s*terms|i\.\s*introduction)\b",
    re.IGNORECASE,
)


def extract_abstract_from_pdf(pdf_path: str | Path) -> str:
    """
    Extrae el abstract de un PDF académico.
    Solo lee las primeras páginas para ahorrar memoria.
    Retorna string vacío si no encuentra abstract.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        logger.warning("PDF no encontrado: %s", pdf_path)
        return ""

    doc = None
    try:
        doc = fitz.open(str(pdf_path))
        max_pages = min(PDF_MAX_PAGES, len(doc))

        full_text = ""
        for page_num in range(max_pages):
            page = doc[page_num]
            full_text += page.get_text("text") + "\n"

        abstract = _find_abstract_section(full_text)
        if abstract:
            return _truncate_words(abstract, MAX_ABSTRACT_WORDS)

        # Si no se detecta sección explícita, devolver primeros párrafos
        logger.info("Abstract no detectado por patrón, usando texto inicial")
        return _truncate_words(full_text.strip(), MAX_ABSTRACT_WORDS)

    except Exception as e:
        logger.error("Error extrayendo abstract de %s: %s", pdf_path, e)
        return ""
    finally:
        if doc is not None:
            doc.close()


def _find_abstract_section(text: str) -> str:
    """Localiza y extrae la sección de abstract del texto completo."""
    start_match = _ABSTRACT_START.search(text)
    if not start_match:
        return ""

    # Texto después de la palabra "Abstract"
    after_abstract = text[start_match.end():]

    # Limpiar separadores comunes (guiones, dos puntos, saltos de línea)
    after_abstract = re.sub(r"^[\s:\-—]+", "", after_abstract)

    end_match = _ABSTRACT_END.search(after_abstract)
    if end_match:
        abstract = after_abstract[:end_match.start()]
    else:
        # Sin marcador de fin: tomar los primeros ~500 palabras
        abstract = after_abstract

    # Limpiar saltos de línea internos del PDF (columnas, etc.)
    abstract = re.sub(r"\n(?!\n)", " ", abstract)
    abstract = re.sub(r"\n{2,}", "\n", abstract)
    return abstract.strip()


def _truncate_words(text: str, max_words: int) -> str:
    """Trunca texto al número de palabras indicado."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
