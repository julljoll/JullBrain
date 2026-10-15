#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
🏛️ JULLBRAIN & UMIF - PARSER E IDENTIFICADOR DE ENCABEZADOS CANÓNICOS
==============================================================================
Proyecto         : Jullbrain / UMIF (Unidad Móvil Informática Forense)
Idea Principal   : Laboratorio Móvil con IA Local para análisis de expedientes penales,
                   agilización de audiencias preliminares y descongestión judicial.
Autor            : Jull Ortiz
Rol Profesional  : Abogado - Diseñador UX/UI Especializado en LegalTech & Forense Digital
Certificación UX : IBM Enterprise Design Thinking / IBM UX Design Professional
Sitio Web        : http://www.sha256.us/
Stack Tecnológico: IBM Docling, IBM Granite 3.0, Granite Guardian (Anti-Alucinaciones),
                   Google OKF, LegalProcessor v2, Python 3.x Local, Vector DBs, SHA-256.
==============================================================================
"""

import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def identificar_encabezado_docling(ruta_archivo: str) -> dict:
    """
    Identifica y valida la estructura de metadatos en el encabezado YAML Frontmatter
    de un documento parseado por Docling / LegalProcessor / Google OKF.
    """
    if not os.path.exists(ruta_archivo):
        return {"valido": False, "error": f"Archivo no encontrado: {ruta_archivo}"}
    
    with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", contenido, re.DOTALL)
    if not match:
        return {
            "valido": False,
            "tipo": "Docling / OKF Markdown",
            "mensaje": "No se detectó bloque YAML Frontmatter al inicio."
        }

    raw_yaml = match.group(1)
    
    if HAS_YAML:
        try:
            data = yaml.safe_load(raw_yaml)
        except Exception as e:
            return {"valido": False, "tipo": "Docling / OKF Markdown", "error": f"Error al parsear YAML: {e}"}
    else:
        data = {}
        for line in raw_yaml.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"\'')

    contiene_autor = "Jull Ortiz" in raw_yaml or data.get("autor_procesamiento") == "Jull Ortiz"
    contiene_umif = "UMIF" in raw_yaml or "Unidad Móvil" in raw_yaml
    contiene_docling = "Docling" in raw_yaml or "sistema" in data
    contiene_granite = "Granite" in raw_yaml or "granite" in raw_yaml
    contiene_okf = "OKF" in raw_yaml or "trust_signals" in raw_yaml or "type:" in raw_yaml
    contiene_jullbrain = "Jullbrain" in raw_yaml or "JULLBRAIN" in raw_yaml
    contiene_ux_legal = "LegalTech" in raw_yaml or "UX/UI" in raw_yaml or "Abogado" in raw_yaml

    return {
        "valido": contiene_autor or contiene_docling or contiene_jullbrain or contiene_granite,
        "tipo": "Docling & Google OKF Markdown Header",
        "proyecto": "Jullbrain",
        "umif_detectado": contiene_umif,
        "granite_detectado": contiene_granite,
        "google_okf_detectado": contiene_okf,
        "perfil_ux_legaltech": contiene_ux_legal,
        "datos_detectados": {
            "proyecto": "Jullbrain",
            "autor": "Jull Ortiz" if contiene_autor else data.get("autor_procesamiento", "No especificado"),
            "rol_profesional": "Abogado - Diseñador UX/UI Especializado en LegalTech & Forense Digital",
            "certificacion_ux": "IBM Enterprise Design Thinking / IBM UX Design Professional",
            "llm_backbone": "IBM Granite 3.0 / 3.1 / 3.2",
            "filtro_seguridad": "IBM Granite Guardian (Anti-Alucinaciones)",
            "formato_conocimiento": "Google Open Knowledge Format (OKF)",
            "sistema_parsing": "IBM Docling + LegalProcessor v2",
            "submodulo_operativo": "UMIF (Unidad Móvil de Informática Forense)",
            "web": "http://www.sha256.us/"
        },
        "frontmatter_raw": data if HAS_YAML else raw_yaml
    }


def identificar_encabezado_bat(ruta_archivo: str) -> dict:
    """
    Identifica y valida si un archivo .bat posee el encabezado canónico Jullbrain & UMIF.
    """
    if not os.path.exists(ruta_archivo):
        return {"valido": False, "error": f"Archivo no encontrado: {ruta_archivo}"}

    with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = [f.readline() for _ in range(35)]

    encabezado_str = "".join(lineas)
    
    contiene_jullbrain = "Jullbrain" in encabezado_str or "JULLBRAIN" in encabezado_str
    contiene_autor = "Jull Ortiz" in encabezado_str
    contiene_umif = "UMIF" in encabezado_str or "Unidad Móvil" in encabezado_str
    contiene_granite = "Granite" in encabezado_str
    contiene_ux_legal = "LegalTech" in encabezado_str or "Diseñador UX/UI" in encabezado_str
    contiene_docling = "IBM Docling" in encabezado_str or "Docling" in encabezado_str

    es_valido = contiene_jullbrain and contiene_autor

    return {
        "valido": es_valido,
        "tipo": "Windows Batch Script (.bat) Header",
        "verificaciones": {
            "proyecto_jullbrain": contiene_jullbrain,
            "submodulo_umif": contiene_umif,
            "autor_jull_ortiz": contiene_autor,
            "stack_ibm_granite": contiene_granite,
            "perfil_ux_legaltech": contiene_ux_legal,
            "tecnologia_docling": contiene_docling
        },
        "datos_canonicos": {
            "proyecto": "Jullbrain",
            "idea_principal": "Unidad Móvil de IA Local para Expedientes Penales (Prevención de Retardo Procesal)",
            "autor": "Jull Ortiz",
            "rol_profesional": "Abogado - Diseñador UX/UI Especializado en LegalTech & Forense Digital",
            "certificacion_ux": "IBM Enterprise Design Thinking / IBM UX Design Professional",
            "equipo_operativo": "2 Peritos Entrenados (TIC + Derecho IA)",
            "tecnologias": "IBM Granite 3.0, Granite Guardian, Google OKF, IBM Docling, LegalProcessor v2, Python 3.x, Vector DBs, SHA-256",
            "web": "http://www.sha256.us/"
        }
    }


def analizar_archivo(ruta: str):
    """Determina automáticamente el tipo de archivo e identifica su encabezado."""
    if ruta.endswith(".bat"):
        res = identificar_encabezado_bat(ruta)
    elif ruta.endswith(".md"):
        res = identificar_encabezado_docling(ruta)
    else:
        res = {"valido": False, "error": "Formato no soportado directamente. Use .md o .bat"}
    
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analizar_archivo(sys.argv[1])
    else:
        print("=== PRUEBA DE IDENTIFICACIÓN DE ENCABEZADO CANÓNICO JULLBRAIN, UMIF, GRANITE & OKF ===")
        bat_res = identificar_encabezado_bat("header_canonico.bat")
        print("\n[Encabezado .BAT]:")
        print(json.dumps(bat_res, indent=2, ensure_ascii=False))
