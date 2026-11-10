"""
audit_logger.py — Sistema de Auditoría Forense Inmutable (ISO/IEC 27037, ISO/IEC 42001, NIST AI RMF)
Implementa:
1. Cadena de Custodia Criptográfica (Hash-Chaining HMAC-SHA256) donde cada registro enlaza el hash anterior.
2. Sellado y Verificación de Integridad de la Bóveda Local de Modelos IA (RAG/modelos_ia).
3. Validación Forense de Magic Bytes (%PDF-) para prevención de payloads maliciosos.
4. Comparación de firmas en tiempo constante (hmac.compare_digest) contra ataques de temporización.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG_DIR = BASE_DIR / "logs"
DEFAULT_VAULT_DIR = BASE_DIR / "RAG" / "modelos_ia"
GENESIS_HASH = "0" * 64


class AuditLogger:
    """
    Registrador forense con encadenamiento criptográfico HMAC-SHA256 (Blockchain-style Audit Log).
    Cada evento incluye `prev_hash`, `hmac_sha256` y `signature_hash`, impidiendo la alteración
    o borrado silencioso de registros intermedios.
    """

    def __init__(self, log_dir: Optional[str | Path] = None, secret_key: Optional[str] = None) -> None:
        self.log_dir = Path(log_dir or os.environ.get("JULLBRAIN_LOG_DIR", str(DEFAULT_LOG_DIR)))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit_forensic.jsonl"

        raw_secret = (
            secret_key
            or os.environ.get("JULLBRAIN_AUDIT_SECRET")
            or "JULLBRAIN-IBM-FORENSIC-ZERO-TRUST-KEY-2026"
        )
        self._secret_bytes = raw_secret.encode("utf-8")
        self._last_hash = self._recover_last_hash()

    def _recover_last_hash(self) -> str:
        """Recupera el último hash de la cadena existente o retorna el GENESIS_HASH."""
        if not self.log_file.exists():
            return GENESIS_HASH
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines:
                return GENESIS_HASH
            last_entry = json.loads(lines[-1])
            return str(last_entry.get("hmac_sha256") or last_entry.get("signature_hash") or GENESIS_HASH)
        except Exception:
            return GENESIS_HASH

    def _compute_hmac(self, payload: Dict[str, Any]) -> str:
        """Calcula el HMAC-SHA256 canónico de un diccionario excluyendo los campos de firma."""
        clean_payload = {
            k: v for k, v in payload.items() if k not in ("hmac_sha256", "signature_hash")
        }
        canonical = json.dumps(clean_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hmac.new(self._secret_bytes, canonical, hashlib.sha256).hexdigest()

    def log_event(
        self,
        event_type: str,
        actor: str = "system_local",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        document_sha256: Optional[str] = None,
        user_id: Optional[str] = None,
        notebook_id: Optional[str] = None,
        action_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Registra un evento en la cadena forense y retorna el registro firmado."""
        effective_actor = user_id or actor
        effective_details = action_details if action_details is not None else (details or {})

        entry: Dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": severity.upper(),
            "actor": effective_actor,
            "user_id": effective_actor,
            "notebook_id": notebook_id,
            "document_sha256": document_sha256,
            "details": effective_details,
            "action_details": effective_details,
            "prev_hash": self._last_hash,
            "standard": "ISO/IEC-27037:2012+NIST-AI-RMF",
        }
        signature = self._compute_hmac(entry)
        entry["hmac_sha256"] = signature
        entry["signature_hash"] = signature
        self._last_hash = signature

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def verify_audit_integrity(self, log_entry: Dict[str, Any]) -> bool:
        """Verifica en tiempo constante la firma HMAC-SHA256 de un único evento de auditoría."""
        recorded_sig = str(log_entry.get("hmac_sha256") or log_entry.get("signature_hash") or "")
        if not recorded_sig:
            return False
        expected_sig = self._compute_hmac(log_entry)
        return hmac.compare_digest(recorded_sig, expected_sig)

    def seal_and_verify_model_vault(self, vault_dir: str | Path = DEFAULT_VAULT_DIR, update_seal: bool = False) -> Dict[str, Any]:
        """Método de instancia que delega en seal_and_verify_model_vault()."""
        return seal_and_verify_model_vault(vault_dir=vault_dir, update_seal=update_seal)

    def verify_log_integrity(self) -> Dict[str, Any]:
        """
        Verifica criptográficamente toda la cadena de custodia (HMAC + eslabones prev_hash).
        Utiliza hmac.compare_digest para resistencia contra ataques side-channel.
        """
        if not self.log_file.exists():
            return {
                "valid": True,
                "total_events": 0,
                "corrupted_events": [],
                "broken_links": [],
                "status": "EMPTY_CHAIN",
            }

        corrupted: List[int] = []
        broken_links: List[int] = []
        expected_prev = GENESIS_HASH
        total = 0

        with open(self.log_file, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue
                total += 1
                try:
                    entry = json.loads(raw)
                    recorded_sig = str(entry.get("hmac_sha256") or entry.get("signature_hash") or "")
                    recorded_prev = str(entry.get("prev_hash", ""))

                    if not hmac.compare_digest(recorded_prev, expected_prev):
                        broken_links.append(idx)

                    expected_sig = self._compute_hmac(entry)
                    if not hmac.compare_digest(recorded_sig, expected_sig):
                        corrupted.append(idx)

                    expected_prev = recorded_sig
                except Exception:
                    corrupted.append(idx)

        is_valid = len(corrupted) == 0 and len(broken_links) == 0
        return {
            "valid": is_valid,
            "total_events": total,
            "corrupted_events": corrupted,
            "broken_links": broken_links,
            "last_chain_hash": expected_prev,
            "status": "CHAIN_VERIFIED" if is_valid else "TAMPERING_DETECTED",
        }


def compute_file_sha256(file_path: str | Path) -> str:
    """Calcula el hash SHA-256 de un archivo en bloques de 64 KB."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_pdf_magic_bytes(file_or_bytes: str | Path | bytes) -> Dict[str, Any]:
    """
    Inspección forense de cabecera binaria (%PDF-) para prevenir inyección de archivos
    falsificados o corruptos antes de procesarlos con IBM Docling.
    Acepta tanto una ruta (str | Path) como un buffer en memoria (bytes).
    """
    if isinstance(file_or_bytes, (bytes, bytearray)):
        size = len(file_or_bytes)
        if size < 64:
            return {"valid": False, "reason": "FILE_TOO_SMALL", "size_bytes": size}
        if b"%PDF-" not in file_or_bytes[:1024]:
            return {"valid": False, "reason": "INVALID_PDF_MAGIC_BYTES"}
        return {
            "valid": True,
            "reason": "VALID_PDF_SIGNATURE",
            "size_bytes": size,
            "sha256": hashlib.sha256(file_or_bytes).hexdigest(),
        }

    path = Path(file_or_bytes)
    if not path.exists() or not path.is_file():
        return {"valid": False, "reason": "FILE_NOT_FOUND", "path": str(path)}

    size = path.stat().st_size
    if size < 64:
        return {"valid": False, "reason": "FILE_TOO_SMALL", "size_bytes": size, "path": str(path)}

    with open(path, "rb") as f:
        header = f.read(1024)

    if b"%PDF-" not in header:
        return {"valid": False, "reason": "INVALID_PDF_MAGIC_BYTES", "path": str(path)}

    return {
        "valid": True,
        "reason": "VALID_PDF_SIGNATURE",
        "size_bytes": size,
        "sha256": compute_file_sha256(path),
        "path": str(path),
    }


def seal_and_verify_model_vault(vault_dir: str | Path = DEFAULT_VAULT_DIR, update_seal: bool = False) -> Dict[str, Any]:
    """
    Sella o verifica criptográficamente los pesos de modelos IA almacenados localmente en RAG/modelos_ia/.
    Garantiza que ningún archivo .safetensors, .bin, .gguf u .onnx haya sido envenenado (Model Tampering).
    """
    vault_path = Path(vault_dir)
    vault_path.mkdir(parents=True, exist_ok=True)
    manifest_path = vault_path / "vault_manifest_sha256.json"

    model_extensions = {".safetensors", ".bin", ".gguf", ".onnx", ".pt", ".pth", ".json"}
    current_files: Dict[str, str] = {}

    for root, _, files in os.walk(vault_path):
        for fname in sorted(files):
            fpath = Path(root) / fname
            if fpath.name == "vault_manifest_sha256.json" or fpath.name == ".gitkeep":
                continue
            if fpath.suffix.lower() in model_extensions:
                rel = str(fpath.relative_to(vault_path)).replace("\\", "/")
                current_files[rel] = compute_file_sha256(fpath)

    if update_seal or not manifest_path.exists():
        manifest_data = {
            "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
            "vault_directory": str(vault_path),
            "standard": "NIST-AI-RMF-1.0 / IBM-Zero-Trust-Model-Vault",
            "total_artifacts": len(current_files),
            "artifacts_sha256": current_files,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        return {
            "valid": True,
            "status": "VAULT_SEALED",
            "total_artifacts": len(current_files),
            "tampered_files": [],
        }

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            saved_manifest = json.load(f)
        saved_hashes: Dict[str, str] = saved_manifest.get("artifacts_sha256", {})
    except Exception as exc:
        return {"valid": False, "status": "MANIFEST_CORRUPTED", "error": str(exc), "tampered_files": []}

    tampered: List[str] = []
    for rel_path, expected_hash in saved_hashes.items():
        actual_hash = current_files.get(rel_path)
        if actual_hash is None or not hmac.compare_digest(actual_hash, expected_hash):
            tampered.append(rel_path)

    return {
        "valid": len(tampered) == 0,
        "status": "VAULT_VERIFIED" if len(tampered) == 0 else "MODEL_TAMPERING_DETECTED",
        "total_artifacts": len(current_files),
        "tampered_files": tampered,
    }


# Instancia global por defecto para compatibilidad transversal
default_audit_logger = AuditLogger()
