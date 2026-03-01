"""
Punto de entrada del sistema de seguimiento bibliográfico.
Procesa un JSON de referencias y genera documentos .docx individuales.

Uso:
    python main.py --input data/input/refs.json --modo con_llm
    python main.py --input data/input/refs.json --modo sin_llm
    python main.py --input data/input/refs.json --modo con_llm --modelo phi3:mini
"""

import argparse
import json
import sys
import time
from pathlib import Path

from config.settings import DATA_OUTPUT_DIR, LLM_MODEL, MEMORY_CHECK_INTERVAL
from core.document_generator import generate_docx
from core.llm_analyzer import (
    analyze_document,
    check_ollama_available,
    set_force_cpu,
    warmup_model,
)
from core.metadata_extractor import extract_metadata
from utils.gpu_detection import detect_gpu
from utils.helpers import (
    check_memory,
    force_gc,
    get_memory_mb,
    setup_logger,
    timer,
)


def load_input(path: str | Path) -> list[dict]:
    """Carga y valida el JSON de entrada."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("El JSON debe contener una lista de objetos")
    for i, item in enumerate(data):
        if "codigo" not in item or "url" not in item:
            raise ValueError(
                f"Entrada {i}: debe tener campos 'codigo' y 'url'"
            )
    return data


def process_single(
    entry: dict,
    modo: str,
    modelo: str,
    output_dir: Path,
    proyecto_context: str,
    logger,
) -> dict:
    """
    Procesa una entrada individual: metadatos -> [LLM] -> .docx
    Retorna dict con resultado y tiempos.
    """
    codigo = entry["codigo"]
    url = entry["url"]
    base_datos = entry.get("base_datos", "")
    result = {"codigo": codigo, "ok": False, "error": "", "times": {}}

    # Fase 1: Extracción de metadatos
    with timer(f"  Metadatos {codigo}", logger):
        t0 = time.perf_counter()
        metadata = extract_metadata(url, base_datos)
        result["times"]["metadata"] = time.perf_counter() - t0

    if metadata.get("error"):
        logger.warning("  Metadatos incompletos: %s", metadata["error"])

    # Fase 2: Análisis LLM (solo en modo con_llm)
    analysis = None
    if modo == "con_llm":
        abstract = metadata.get("abstract", "")
        if not abstract:
            logger.info("  Sin abstract disponible para LLM")

        with timer(f"  LLM {codigo}", logger):
            t0 = time.perf_counter()
            analysis = analyze_document(
                metadata, abstract, proyecto_context, modelo
            )
            result["times"]["llm"] = time.perf_counter() - t0

        if analysis.get("_error"):
            logger.warning("  Error LLM: %s", analysis["_error"])

    # Fase 3: Generación de documento
    with timer(f"  DOCX {codigo}", logger):
        t0 = time.perf_counter()
        output_path = generate_docx(metadata, analysis, codigo, output_dir)
        result["times"]["docx"] = time.perf_counter() - t0

    result["ok"] = True
    result["output"] = str(output_path)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Seguimiento Bibliográfico con LLM Local"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Ruta al archivo JSON de entrada",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=f"Directorio de salida (default: {DATA_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--modo", "-m",
        choices=["sin_llm", "con_llm"],
        default="sin_llm",
        help="Modo de ejecución (default: sin_llm)",
    )
    parser.add_argument(
        "--modelo",
        default=None,
        help=f"Modelo de Ollama a usar (default: {LLM_MODEL})",
    )
    parser.add_argument(
        "--proyecto",
        default="",
        help="Contexto del proyecto para el análisis LLM",
    )
    parser.add_argument(
        "--force-cpu",
        action="store_true",
        help="Forzar modo CPU aunque se detecte GPU",
    )
    parser.add_argument(
        "--solo",
        default=None,
        help="Procesar únicamente el documento con este código (ej: SB-REV-02)",
    )
    args = parser.parse_args()

    logger = setup_logger()
    output_dir = Path(args.output) if args.output else DATA_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    modelo = args.modelo or LLM_MODEL

    logger.info("=" * 60)
    logger.info("SISTEMA DE SEGUIMIENTO BIBLIOGRÁFICO")
    logger.info("=" * 60)
    logger.info("Modo: %s", args.modo)
    logger.info("Modelo: %s", modelo if args.modo == "con_llm" else "N/A")
    logger.info("Salida: %s", output_dir)

    if args.force_cpu and args.modo == "con_llm":
        set_force_cpu(True)
    elif args.modo == "con_llm":
        gpu_info = detect_gpu()
        if gpu_info.disponible:
            logger.info(
                "GPU detectada: %s %s (%d MB VRAM)",
                gpu_info.fabricante.upper(),
                gpu_info.nombre,
                gpu_info.vram_mb,
            )

    # Cargar entrada
    try:
        entries = load_input(args.input)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Error cargando JSON: %s", e)
        sys.exit(1)

    if args.solo:
        entries = [e for e in entries if e["codigo"] == args.solo]
        if not entries:
            logger.error("Código '%s' no encontrado en el JSON de entrada", args.solo)
            sys.exit(1)
        logger.info("Filtro --solo: procesando únicamente '%s'", args.solo)

    total = len(entries)
    logger.info("Documentos a procesar: %d", total)

    # Verificar Ollama si es modo con_llm
    if args.modo == "con_llm":
        if not check_ollama_available(modelo):
            logger.error(
                "Ollama no disponible o modelo '%s' no instalado. "
                "Ejecuta: ollama pull %s",
                modelo,
                modelo,
            )
            sys.exit(1)
        logger.info("Ollama verificado: modelo '%s' disponible", modelo)
        warmup_model(modelo)

    # Procesar secuencialmente
    baseline_mb = get_memory_mb()
    logger.info("Memoria inicial: %.1f MB", baseline_mb)
    start_total = time.perf_counter()

    results = []
    ok_count = 0
    error_count = 0

    for idx, entry in enumerate(entries, 1):
        codigo = entry["codigo"]
        logger.info("-" * 40)
        logger.info("[%d/%d] Procesando: %s", idx, total, codigo)

        doc_start = time.perf_counter()
        try:
            result = process_single(
                entry, args.modo, modelo, output_dir, args.proyecto, logger
            )
            if result["ok"]:
                ok_count += 1
            else:
                error_count += 1
        except Exception as e:
            logger.error("Error inesperado procesando %s: %s", codigo, e)
            result = {"codigo": codigo, "ok": False, "error": str(e)}
            error_count += 1

        doc_elapsed = time.perf_counter() - doc_start
        status = "OK" if result.get("ok") else "ERROR"
        logger.info("[%d/%d] %s — %s (%.1fs)", idx, total, codigo, status, doc_elapsed)

        results.append(result)

        # Liberar memoria y verificar periódicamente
        force_gc()
        if idx % MEMORY_CHECK_INTERVAL == 0:
            check_memory(baseline_mb, logger, idx)

    # Reporte final
    total_elapsed = time.perf_counter() - start_total
    final_mb = get_memory_mb()

    logger.info("=" * 60)
    logger.info("REPORTE FINAL")
    logger.info("=" * 60)
    logger.info("Total procesados: %d", total)
    logger.info("Exitosos: %d", ok_count)
    logger.info("Con errores: %d", error_count)
    logger.info("Tiempo total: %.1fs", total_elapsed)
    if ok_count > 0:
        logger.info("Tiempo promedio/doc: %.1fs", total_elapsed / total)
    logger.info("Memoria final: %.1f MB (inicio: %.1f MB)", final_mb, baseline_mb)
    logger.info("Documentos en: %s", output_dir)

    if error_count > 0:
        logger.info("Documentos con error:")
        for r in results:
            if not r.get("ok"):
                logger.info("  - %s: %s", r["codigo"], r.get("error", ""))

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
