---
name: JullBrain-metadata
description: >
  Skill para el mÃ³dulo metadata_extractor.py de JullBrain. Ãšsalo cuando necesites: extraer
  o corregir el YAML frontmatter de normativas venezolanas, agregar el nÃºmero de Gaceta
  Oficial, fecha de publicaciÃ³n o tipo de instrumento, calcular o verificar el hash SHA-256
  de un PDF, extender el schema de metadata para nuevas categorÃ­as jurÃ­dicas, o depurar
  problemas donde el frontmatter YAML estÃ¡ mal formado, incompleto o ausente. TambiÃ©n aplica
  para diseÃ±ar filtros de bÃºsqueda RAG basados en metadata. Trigger siempre que el usuario
  mencione: Gaceta Oficial, YAML frontmatter, metadata legal, SHA-256 de PDF,
  metadata_extractor, o filtros por fecha/instrumento.
---

# JullBrain Metadata Extractor â€” Skill Especializado

## Schema YAML Completo

```yaml
---
# â”€â”€ IDENTIFICACIÃ“N DEL INSTRUMENTO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
tipo_instrumento: "CÃ³digo"          # Ver tabla de tipos abajo
nombre_oficial: "CÃ³digo Penal de Venezuela"
nombre_corto: "CÃ³digo Penal"        # Para referencias en chunks

# â”€â”€ PUBLICACIÃ“N OFICIAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"     # ISO 8601: YYYY-MM-DD
fecha_ultima_reforma: "2005-03-16"  # Opcional: fecha de reforma mÃ¡s reciente

# â”€â”€ CLASIFICACIÃ“N TEMÃTICA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
categorias: ["penal", "procesal"]   # Lista de categorÃ­as (ver catÃ¡logo)
ambito: "nacional"                  # nacional | estadal | municipal

# â”€â”€ ESTADÃSTICAS DE EXTRACCIÃ“N â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
articulos_detectados: 640
articulos_vigentes: 635             # Excluye derogados si se detectan
titulos_detectados: 8
capitulos_detectados: 24

# â”€â”€ INTEGRIDAD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
hash_pdf_sha256: "abc123..."        # SHA-256 del PDF original
fecha_procesamiento: "2026-01-15"   # CuÃ¡ndo se procesÃ³ con JullBrain
version_JullBrain: "1.0"
---
```

---

## Tipos de Instrumento Legal (Venezuela)

| `tipo_instrumento` | Ejemplos |
|-------------------|---------|
| `"CÃ³digo"` | CÃ³digo Penal, CÃ³digo Civil, COPP |
| `"Ley OrgÃ¡nica"` | LOPNA, LOPCYMAT |
| `"Ley Especial"` | Ley Especial de Delitos InformÃ¡ticos |
| `"Ley"` | Ley sobre Mensajes de Datos |
| `"Decreto con Rango de Ley"` | Decretos-Ley del Ejecutivo |
| `"Decreto"` | Decretos ejecutivos |
| `"ResoluciÃ³n"` | Resoluciones ministeriales |
| `"Circular"` | Circulares de organismos |
| `"Norma TÃ©cnica"` | ISO, NIST, COVENIN |
| `"Reglamento"` | Reglamentos de ejecuciÃ³n |

## CatÃ¡logo de CategorÃ­as

```python
CATEGORIAS_VALIDAS = {
    # Derecho Sustantivo
    "penal", "civil", "mercantil", "laboral", "administrativo",
    "constitucional", "tributario", "ambiental", "familiar",
    
    # Derecho Procesal
    "procesal_penal", "procesal_civil", "procesal_laboral",
    
    # Ãreas Especiales
    "informatica_forense", "delitos_informaticos", "firma_electronica",
    "datos_personales", "telecomunicaciones", "financiero", "bancario",
    
    # Organismos
    "cenif", "sudeban", "conatel", "seniat",
    
    # Normas TÃ©cnicas
    "iso_27000", "nist", "covenin",
}
```

