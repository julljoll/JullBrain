---
name: JullBrain-metadata
description: >
  Skill para el módulo metadata_extractor.py de JullBrain. Úsalo cuando necesites: extraer
  o corregir el YAML frontmatter de normativas venezolanas, agregar el número de Gaceta
  Oficial, fecha de publicación o tipo de instrumento, calcular o verificar el hash SHA-256
  de un PDF, extender el schema de metadata para nuevas categorías jurídicas, o depurar
  problemas donde el frontmatter YAML está mal formado, incompleto o ausente. También aplica
  para diseñar filtros de búsqueda RAG basados en metadata. Trigger siempre que el usuario
  mencione: Gaceta Oficial, YAML frontmatter, metadata legal, SHA-256 de PDF,
  metadata_extractor, o filtros por fecha/instrumento.
---

# JullBrain Metadata Extractor — Skill Especializado

## Schema YAML Completo

```yaml
---
# ── IDENTIFICACIÓN DEL INSTRUMENTO ──────────────────────────────
tipo_instrumento: "Código"          # Ver tabla de tipos abajo
nombre_oficial: "Código Penal de Venezuela"
nombre_corto: "Código Penal"        # Para referencias en chunks

# ── PUBLICACIÓN OFICIAL ──────────────────────────────────────────
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"     # ISO 8601: YYYY-MM-DD
fecha_ultima_reforma: "2005-03-16"  # Opcional: fecha de reforma más reciente

# ── CLASIFICACIÓN TEMÁTICA ───────────────────────────────────────
categorias: ["penal", "procesal"]   # Lista de categorías (ver catálogo)
ambito: "nacional"                  # nacional | estadal | municipal

# ── ESTADÍSTICAS DE EXTRACCIÓN ───────────────────────────────────
articulos_detectados: 640
articulos_vigentes: 635             # Excluye derogados si se detectan
titulos_detectados: 8
capitulos_detectados: 24

# ── INTEGRIDAD ───────────────────────────────────────────────────
hash_pdf_sha256: "abc123..."        # SHA-256 del PDF original
fecha_procesamiento: "2026-01-15"   # Cuándo se procesó con JullBrain
version_JullBrain: "1.0"
---
```

---

## Tipos de Instrumento Legal (Venezuela)

| `tipo_instrumento` | Ejemplos |
|-------------------|---------|
| `"Código"` | Código Penal, Código Civil, COPP |
| `"Ley Orgánica"` | LOPNA, LOPCYMAT |
| `"Ley Especial"` | Ley Especial de Delitos Informáticos |
| `"Ley"` | Ley sobre Mensajes de Datos |
| `"Decreto con Rango de Ley"` | Decretos-Ley del Ejecutivo |
| `"Decreto"` | Decretos ejecutivos |
| `"Resolución"` | Resoluciones ministeriales |
| `"Circular"` | Circulares de organismos |
| `"Norma Técnica"` | ISO, NIST, COVENIN |
| `"Reglamento"` | Reglamentos de ejecución |

## Catálogo de Categorías

```python
CATEGORIAS_VALIDAS = {
    # Derecho Sustantivo
    "penal", "civil", "mercantil", "laboral", "administrativo",
    "constitucional", "tributario", "ambiental", "familiar",
    
    # Derecho Procesal
    "procesal_penal", "procesal_civil", "procesal_laboral",
    
    # Áreas Especiales
    "informatica_forense", "delitos_informaticos", "firma_electronica",
    "datos_personales", "telecomunicaciones", "financiero", "bancario",
    
    # Organismos
    "cenif", "sudeban", "conatel", "seniat",
    
    # Normas Técnicas
    "iso_27000", "nist", "covenin",
}
```

---

## Extracción Automática de Metadata

### Algoritmo de Detección de Gaceta Oficial

```python
import re
from datetime import datetime

GACETA_PATTERNS = [
    # "Gaceta Oficial N° 5.494 Extraordinario del 20/10/2000"
    r'[Gg]aceta\s+[Oo]ficial\s+(?:[Ee]xtraordinaria?\s+)?[Nn][°º]\s*([\d.,]+(?:\s+Extraordinario)?)',
    # "G.O. N° 5494"
    r'G\.O\.\s+[Nn][°º]\s*([\d.,]+(?:\s+Extraordinario)?)',
    # En el propio nombre del PDF: "GO-5494-Extraordinario"
    r'GO[-_](\d+)[-_]?(Extraordinario|Ordinario)?',
]

DATE_PATTERNS = [
    # "20 de octubre de 2000"
    r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})',
    # "20/10/2000" o "20-10-2000"
    r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
]

MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def extract_gaceta(text: str) -> str:
    """Extrae número de Gaceta Oficial del texto de la ley."""
    for pattern in GACETA_PATTERNS:
        m = re.search(pattern, text[:3000])  # Buscar en las primeras páginas
        if m:
            return m.group(1).strip()
    return "N/D"

def extract_date(text: str) -> str:
    """Extrae fecha de publicación en formato ISO 8601."""
    for pattern in DATE_PATTERNS:
        m = re.search(pattern, text[:3000], re.IGNORECASE)
        if m:
            if len(m.groups()) == 3:
                day, month_str, year = m.groups()
                if month_str.lower() in MESES:
                    month = MESES[month_str.lower()]
                else:
                    month = month_str.zfill(2)
                return f"{year}-{month}-{day.zfill(2)}"
    return "N/D"
```

