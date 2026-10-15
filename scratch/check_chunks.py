import os
from pathlib import Path
import json

BASE_DIR = Path(r"c:\VS CODE\CODIGO\JullBrain")
RAG_DIR = BASE_DIR / "normativas_rag"
CHUNKS_DIR = BASE_DIR / "normativas_chunks"

md_files = list(RAG_DIR.rglob("*.md"))
print(f"Total MD: {len(md_files)}")

invalid_json = []
empty_json = []
missing_json = []

for md_file in md_files:
    if md_file.name == ".gitkeep":
        continue
    
    rel_path = md_file.relative_to(RAG_DIR)
    chunk_dir = CHUNKS_DIR / rel_path.parent / md_file.stem
    chunk_file = chunk_dir / "hierarchical_chunks.json"
    
    if not chunk_file.exists():
        missing_json.append(rel_path)
    else:
        # Verificar contenido
        try:
            size = chunk_file.stat().st_size
            if size == 0:
                empty_json.append(rel_path)
                continue
            with open(chunk_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list) or len(data) == 0:
                    empty_json.append(rel_path)
        except Exception as e:
            invalid_json.append((rel_path, str(e)))

print(f"No existen: {len(missing_json)}")
for p in missing_json:
    print(f" - {p}")

print(f"Vacíos o listas vacías: {len(empty_json)}")
for p in empty_json:
    print(f" - {p}")

print(f"JSON Inválidos: {len(invalid_json)}")
for p, err in invalid_json:
    print(f" - {p}: {err}")
