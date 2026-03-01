# Diagnóstico y activación de GPU para Ollama

## Paso 1 — Confirmar que tienes GPU NVIDIA

```powershell
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM
```

---

## Paso 2 — Encontrar dónde está nvidia-smi.exe

```powershell
Get-ChildItem C:\ -Recurse -Filter "nvidia-smi.exe" -ErrorAction SilentlyContinue | Select-Object FullName
```

> Si aparece una ruta, anótala. Normalmente es:
> `C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe`

---

## Paso 3 — Agregar nvidia-smi al PATH del sistema (ejecutar como Administrador)

Reemplaza la ruta por la que encontraste en el paso 2:

```powershell
$ruta = "C:\Program Files\NVIDIA Corporation\NVSMI"
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ruta", "Machine")
```

Luego **cierra y vuelve a abrir** PowerShell y verifica:

```powershell
nvidia-smi
```

---

## Paso 4 — Verificar que Ollama usa la GPU

```powershell
ollama run mistral "Hola"
```

En otra terminal, mientras corre:

```powershell
nvidia-smi
```

En la columna `GPU-Util` debe aparecer un porcentaje > 0%.

---

## Paso 5 — Descargar llama3 y verificar

```powershell
ollama pull llama3
ollama run llama3 "Hola, responde en una línea"
```

---

## Paso 6 — Ejecutar el sistema con llama3 y GPU

```powershell
cd C:\Users\migue\OneDrive\Documents\DEVs\BIBLIOGRAFIAS
.venv\Scripts\activate
python main.py --input data/input/referencias_phishing_36_52.json --modo con_llm --modelo llama3
```

El log debe mostrar:
```
Hardware: GPU (num_ctx=4096, timeout=120s)
```

Si sigue diciendo CPU, forzar con variable de entorno antes de ejecutar:

```powershell
$env:LLM_MODEL = "llama3"
python main.py --input data/input/referencias_phishing_36_52.json --modo con_llm --modelo llama3
```

---

## Diagnóstico adicional si GPU sigue sin detectarse

```powershell
# Ver versión de drivers NVIDIA instalados
Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceName -like "*NVIDIA*" } | Select-Object DeviceName, DriverVersion

# Ver si CUDA está instalado
nvcc --version

# Ver logs internos de Ollama
Get-Content "$env:LOCALAPPDATA\Ollama\logs\server.log" -Tail 50
```
