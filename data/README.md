# Datos

Esta carpeta contiene los datos del proyecto. El contenido de `raw/` y los
JSON derivados **no se versionan** (ver `.gitignore`); solo se versiona
`dataset_info.json`.

## Estructura esperada

```
data/
├── dataset_info.json        # registro de datasets (versionado)
├── raw/
│   ├── images/              # imágenes de tickets (.jpg / .png)
│   │   ├── ticket_0001.jpg
│   │   └── ...
│   └── annotations.jsonl    # una anotación por línea
├── tickets.json             # generado por prepare_dataset.py
├── tickets_train.json       # generado por split_dataset.py
└── tickets_val.json         # generado por split_dataset.py
```

## Formato de `annotations.jsonl`

Un objeto JSON por línea. Campos:

- `image`: ruta de la imagen, relativa a `--images-root`.
- `label`: el objeto JSON esperado (ver [`../docs/schema.md`](../docs/schema.md)).
  Puede ir como objeto anidado o como cadena ya serializada.

```json
{"image": "ticket_0001.jpg", "label": {"comercio": {"nombre": "..."}, "total": 3.35}}
```

Ver [`../examples/sample_annotations.jsonl`](../examples/sample_annotations.jsonl).

## Formato ShareGPT (consumo de LLaMA-Factory)

`prepare_dataset.py` convierte cada anotación en una muestra ShareGPT:

```json
{
  "messages": [
    {"role": "user", "content": "<image>Extrae la información de este ticket..."},
    {"role": "assistant", "content": "{\"comercio\": {...}, \"total\": 3.35}"}
  ],
  "images": ["images/ticket_0001.jpg"]
}
```

Cada etiqueta `<image>` del texto corresponde a una entrada de `images`: el
número debe coincidir exactamente.
