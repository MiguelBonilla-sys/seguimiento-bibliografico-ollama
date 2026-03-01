"""
Integración con Ollama para análisis de documentos académicos vía LLM local.
Comunicación por HTTP REST — sin dependencias de SDK pesados.
Detecta GPU/VRAM automáticamente y ajusta parámetros para máximo rendimiento.
"""

import json
import logging
import re
from typing import Any

import requests

from config.settings import (
    LLM_MAX_OUTPUT_TOKENS,
    LLM_MODEL,
    LLM_REPEAT_PENALTY,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    OLLAMA_BASE_URL,
)
from templates.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT,
    DEFAULT_PROJECT_CONTEXT,
    EXPECTED_SECTIONS,
)
from utils.gpu_detection import detect_gpu, get_llm_options_for_hardware
from utils.helpers import truncate_text

logger = logging.getLogger("bibliografias")

_NOT_AVAILABLE = "No disponible"

# Cache de detección de hardware (se evalúa una sola vez)
_hardware_options: dict | None = None
_force_cpu: bool = False


def set_force_cpu(force: bool = True) -> None:
    """Fuerza modo CPU aunque se detecte GPU (ej: --force-cpu)."""
    global _force_cpu, _hardware_options
    _force_cpu = force
    _hardware_options = None  # invalidar cache para re-evaluar


def _get_hardware_options() -> dict:
    """Obtiene opciones óptimas según GPU/CPU (cacheado)."""
    global _hardware_options
    if _hardware_options is None:
        if _force_cpu:
            _hardware_options = {
                "num_gpu": None,
                "num_ctx": 2048,
                "timeout": 600,
                "modo": "cpu",
            }
            logger.info("Modo CPU forzado (--force-cpu)")
        else:
            gpu_info = detect_gpu()
            _hardware_options = get_llm_options_for_hardware(gpu_info)
        logger.info(
            "Hardware: %s (num_ctx=%d, timeout=%ds)",
            _hardware_options["modo"].upper(),
            _hardware_options["num_ctx"],
            _hardware_options["timeout"],
        )
    return _hardware_options


def check_ollama_available(model: str | None = None) -> bool:
    """Verifica que Ollama esté corriendo y el modelo esté disponible."""
    model = model or LLM_MODEL
    try:
        resp = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags", timeout=10
        )
        resp.raise_for_status()
        tags = resp.json()
        resp.close()
        available = [m["name"] for m in tags.get("models", [])]
        if not any(model in name for name in available):
            logger.error(
                "Modelo '%s' no encontrado. Disponibles: %s",
                model,
                available,
            )
            return False
        return True
    except requests.exceptions.RequestException as e:
        logger.error("Ollama no disponible en %s: %s", OLLAMA_BASE_URL, e)
        return False


def warmup_model(model: str | None = None) -> None:
    """Precarga el modelo en RAM/VRAM enviando un prompt trivial."""
    model = model or LLM_MODEL
    opts = _get_hardware_options()
    timeout = opts["timeout"]
    logger.info(
        "Precargando modelo '%s' en %s (timeout %ds)...",
        model,
        opts["modo"].upper(),
        timeout,
    )
    try:
        options = {"num_ctx": 64, "num_predict": 1}
        if opts.get("num_gpu") is not None:
            options["num_gpu"] = opts["num_gpu"]
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": "Hola", "stream": False, "options": options},
            timeout=timeout,
        )
        resp.raise_for_status()
        resp.close()
        logger.info("Modelo precargado exitosamente")
    except requests.exceptions.RequestException as e:
        logger.warning("Warmup falló (no es crítico): %s", e)


def analyze_document(
    metadata: dict[str, Any],
    abstract: str,
    proyecto_context: str = "",
    model: str | None = None,
) -> dict[str, str]:
    """
    Envía el abstract y metadatos al LLM y devuelve análisis estructurado.
    Retorna dict con las secciones parseadas o campos vacíos si falla.
    """
    model = model or LLM_MODEL
    proyecto_context = proyecto_context or DEFAULT_PROJECT_CONTEXT

    # Construir texto de entrada truncado
    autores_str = ", ".join(metadata.get("autores", [])) or _NOT_AVAILABLE
    abstract_truncated = truncate_text(abstract, 800) if abstract else _NOT_AVAILABLE

    user_prompt = ANALYSIS_USER_PROMPT.format(
        titulo=metadata.get("titulo", _NOT_AVAILABLE),
        autores=autores_str,
        anio=metadata.get("anio", _NOT_AVAILABLE),
        journal=metadata.get("journal", _NOT_AVAILABLE),
        base_datos=metadata.get("base_datos", "No especificada"),
        abstract=abstract_truncated,
        proyecto_context=proyecto_context,
    )

    opts = _get_hardware_options()
    options = {
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
        "repeat_penalty": LLM_REPEAT_PENALTY,
        "num_ctx": opts["num_ctx"],
        "num_predict": LLM_MAX_OUTPUT_TOKENS,
    }
    if opts.get("num_gpu") is not None:
        options["num_gpu"] = opts["num_gpu"]

    payload = {
        "model": model,
        "prompt": user_prompt,
        "system": ANALYSIS_SYSTEM_PROMPT,
        "stream": False,
        "options": options,
    }

    timeout = opts["timeout"]
    try:
        logger.info("Enviando a LLM (%s) [%s]...", model, opts["modo"].upper())
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        result = resp.json()
        resp.close()

        raw_response = result.get("response", "")
        if not raw_response:
            logger.warning("LLM devolvió respuesta vacía")
            return _empty_analysis("Respuesta vacía del LLM")

        logger.info(
            "LLM respondió: %d tokens generados, %.1fs",
            result.get("eval_count", 0),
            result.get("total_duration", 0) / 1e9,
        )

        return _parse_sections(raw_response)

    except requests.exceptions.Timeout:
        logger.error("Timeout (%ds) esperando respuesta del LLM", timeout)
        return _empty_analysis("Timeout del LLM")
    except requests.exceptions.RequestException as e:
        logger.error("Error de conexión con Ollama: %s", e)
        return _empty_analysis(f"Error de conexión: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Error parseando respuesta del LLM: %s", e)
        return _empty_analysis(f"Error de parsing: {e}")


def _parse_sections(raw: str) -> dict[str, str]:
    """Parsea la respuesta del LLM extrayendo contenido entre etiquetas XML."""
    result: dict[str, str] = {}
    for section in EXPECTED_SECTIONS:
        # Etiquetas XML: <SECCION>...</SECCION>
        pattern = rf"<{section}>\s*(.*?)\s*</{section}>"
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        result[section] = match.group(1).strip() if match else ""

    missing = [s for s in EXPECTED_SECTIONS if not result[s]]
    if missing:
        logger.warning("Secciones faltantes en respuesta LLM: %s", missing)

    result["_raw"] = raw
    result["_error"] = ""
    return result


def _empty_analysis(error_msg: str) -> dict[str, str]:
    """Retorna dict de análisis con todos los campos vacíos y el error."""
    result = dict.fromkeys(EXPECTED_SECTIONS, "")
    result["_raw"] = ""
    result["_error"] = error_msg
    return result
