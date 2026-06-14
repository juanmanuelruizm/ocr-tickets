#!/usr/bin/env python3
"""Inferencia de extracción de tickets con GLM-OCR (+ adaptador LoRA opcional).

Carga el modelo base GLM-OCR, opcionalmente aplica un adaptador LoRA entrenado,
y extrae el JSON estructurado de una imagen de ticket.

Ejemplo:
    python scripts/infer.py \
        --model zai-org/GLM-OCR \
        --adapter saves/glm-ocr/lora/tickets \
        --image data/raw/images/ticket_0001.jpg \
        --prompt prompts/ticket_extraction.txt

Nota: la API exacta de carga de GLM-OCR puede variar entre versiones de
transformers; ajusta processor/model si la tarjeta del modelo lo indica.
"""
import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="zai-org/GLM-OCR",
                    help="Modelo base o ruta del modelo ya fusionado.")
    ap.add_argument("--adapter", default=None,
                    help="Directorio del adaptador LoRA (opcional).")
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--prompt", required=True, type=Path)
    ap.add_argument("--max-new-tokens", type=int, default=2048)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    prompt = load_prompt(args.prompt)
    image = Image.open(args.image).convert("RGB")

    processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map=args.device,
    )

    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)

    model.eval()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = processor(text=[text], images=[image], return_tensors="pt").to(model.device)

    with torch.no_grad():
        generated = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)

    trimmed = generated[:, inputs["input_ids"].shape[1]:]
    output = processor.batch_decode(trimmed, skip_special_tokens=True)[0].strip()

    # Intenta validar/imprimir como JSON; si no, muestra el texto crudo.
    try:
        parsed = json.loads(output)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