---

## ExtracciÃ³n AutomÃ¡tica de Metadata

### Algoritmo de DetecciÃ³n de Gaceta Oficial

```python
import re
from datetime import datetime

GACETA_PATTERNS = [
    # "Gaceta Oficial NÂ° 5.494 Extraordinario del 20/10/2000"
    r'[Gg]aceta\s+[Oo]ficial\s+(?:[Ee]xtraordinaria?\s+)?[Nn][Â°Âº]\s*([\d.,]+(?:\s+Extraordinario)?)',
    # "G.O. NÂ° 5494"
    r'G\.O\.\s+[Nn][Â°Âº]\s*([\d.,]+(?:\s+Extraordinario)?)',
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
    """Extrae nÃºmero de Gaceta Oficial del texto de la ley."""
    for pattern in GACETA_PATTERNS:
        m = re.search(pattern, text[:3000])  # Buscar en las primeras pÃ¡ginas
        if m:
            return m.group(1).strip()
    return "N/D"

def extract_date(text: str) -> str:
    """Extrae fecha de publicaciÃ³n en formato ISO 8601."""
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

### CÃ¡lculo de SHA-256

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

### DetecciÃ³n de Tipo de Instrumento

```python
TIPO_KEYWORDS = {
    "CÃ³digo": [r'\bCÃ³digo\b', r'\bCODIGO\b'],
    "Ley OrgÃ¡nica": [r'Ley\s+OrgÃ¡nica', r'LEY\s+ORGÃNICA'],
    "Ley Especial": [r'Ley\s+Especial', r'LEY\s+ESPECIAL'],
    "Decreto con Rango de Ley": [r'Decreto\s+con\s+[Ff]uerza', r'Decreto\s+[Ll]ey'],
    "Ley": [r'^Ley\s+(?!OrgÃ¡nica|Especial)', r'^LEY\s+(?!ORGÃNICA|ESPECIAL)'],
    "Reglamento": [r'\bReglamento\b'],
    "ResoluciÃ³n": [r'\bResoluciÃ³n\b'],
    "Decreto": [r'^\s*Decreto\s+N[Â°Âº]'],
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

## InyecciÃ³n del Frontmatter al Markdown

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

## ValidaciÃ³n del Frontmatter

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
            issues.append(f"Campo no detectado automÃ¡ticamente: {field} â€” revisar manualmente")
    
    # Validar formato de fecha
    if 'fecha_publicacion' in metadata and metadata['fecha_publicacion'] != "N/D":
        try:
            datetime.strptime(metadata['fecha_publicacion'], '%Y-%m-%d')
        except ValueError:
            issues.append(f"Formato de fecha invÃ¡lido: {metadata['fecha_publicacion']} (usar YYYY-MM-DD)")
    
    # Validar SHA-256 (64 caracteres hex)
    if 'hash_pdf_sha256' in metadata:
        h = metadata['hash_pdf_sha256']
        if len(h) != 64 or not all(c in '0123456789abcdef' for c in h.lower()):
            issues.append(f"SHA-256 invÃ¡lido: {h[:20]}...")
    
    return issues
```

---

## Uso en RAG: Filtros por Metadata

Con el frontmatter YAML correcto, los sistemas RAG pueden filtrar:

```python
# LangChain â€” Filtrar por tipo de instrumento y fecha
retriever = vectorstore.as_retriever(
    search_kwargs={
        "filter": {
            "tipo_instrumento": "CÃ³digo",
            "fecha_publicacion": {"$gte": "2000-01-01"}
        }
    }
)

# ChromaDB â€” Filtrar por categorÃ­a
results = collection.query(
    query_texts=["Â¿QuÃ© dice sobre el delito informÃ¡tico?"],
    where={"categorias": {"$contains": "delitos_informaticos"}}
)
```

