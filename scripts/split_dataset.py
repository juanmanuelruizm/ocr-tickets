#!/usr/bin/env python3
"""Divide un dataset ShareGPT en particiones de entrenamiento y validación.

Ejemplo:
    python scripts/split_dataset.py \
        --input data/tickets.json \
        --train data/tickets_train.json \
        --val data/tickets_val.json \
        --val-ratio 0.1 --seed 42
"""
import argparse
import json
import random
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--train", required=True, type=Path)
    ap.add_argument("--val", required=True, type=Path)
    ap.add_argument("--val-ratio", type=float, default=0.1,
                    help="Proporción de muestras para validación (0-1).")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not 0.0 <= args.val_ratio < 1.0:
        ap.error("--val-ratio debe estar en [0, 1)")

    data = json.loads(args.input.read_text(encoding="utf-8"))
    random.Random(args.seed).shuffle(data)

    n_val = int(len(data) * args.val_ratio)
    val, train = data[:n_val], data[n_val:]

    for path, part in ((args.train, train), (args.val, val)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(part, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"Total: {len(data)} | train: {len(train)} | val: {len(val)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
