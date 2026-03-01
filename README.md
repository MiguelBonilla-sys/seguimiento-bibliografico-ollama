# Sistema de Seguimiento Bibliográfico con LLM Local

Sistema en Python que genera automáticamente documentos `.docx` de seguimiento bibliográfico a partir de un JSON con referencias académicas (DOI, arXiv, GitHub, web, PDF). Usa LLM local vía Ollama con detección automática de GPU/CPU.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Caso 1: Instalación inicial (primera vez)](#caso-1-instalación-inicial-primera-vez)
3. [Caso 2: Solo metadatos (sin LLM)](#caso-2-solo-metadatos-sin-llm)
4. [Caso 3: Análisis con LLM en CPU](#caso-3-análisis-con-llm-en-cpu)
5. [Caso 4: Análisis con LLM en GPU](#caso-4-análisis-con-llm-en-gpu)
6. [Formato del JSON de entrada](#formato-del-json-de-entrada)
7. [Opciones de línea de comandos](#opciones-de-línea-de-comandos)
8. [Estructura del proyecto](#estructura-del-proyecto)

---

## 1. Requisitos previos

| Requisito | Detalle |
|-----------|---------|
| Python | 3.11 o superior |
| Ollama | Solo para modos con LLM (casos 3 y 4) |
| Sistema | Windows 10/11 (22H2+) o Linux |
| RAM | 8 GB libres mínimo (20 GB recomendado para CPU) |
| GPU | Opcional — NVIDIA (CUDA) o AMD (ROCm) se detecta automáticamente |

---

## Caso 1: Instalación inicial (primera vez)

Pasos para dejar el proyecto listo la primera vez que lo usas.

### Paso 1.1 — Ir al directorio del proyecto

```powershell
cd C:\Users\tu_usuario\Documents\DEVs\BIBLIOGRAFIAS
```

*(En Linux: `cd /ruta/a/BIBLIOGRAFIAS`)*

### Paso 1.2 — Crear y activar el entorno virtual

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\activate
```

*(En Linux: `source .venv/bin/activate`)*

Deberías ver `(.venv)` al inicio del prompt.

### Paso 1.3 — Instalar dependencias de Python

```powershell
pip install -r requirements.txt
```

### Paso 1.4 — Instalar Ollama (solo si usarás LLM)

1. Descargar: https://ollama.com/download  
2. Instalar (Windows: `OllamaSetup.exe`)  
3. Descargar el modelo:

```powershell
ollama pull mistral
```

### Paso 1.5 — Configurar Ollama (recomendado)

**En Windows** (PowerShell como administrador o Variables de entorno del sistema):

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "1", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "1", "User")
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "5m", "User")
```

**En Linux** (añadir a `~/.bashrc` o `~/.profile`):

```bash
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=5m
```

Reinicia Ollama después de cambiar variables.

### Paso 1.6 — Verificar que todo funciona

```powershell
python main.py --input data/input/ejemplo_refs.json --modo sin_llm
```

Si se generan archivos en `data/output/`, la instalación es correcta.

---

## Caso 2: Solo metadatos (sin LLM)

Genera `.docx` con metadatos extraídos (CrossRef, OpenAlex, arXiv, GitHub, etc.) y placeholders en las secciones de análisis. **No requiere Ollama**.

### Paso 2.1 — Activar el entorno virtual

```powershell
cd C:\Users\tu_usuario\Documents\DEVs\BIBLIOGRAFIAS
.venv\Scripts\activate
```

### Paso 2.2 — Colocar tu JSON en `data/input/`

Ejemplo: `data/input/mis_refs.json`

### Paso 2.3 — Ejecutar

```powershell
python main.py --input data/input/mis_refs.json --modo sin_llm
```

### Paso 2.4 — Revisar resultados

Los `.docx` estarán en `data/output/`, nombrados por el campo `codigo` de cada entrada.

---

## Caso 3: Análisis con LLM en CPU

Genera documentos con análisis completo del LLM. Pensado para equipos sin GPU o cuando quieres forzar CPU.

### Paso 3.1 — Preajustes de Ollama para CPU

Variables de entorno (si no las configuraste en Caso 1):

```powershell
$env:OLLAMA_NUM_PARALLEL = "1"
$env:OLLAMA_MAX_LOADED_MODELS = "1"
$env:OLLAMA_KEEP_ALIVE = "5m"
```

*(En Linux: `export OLLAMA_NUM_PARALLEL=1` etc.)*

### Paso 3.2 — Comprobar que Ollama está corriendo

Ollama suele iniciarse como servicio. Si no:

```powershell
ollama serve
```

*(En otra terminal)*

### Paso 3.3 — Activar venv y ejecutar

```powershell
cd C:\Users\tu_usuario\Documents\DEVs\BIBLIOGRAFIAS
.venv\Scripts\activate
python main.py --input data/input/mis_refs.json --modo con_llm
```

Para forzar CPU aunque tengas GPU:

```powershell
python main.py --input data/input/mis_refs.json --modo con_llm --force-cpu
```

### Paso 3.4 — Tiempos orientativos

~2–4 minutos por documento en CPU. Para 35 referencias: ~1.5–2.5 horas.

---

## Caso 4: Análisis con LLM en GPU

Mismo flujo que el Caso 3, pero el sistema detecta la GPU y ajusta parámetros automáticamente (más contexto, menos tiempo).

### Paso 4.1 — Requisitos de GPU

- **NVIDIA**: drivers actualizados, CUDA instalado  
- **AMD**: ROCm (Linux)  
- El sistema usa `nvidia-smi` o `rocm-smi` para detectar la GPU

### Paso 4.2 — Comprobar que Ollama ve la GPU

```powershell
ollama run mistral "Hola"
```

Si responde sin errores, Ollama está usando la GPU.

### Paso 4.3 — Activar venv y ejecutar

```powershell
cd C:\Users\tu_usuario\Documents\DEVs\BIBLIOGRAFIAS
.venv\Scripts\activate
python main.py --input data/input/mis_refs.json --modo con_llm
```

No hace falta `--force-cpu`; el sistema detecta la GPU y aplica `num_gpu=99`, `num_ctx=4096–8192`, timeout 2 min.

### Paso 4.4 — Tiempos orientativos

~30–90 segundos por documento en GPU (según modelo y VRAM).

---

## Formato del JSON de entrada

```json
[
  {
    "codigo": "SB-REV-01",
    "url": "https://doi.org/10.1016/j.compeleceng.2024.109625",
    "base_datos": "ScienceDirect"
  },
  {
    "codigo": "SB-REV-21",
    "url": "https://arxiv.org/abs/2405.11619",
    "base_datos": "arXiv"
  }
]
```

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `codigo` | Sí | Identificador único (ej. SB-REV-01) |
| `url` | Sí | DOI, arXiv, GitHub, web o PDF |
| `base_datos` | No | Origen (ScienceDirect, IEEE, arXiv, etc.) |

**Tipos de URL soportados**: DOI, arXiv, GitHub, páginas web, PDFs remotos.

---

## Opciones de línea de comandos

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--input`, `-i` | Ruta al JSON de entrada | (requerido) |
| `--output`, `-o` | Directorio de salida | `data/output/` |
| `--modo`, `-m` | `sin_llm` o `con_llm` | `sin_llm` |
| `--modelo` | Modelo de Ollama | `mistral` |
| `--proyecto` | Contexto de tu proyecto | (genérico) |
| `--force-cpu` | Forzar CPU aunque haya GPU | desactivado |

**Ejemplos:**

```powershell
python main.py -i data/input/refs.json -m con_llm --modelo phi3:mini
python main.py -i data/input/refs.json -m con_llm -o C:\Salida
python main.py -i data/input/refs.json -m con_llm --proyecto "Mi tesis sobre phishing"
```

---

## Estructura del documento generado

Cada `.docx` incluye:

1. **Datos Generales** — código, base de datos, DOI/URL  
2. **Referencia Bibliográfica** — formato IEEE  
3. **Información del Documento** — título, autores, año, abstract  
4. **Análisis del Contenido** — problema, metodología, resultados, aportes, limitaciones  
5. **Relación con mi Proyecto**  
6. **Clasificación del Artículo**

---

## Estructura del proyecto

```
BIBLIOGRAFIAS/
├── config/settings.py          — Configuración
├── core/
│   ├── metadata_extractor.py   — DOI, arXiv, GitHub, web, PDF
│   ├── pdf_extractor.py        — Extracción de abstract
│   ├── llm_analyzer.py         — Ollama (GPU/CPU auto)
│   └── document_generator.py   — Generación .docx
├── templates/prompts.py        — Prompts académicos
├── utils/
│   ├── helpers.py              — Logging, timing
│   └── gpu_detection.py        — Detección GPU
├── data/input/                 — JSONs de entrada
├── data/output/                — Documentos generados
├── logs/                       — Logs de ejecución
├── main.py                     — Punto de entrada
└── requirements.txt
```

---

## Modelos recomendados

| Modelo | RAM/VRAM | Uso |
|--------|----------|-----|
| `mistral` | ~4.5 GB | Recomendado |
| `phi3:mini` | ~2.2 GB | Más rápido en CPU |
| `llama3:8b` | ~5 GB | Mejor calidad, más lento |