### Cálculo de SHA-256

```python
import hashlib

def calculate_sha256(file_path: str) -> str:
    """Calcula SHA-256 del archivo PDF original."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
```

### Detección de Tipo de Instrumento

```python
TIPO_KEYWORDS = {
    "Código": [r'\bCódigo\b', r'\bCODIGO\b'],
    "Ley Orgánica": [r'Ley\s+Orgánica', r'LEY\s+ORGÁNICA'],
    "Ley Especial": [r'Ley\s+Especial', r'LEY\s+ESPECIAL'],
    "Decreto con Rango de Ley": [r'Decreto\s+con\s+[Ff]uerza', r'Decreto\s+[Ll]ey'],
    "Ley": [r'^Ley\s+(?!Orgánica|Especial)', r'^LEY\s+(?!ORGÁNICA|ESPECIAL)'],
    "Reglamento": [r'\bReglamento\b'],
    "Resolución": [r'\bResolución\b'],
    "Decreto": [r'^\s*Decreto\s+N[°º]'],
}

def detect_instrument_type(text: str, filename: str) -> str:
    search_text = (filename + " " + text[:1000]).lower()
    for tipo, patterns in TIPO_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, search_text, re.IGNORECASE):
                return tipo
    return "Instrumento Legal"
```

---

## Inyección del Frontmatter al Markdown

```python
import yaml

def inject_frontmatter(markdown_content: str, metadata: dict) -> str:
    """
    Inyecta el YAML frontmatter al inicio del Markdown.
    Si ya existe frontmatter, lo reemplaza.
    """
    # Remover frontmatter existente si hay
    if markdown_content.startswith('---\n'):
        end = markdown_content.find('\n---\n', 3)
        if end != -1:
            markdown_content = markdown_content[end + 5:]
    
    # Generar YAML limpio
    yaml_str = yaml.dump(
        metadata, 
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False
    )
    
    return f"---\n{yaml_str}---\n\n{markdown_content}"
```

---

## Validación del Frontmatter

```python
REQUIRED_FIELDS = ['tipo_instrumento', 'nombre_oficial', 'gaceta_oficial', 
                   'fecha_publicacion', 'hash_pdf_sha256']

def validate_frontmatter(metadata: dict) -> list[str]:
    """Retorna lista de problemas encontrados en el frontmatter."""
    issues = []
    
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            issues.append(f"Campo requerido faltante: {field}")
        elif metadata[field] == "N/D":
            issues.append(f"Campo no detectado automáticamente: {field} — revisar manualmente")
    
    # Validar formato de fecha
    if 'fecha_publicacion' in metadata and metadata['fecha_publicacion'] != "N/D":
        try:
            datetime.strptime(metadata['fecha_publicacion'], '%Y-%m-%d')
        except ValueError:
            issues.append(f"Formato de fecha inválido: {metadata['fecha_publicacion']} (usar YYYY-MM-DD)")
    
    # Validar SHA-256 (64 caracteres hex)
    if 'hash_pdf_sha256' in metadata:
        h = metadata['hash_pdf_sha256']
        if len(h) != 64 or not all(c in '0123456789abcdef' for c in h.lower()):
            issues.append(f"SHA-256 inválido: {h[:20]}...")
    
    return issues
```

---

## Uso en RAG: Filtros por Metadata

Con el frontmatter YAML correcto, los sistemas RAG pueden filtrar:

```python
# LangChain — Filtrar por tipo de instrumento y fecha
retriever = vectorstore.as_retriever(
    search_kwargs={
        "filter": {
            "tipo_instrumento": "Código",
            "fecha_publicacion": {"$gte": "2000-01-01"}
        }
    }
)

# ChromaDB — Filtrar por categoría
results = collection.query(
    query_texts=["¿Qué dice sobre el delito informático?"],
    where={"categorias": {"$contains": "delitos_informaticos"}}
)
```

