# Extensión: Soporte de Secciones Numeradas (ISO/NIST)

## El problema

Los documentos ISO/NIST no usan "Artículo N" sino numeración jerárquica:
```
1. Scope
1.1 Purpose
1.2 Applicability
2. Normative References
3.1.1 Definition of X
```

El `legalizer.py` actual está optimizado para el patrón venezolano (`Artículo N`).

## Solución: Parser Alternativo

Agregar detección de tipo de documento antes del procesamiento principal:

```python
# En legalizer.py — agregar función de detección

import re

def detect_document_type(text: str) -> str:
    """Detecta si el documento usa artículos venezolanos o secciones ISO."""
    articulo_pattern = re.compile(r'\bArt[íi]culo\s+\d+', re.IGNORECASE)
    section_pattern = re.compile(r'^\d+\.\d+[\s\t]', re.MULTILINE)
    
    articulo_hits = len(articulo_pattern.findall(text[:5000]))
    section_hits = len(section_pattern.findall(text[:5000]))
    
    if articulo_hits > section_hits:
        return "venezuelan_law"
    elif section_hits > 0:
        return "iso_nist"
    else:
        return "unknown"
```

## Patrones de Sección ISO para el Chunker

```python
ISO_SECTION_PATTERNS = [
    # Sección principal: "1. Scope"
    r'^(\d+)\.\s+([A-Z][^\n]{3,80})$',
    # Subsección: "1.1 Purpose"  
    r'^(\d+\.\d+)\s+([A-Z][^\n]{3,80})$',
    # Sub-subsección: "3.1.1 Definition"
    r'^(\d+\.\d+\.\d+)\s+([A-Z][^\n]{3,80})$',
]
```

## YAML Frontmatter para Documentos ISO

```yaml
---
tipo_instrumento: "Norma Técnica"
nombre_oficial: "ISO/IEC 27037:2012"
tipo_numeracion: "secciones"  # Diferenciador clave
seccion_raiz: "1"
subsecciones_detectadas: 45
categorias: ["ISO", "evidencia_digital", "forense"]
hash_pdf_sha256: "..."
---
```

## Metadata Adicional para Chunks ISO

```yaml
---
documento: "ISO/IEC 27037"
seccion: "4.1.2"
titulo_seccion: "Identification of digital evidence"
jerarquia: "4 > 4.1 > 4.1.2"
tipo_numeracion: "iso"
---
```

## Estado de Implementación

- [ ] Función `detect_document_type()` en `legalizer.py`
- [ ] Parser de secciones ISO en `legalizer.py`
- [ ] YAML schema extendido en `metadata_extractor.py`
- [ ] Tests de regresión para documentos mixtos
- [ ] Flag `--doc-type [auto|venezolano|iso]` en `convert_normativas.py`
