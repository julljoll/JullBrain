# Skill 01 — Ingesta Documental con Docling

## 1. Rol responsable
**R1 (arquitectura del pipeline) + R2 (implementación)**.

## 2. Propósito
Convertir expedientes penales en sus formatos originales (PDF nativo, PDF escaneado, imagen, Word) en una representación estructurada y fiel al orden del documento fuente, preservando folio, jerarquía y metadatos — condición de entrada para todas las skills posteriores.

## 3. Entradas
- Archivo del expediente (PDF/imagen/docx) en `/data/raw/<expediente_id>/`.

## 4. Salidas
- Documento estructurado en formato Markdown/JSON (`DoclingDocument`), con metadato de folio y posición por cada elemento.

## 5. Dependencias tecnológicas
Docling (IBM Research), Python 3.11+.

## 6. Reglas obligatorias
1. **Espejo documental (principio forense, R7):** ningún texto se descarta, resume ni corrige en esta etapa. Lo que Docling no puede leer con confianza se marca, no se omite.
2. Cada elemento extraído (párrafo, tabla, firma, sello) conserva su número de folio y posición de origen.
3. No se realiza ningún tipo de inferencia semántica en esta skill — es exclusivamente conversión estructural.

## 7. Implementación de referencia

```python
# skills/01_docling_ingesta/ingest.py
from docling.document_converter import DocumentConverter
from pathlib import Path
import json

def ingest_expediente(filepath: str, expediente_id: str, output_dir: str = "data/structured"):
    """
    Convierte un archivo de expediente a formato estructurado,
    preservando folio y orden original (principio de espejo documental).
    """
    converter = DocumentConverter()
    result = converter.convert(filepath)
    doc = result.document

    output_path = Path(output_dir) / expediente_id
    output_path.mkdir(parents=True, exist_ok=True)

    # Exportar a Markdown preservando estructura
    md_content = doc.export_to_markdown()
    (output_path / "estructura.md").write_text(md_content, encoding="utf-8")

    # Exportar metadatos de posición/folio por elemento (para Skill 03)
    elementos = []
    for idx, item in enumerate(doc.texts):
        elementos.append({
            "elemento_id": idx,
            "folio_origen": getattr(item, "prov", None),  # proveniencia/página
            "texto": item.text,
            "tipo": item.label,
        })

    (output_path / "metadatos_posicion.json").write_text(
        json.dumps(elementos, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "expediente_id": expediente_id,
        "total_elementos": len(elementos),
        "output_dir": str(output_path),
    }

if __name__ == "__main__":
    resultado = ingest_expediente("data/raw/EXP-001/expediente.pdf", "EXP-001")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
```

## 8. Criterios de aceptación
- [ ] 100% de las páginas del original tienen al menos un elemento extraído o marcado como "no legible" (nunca ausente sin registro).
- [ ] Cada elemento conserva su referencia de folio/página.
- [ ] Prueba con al menos un expediente simulado de ≥30 páginas, mezclando texto nativo y escaneado.

## 9. Relación con otras skills
Entrada directa de la Skill 02 (control de calidad OCR) y la Skill 03 (estructuración cronológica).
