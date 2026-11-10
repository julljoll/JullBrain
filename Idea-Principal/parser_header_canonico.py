"""
parser_header_canonico.py — Validador del Encabezado Canónico de JullBrain & UMIF v0.2.0
Verifica que los archivos .bat contengan todos los campos obligatorios del estándar
canónico oficial, utilicen exclusivamente Google Antigravity + tecnología IBM, y estén
codificados en UTF-8 sin BOM con saltos de línea CRLF.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

REQUIRED_FIELDS = [
    "Proyecto",
    "Idea Principal",
    "Autor",
    "Rol Profesional",
    "Certificación UX",
    "Sitio Web",
    "Stack Tecnológico",
    "Leyes Nacionales",
    "Estándares Int.",
    "Licencia",
]

FIELD_REGEX = re.compile(r"^@?REM\s+([^:]+?)\s*:\s*(.+)$")


def parse_bat_header(filepath: str | Path) -> Dict[str, str]:
    """Extrae los pares clave-valor del bloque @REM / REM canónico de un archivo .bat."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    raw_bytes = path.read_bytes()
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    has_crlf = b"\r\n" in raw_bytes

    text = raw_bytes.decode("utf-8-sig", errors="replace")
    parsed: Dict[str, str] = {
        "_encoding_no_bom": "true" if not has_bom else "false",
        "_line_endings_crlf": "true" if has_crlf else "false",
    }

    last_key = None
    for line in text.splitlines()[:45]:
        stripped = line.strip()
        match = FIELD_REGEX.match(stripped)
        if match:
            key = match.group(1).strip()
            val = match.group(2).strip()
            parsed[key] = val
            last_key = key
        elif last_key and stripped.startswith(("@REM", "REM")) and "===" not in stripped:
            continuation = re.sub(r"^@?REM\s+", "", stripped).strip()
            if continuation:
                parsed[last_key] = f"{parsed[last_key]} {continuation}"

    return parsed


def validate_bat_header(filepath: str | Path) -> List[str]:
    """Valida que el encabezado cumpla con el estándar canónico v0.2.0."""
    errors: List[str] = []
    parsed = parse_bat_header(filepath)

    if parsed.get("_encoding_no_bom") != "true":
        errors.append("El archivo .bat contiene BOM UTF-8 (debe ser UTF-8 sin BOM).")
    if parsed.get("_line_endings_crlf") != "true":
        errors.append("El archivo .bat no utiliza saltos de línea CRLF (\\r\\n).")

    for req in REQUIRED_FIELDS:
        if req not in parsed:
            errors.append(f"Falta el campo canónico obligatorio: '{req}'")

    stack_text = parsed.get("Stack Tecnológico", "")
    for forbidden in ("Claude", "OpenAI", "ChatGPT", "Qwen", "Streamlit", "Chocolatey"):
        if forbidden.lower() in stack_text.lower():
            errors.append(f"El Stack Tecnológico menciona tecnología no permitida: {forbidden}")

    return errors


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "orquestador_JullBrain.bat"
    errs = validate_bat_header(target)
    if errs:
        print(f"[ERROR] Falló la validación canónica de {target}:")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)
    print(f"[OK] Encabezado canónico válido en {target}")
