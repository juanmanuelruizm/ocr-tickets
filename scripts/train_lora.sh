#!/usr/bin/env bash
# Lanza el entrenamiento LoRA de GLM-OCR para tickets con LLaMA-Factory.
#
# Uso:
#   LLAMAFACTORY_HOME=/ruta/a/LLaMA-Factory \
#     bash scripts/train_lora.sh [configs/tickets_lora_sft.yaml]
#
# Variables de entorno:
#   LLAMAFACTORY_HOME   ruta a la instalación de LLaMA-Factory (obligatoria si
#                       llamafactory-cli no está en el PATH)
#   CUDA_VISIBLE_DEVICES  GPUs a usar (por defecto 0)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${1:-${REPO_ROOT}/configs/tickets_lora_sft.yaml}"

if [[ ! -f "${CONFIG}" ]]; then
  echo "Error: no se encuentra la configuración: ${CONFIG}" >&2
  exit 1
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export DISABLE_VERSION_CHECK="${DISABLE_VERSION_CHECK:-1}"

if command -v llamafactory-cli >/dev/null 2>&1; then
  CLI=(llamafactory-cli)
elif [[ -n "${LLAMAFACTORY_HOME:-}" ]]; then
  CLI=(python "${LLAMAFACTORY_HOME}/src/llamafactory/cli.py")
else
  echo "Error: no se encuentra 'llamafactory-cli'. Instala LLaMA-Factory o " \
       "define LLAMAFACTORY_HOME." >&2
  exit 1
fi

echo "Entrenando con: ${CONFIG}"
echo "GPUs: ${CUDA_VISIBLE_DEVICES}"
exec "${CLI[@]}" train "${CONFIG}"
