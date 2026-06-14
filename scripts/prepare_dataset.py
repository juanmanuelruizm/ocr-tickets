#!/usr/bin/env python3
"""Convierte anotaciones crudas de tickets al formato ShareGPT de LLaMA-Factory.

Entrada:  un .jsonl con un objeto por línea {"image": ..., "label": ...}
Salida:   un .json (lista de muestras ShareGPT) listo para GLM-OCR.

Ejemplo:
    python scripts/prepare_dataset.py \
        --annotations data/raw/annotations.jsonl \
        --images-root data/raw/images \
        --prompt prompts/ticket_extraction.txt \
        --out data/tickets.json
"""
import argparse
import json
import sys
from pathlib import Path


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def normalize_label(label) -> str:
    """Devuelve el label como JSON serializado de forma estable.

    Acepta tanto un objeto ya estructurado como una cadena (que se valida
    para asegurar que es JSON correcto)."""
    if isinstance(label, str):
        label = json.loads(label)  # valida que sea JSON
    return json.dumps(label, ensure_ascii=False, sort_keys=False)


def build_sample(image_rel: str, prompt: str, label_json: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": f"<image>{prompt}"},
            {"role": "assistant", "content": label_json},
        ],
        "images": [image_rel],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--annotations", required=True, type=Path,
                    help="Fichero .jsonl con las anotaciones crudas.")
    ap.add_argument("--images-root", required=True, type=Path,
                    help="Carpeta raíz de las imágenes (las rutas se calculan relativas a ella).")
    ap.add_argument("--prompt", required=True, type=Path,
                    help="Fichero de texto con la instrucción de extracción.")
    ap.add_argument("--out", required=True, type=Path,
                    help="Fichero .json de salida en formato ShareGPT.")
    ap.add_argument("--image-prefix", default="images",
                    help="Prefijo de ruta de imagen que verá LLaMA-Factory "
                         "(relativo a su carpeta data/). Por defecto: images")
    args = ap.parse_args()

    prompt = load_prompt(args.prompt)

    samples = []
    skipped = 0
    with args.annotations.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"[aviso] línea {lineno}: JSON inválido ({exc}); se omite",
                      file=sys.stderr)
                skipped += 1
                continue

            image = rec.get("image")
            label = rec.get("label")
            if not image or label is None:
                print(f"[aviso] línea {lineno}: falta 'image' o 'label'; se omite",
                      file=sys.stderr)
                skipped += 1
                continue

            img_path = args.images_root / image
            if not img_path.exists():
                print(f"[aviso] línea {lineno}: no existe la imagen {img_path}; se omite",
                      file=sys.stderr)
                skipped += 1
                continue

            try:
                label_json = normalize_label(label)
            except json.JSONDecodeError as exc:
                print(f"[aviso] línea {lineno}: 'label' no es JSON válido ({exc}); se omite",
                      file=sys.stderr)
                skipped += 1
                continue

            image_rel = f"{args.image_prefix.rstrip('/')}/{Path(image).name}"
            samples.append(build_sample(image_rel, prompt, label_json))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(samples, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Escritas {len(samples)} muestras en {args.out} "
          f"({skipped} omitidas).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
