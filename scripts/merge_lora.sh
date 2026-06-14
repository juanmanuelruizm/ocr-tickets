#!/usr/bin/env bash
# Fusiona el adaptador LoRA entrenado en el modelo base GLM-OCR para desplegar.
#
# Uso:
#   LLAMAFACTORY_HOME=/ruta/a/LLaMA-Factory \
#     bash scripts/merge_lora.sh [adapter_dir] [export_dir]
#
# Por defecto:
#   adapter_dir = saves/glm-ocr/lora/tickets
#   export_dir  = <adapter_dir>/merged
set -euo pipefail

ADAPTER_DIR="${1:-saves/glm-ocr/lora/tickets}"
EXPORT_DIR="${2:-${ADAPTER_DIR%/}/merged}"
BASE_MODEL="${BASE_MODEL:-zai-org/GLM-OCR}"

if [[ ! -d "${ADAPTER_DIR}" ]]; then
  echo "Error: no existe el directorio del adaptador: ${ADAPTER_DIR}" >&2
  exit 1
fi

if command -v llamafactory-cli >/dev/null 2>&1; then
  CLI=(llamafactory-cli)
elif [[ -n "${LLAMAFACTORY_HOME:-}" ]]; then
  CLI=(python "${LLAMAFACTORY_HOME}/src/llamafactory/cli.py")
else
  echo "Error: no se encuentra 'llamafactory-cli'. Instala LLaMA-Factory o " \
       "define LLAMAFACTORY_HOME." >&2
  exit 1
fi

echo "Fusionando ${ADAPTER_DIR} sobre ${BASE_MODEL} -> ${EXPORT_DIR}"
exec "${CLI[@]}" export \
  --model_name_or_path "${BASE_MODEL}" \
  --adapter_name_or_path "${ADAPTER_DIR}" \
  --template glm_ocr \
  --finetuning_type lora \
  --export_dir "${EXPORT_DIR}" \
  --export_size 5 \
  --trust_remote_code true
