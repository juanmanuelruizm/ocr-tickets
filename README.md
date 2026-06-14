# ocr-tickets

Adaptación por **LoRA** del modelo **[GLM-OCR](https://huggingface.co/zai-org/GLM-OCR)**
al dominio de **tickets de compra / recibos**.

El objetivo es especializar GLM-OCR para que, dada la imagen de un ticket,
devuelva un **JSON estructurado** con los campos clave (comercio, fecha, líneas
de producto, impuestos, total, forma de pago…) — es decir, una tarea de
*Key Information Extraction* (KIE) sobre tickets reales.

El entrenamiento se hace con **[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)**,
que es el flujo oficial soportado por GLM-OCR.

---

## Estructura del repositorio

```
ocr-tickets/
├── configs/
│   └── tickets_lora_sft.yaml      # configuración de entrenamiento LoRA
├── data/
│   ├── dataset_info.json          # registro de datasets para LLaMA-Factory
│   ├── raw/                       # imágenes + anotaciones crudas (no versionado)
│   └── README.md                  # convenciones del dataset
├── scripts/
│   ├── prepare_dataset.py         # anotaciones crudas -> ShareGPT JSON
│   ├── split_dataset.py           # partición train / val
│   ├── train_lora.sh              # lanza el entrenamiento
│   ├── merge_lora.sh              # fusiona el adaptador en el modelo base
│   └── infer.py                   # inferencia sobre una imagen de ticket
├── prompts/
│   └── ticket_extraction.txt      # instrucción de extracción (prompt)
├── examples/
│   ├── sample_annotations.jsonl   # ejemplo de anotación de entrada
│   └── sample_sharegpt.json       # ejemplo de salida en formato ShareGPT
├── docs/
│   └── schema.md                  # esquema JSON de salida de un ticket
├── requirements.txt
└── README.md
```

---

## Flujo de trabajo

### 0. Requisitos

```bash
pip install -r requirements.txt

# LLaMA-Factory (en una carpeta hermana, fuera de este repo)
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory && pip install -e ".[torch,metrics]" && cd ..
```

LoRA cabe en una GPU de ~8 GB de VRAM; el full fine-tuning necesita ~24 GB.

### 1. Anotar los tickets

Coloca las imágenes en `data/raw/images/` y las anotaciones en
`data/raw/annotations.jsonl`. Cada línea es un objeto con la ruta de la imagen
y el JSON esperado (ver [`data/README.md`](data/README.md) y
[`docs/schema.md`](docs/schema.md)).

### 2. Construir el dataset en formato ShareGPT

```bash
python scripts/prepare_dataset.py \
  --annotations data/raw/annotations.jsonl \
  --images-root data/raw/images \
  --prompt prompts/ticket_extraction.txt \
  --out data/tickets.json

python scripts/split_dataset.py \
  --input data/tickets.json \
  --train data/tickets_train.json \
  --val data/tickets_val.json \
  --val-ratio 0.1
```

### 3. Registrar el dataset en LLaMA-Factory

Copia las imágenes y los JSON a `LLaMA-Factory/data/` y añade las entradas de
[`data/dataset_info.json`](data/dataset_info.json) al `dataset_info.json` de
LLaMA-Factory.

### 4. Entrenar el LoRA

```bash
LLAMAFACTORY_HOME=/ruta/a/LLaMA-Factory \
  bash scripts/train_lora.sh configs/tickets_lora_sft.yaml
```

### 5. Fusionar el adaptador (opcional, para desplegar)

```bash
LLAMAFACTORY_HOME=/ruta/a/LLaMA-Factory \
  bash scripts/merge_lora.sh saves/glm-ocr/lora/tickets
```

### 6. Inferencia

```bash
python scripts/infer.py \
  --model zai-org/GLM-OCR \
  --adapter saves/glm-ocr/lora/tickets \
  --image data/raw/images/ticket_0001.jpg \
  --prompt prompts/ticket_extraction.txt
```

---

## Referencias

- [Guía oficial de fine-tuning de GLM-OCR con LLaMA-Factory](https://github.com/zai-org/GLM-OCR/blob/main/examples/finetune/README.md)
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
