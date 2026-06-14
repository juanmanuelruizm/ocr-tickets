# Esquema de salida de un ticket

El modelo, dada la imagen de un ticket, debe devolver **un único objeto JSON**
con la siguiente estructura. Todos los importes son números (punto decimal) y
las cantidades faltantes se devuelven como `null`.

```json
{
  "comercio": {
    "nombre": "string",
    "cif": "string | null",
    "direccion": "string | null",
    "telefono": "string | null"
  },
  "ticket": {
    "numero": "string | null",
    "fecha": "DD/MM/AAAA | null",
    "hora": "HH:MM | null"
  },
  "lineas": [
    {
      "descripcion": "string",
      "cantidad": "number",
      "precio_unitario": "number | null",
      "importe": "number"
    }
  ],
  "impuestos": [
    {
      "tipo": "string",
      "porcentaje": "number",
      "base": "number | null",
      "cuota": "number | null"
    }
  ],
  "subtotal": "number | null",
  "total": "number",
  "forma_pago": "string | null"
}
```

## Convenciones

- **Importes**: punto como separador decimal, sin símbolo de moneda
  (`12.50`, no `12,50 €`).
- **Fechas**: formato `DD/MM/AAAA`. Si el ticket usa otro formato, se normaliza.
- **Impuestos**: una entrada por cada tipo de IVA presente en el ticket.
  En España lo habitual es `IVA` con porcentajes 4, 10 o 21.
- **Campos ausentes**: `null` (no se inventan valores).
- **Coherencia**: `total` debe coincidir con la suma de líneas + impuestos
  cuando el ticket lo permita; no se fuerza si el ticket es ilegible.

## Ejemplo

```json
{
  "comercio": {
    "nombre": "SUPERMERCADO LA PLAZA S.L.",
    "cif": "B12345678",
    "direccion": "C/ Mayor 12, 28013 Madrid",
    "telefono": "911234567"
  },
  "ticket": { "numero": "A-004521", "fecha": "14/06/2026", "hora": "19:42" },
  "lineas": [
    { "descripcion": "LECHE ENTERA 1L", "cantidad": 2, "precio_unitario": 0.95, "importe": 1.90 },
    { "descripcion": "PAN DE MOLDE",    "cantidad": 1, "precio_unitario": 1.45, "importe": 1.45 }
  ],
  "impuestos": [
    { "tipo": "IVA", "porcentaje": 4, "base": 3.22, "cuota": 0.13 }
  ],
  "subtotal": 3.22,
  "total": 3.35,
  "forma_pago": "TARJETA"
}
```
