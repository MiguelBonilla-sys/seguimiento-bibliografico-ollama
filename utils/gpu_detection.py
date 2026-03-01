"""
Detección de GPU y VRAM disponible para optimizar parámetros del LLM.
Soporta NVIDIA (nvidia-smi) y AMD (rocm-smi en Linux).
"""

import logging
import subprocess
import sys
from dataclasses import dataclass

logger = logging.getLogger("bibliografias")


@dataclass
class GPUInfo:
    """Información detectada sobre la GPU."""
    disponible: bool
    fabricante: str  # "nvidia", "amd", ""
    vram_mb: int
    nombre: str


def detect_gpu() -> GPUInfo:
    """
    Detecta si hay GPU disponible y cuánta VRAM tiene.
    Retorna GPUInfo con disponibilidad, fabricante, VRAM en MB y nombre.
    """
    # 1. Intentar nvidia-smi (NVIDIA)
    nvidia_info = _detect_nvidia_gpu()
    if nvidia_info:
        return nvidia_info

    # 2. Intentar rocm-smi (AMD, típicamente Linux)
    amd_info = _detect_amd_gpu()
    if amd_info:
        return amd_info

    return GPUInfo(
        disponible=False,
        fabricante="",
        vram_mb=0,
        nombre="",
    )


def _detect_nvidia_gpu() -> GPUInfo | None:
    """Detecta GPU NVIDIA vía nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        lines = result.stdout.strip().split("\n")
        first_line = lines[0]
        parts = first_line.split(",", 1)
        if len(parts) < 2:
            return None

        name = parts[0].strip()
        vram_str = parts[1].strip().split()[0]
        try:
            vram_mb = int(float(vram_str))
        except ValueError:
            vram_mb = 0

        logger.info("GPU NVIDIA detectada: %s (%d MB VRAM)", name, vram_mb)
        return GPUInfo(
            disponible=True,
            fabricante="nvidia",
            vram_mb=vram_mb,
            nombre=name,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        logger.debug("nvidia-smi no disponible: %s", e)
        return None


def _detect_amd_gpu() -> GPUInfo | None:
    """Detecta GPU AMD vía rocm-smi (Linux)."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showmeminfo", "vram", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None

        import json
        data = json.loads(result.stdout)
        # Estructura varía; simplificado
        vram_mb = 0
        for key, val in data.items():
            if "vram" in key.lower() and isinstance(val, (int, float)):
                vram_mb = max(vram_mb, int(val) // (1024 * 1024))

        if vram_mb > 0:
            logger.info("GPU AMD detectada (%d MB VRAM)", vram_mb)
            return GPUInfo(
                disponible=True,
                fabricante="amd",
                vram_mb=vram_mb,
                nombre="AMD GPU",
            )
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return None


def get_llm_options_for_hardware(gpu_info: GPUInfo) -> dict:
    """
    Retorna opciones óptimas para Ollama según el hardware detectado.
    - Con GPU: num_gpu=99 (todas las capas en GPU), num_ctx mayor, timeout menor
    - Sin GPU: num_ctx reducido, sin num_gpu (Ollama usa CPU)
    """
    if gpu_info.disponible and gpu_info.vram_mb >= 4096:
        # GPU con al menos 4 GB VRAM
        if gpu_info.vram_mb >= 12000:
            num_ctx = 8192
        elif gpu_info.vram_mb >= 8000:
            num_ctx = 4096
        else:
            num_ctx = 4096

        return {
            "num_gpu": 99,
            "num_ctx": num_ctx,
            "timeout": 120,
            "modo": "gpu",
        }
    else:
        return {
            "num_gpu": None,
            "num_ctx": 2048,
            "timeout": 900,
            "modo": "cpu",
        }
