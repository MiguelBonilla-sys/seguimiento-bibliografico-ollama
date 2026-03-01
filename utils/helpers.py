"""
Utilidades transversales: logging, medición de tiempo y monitoreo de memoria.
"""

import gc
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import psutil

from config.settings import LOGS_DIR, MEMORY_ALERT_THRESHOLD_MB


def setup_logger(name: str = "bibliografias") -> logging.Logger:
    """Configura y devuelve un logger con salida a consola y archivo."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"run_{timestamp}.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    logger.info("Log iniciado: %s", log_file)
    return logger


@contextmanager
def timer(label: str, logger: logging.Logger | None = None):
    """Context manager que mide y reporta tiempo de ejecución."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    msg = f"{label}: {elapsed:.2f}s"
    if logger:
        logger.info(msg)
    else:
        print(msg)


def get_memory_mb() -> float:
    """Devuelve la memoria RSS del proceso actual en MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def check_memory(
    baseline_mb: float, logger: logging.Logger, doc_index: int
) -> None:
    """
    Verifica el crecimiento de memoria respecto a la baseline.
    Emite una alerta si supera el umbral configurado.
    """
    current_mb = get_memory_mb()
    delta = current_mb - baseline_mb
    logger.info(
        "Memoria [doc %d]: %.1f MB (delta: %+.1f MB)",
        doc_index,
        current_mb,
        delta,
    )
    if delta > MEMORY_ALERT_THRESHOLD_MB:
        logger.warning(
            "ALERTA: crecimiento de memoria excede %d MB (delta=%.1f MB)",
            MEMORY_ALERT_THRESHOLD_MB,
            delta,
        )


def force_gc() -> None:
    """Fuerza recolección de basura para liberar memoria."""
    gc.collect()


def truncate_text(text: str, max_words: int) -> str:
    """Trunca texto al número máximo de palabras indicado."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " [...]"
