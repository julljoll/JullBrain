"""
audit_logger.py — Sistema de Auditoría Inmutable y Registro de Eventos Criptográficos
JullBrain Enterprise Legal Platform
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("JullBrain.AuditLogger")
logger.setLevel(logging.INFO)

AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), "audit_trail.jsonl")


class AuditLogger:
    """
    Registrador de auditoría inmutable.
    Genera firmas SHA-256 para cada evento garantizando la no-alteración.
    """

    def __init__(self, db_connection=None):
        self.db_conn = db_connection
        self.secret_salt = os.getenv("JULLBRAIN_AUDIT_SALT", "EnterpriseLegalRAG_2026_Salt")

    def compute_signature(self, event_type: str, user_id: str, timestamp_utc: str, details_json: str) -> str:
        """Calcula la firma criptográfica SHA-256 del registro."""
        raw_data = f"{event_type}|{user_id}|{timestamp_utc}|{details_json}|{self.secret_salt}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def log_event(
        self,
        event_type: str,
        user_id: str,
        notebook_id: Optional[str] = None,
        action_details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """
        Registra un evento de auditoría con timestamp UTC y firma SHA-256.
        """
        if action_details is None:
            action_details = {}

        timestamp_utc = datetime.now(timezone.utc).isoformat()
        details_str = json.dumps(action_details, sort_keys=True)
        signature = self.compute_signature(event_type, user_id, timestamp_utc, details_str)

        log_entry = {
            "event_type": event_type,
            "user_id": user_id,
            "notebook_id": notebook_id,
            "action_details": action_details,
            "ip_address": ip_address,
            "timestamp_utc": timestamp_utc,
            "signature_hash": signature
        }

        # Persistencia en Base de Datos PostgreSQL si existe conexión
        if self.db_conn:
            try:
                with self.db_conn.cursor() as cursor:
                    query = """
                        INSERT INTO audit_logs (event_type, user_id, notebook_id, action_details, ip_address, timestamp_utc, signature_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(
                        query,
                        (event_type, user_id if user_id != "SYSTEM" else None, notebook_id, details_str, ip_address, timestamp_utc, signature)
                    )
                self.db_conn.commit()
            except Exception as e:
                logger.warning(f"No se pudo guardar auditoría en PostgreSQL: {e}. Usando archivo local JSONL fallback.")

        # Persistencia local fallback (JSONL append-only)
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Fallo crítico al escribir log de auditoría local: {e}")

        logger.info(f"[AUDIT] {event_type} | User: {user_id} | Notebook: {notebook_id} | SIG: {signature[:12]}...")
        return log_entry

    def verify_audit_integrity(self, log_entry: Dict[str, Any]) -> bool:
        """Verifica que un registro de auditoría no haya sido alterado."""
        expected_sig = log_entry.get("signature_hash")
        details_str = json.dumps(log_entry.get("action_details", {}), sort_keys=True)
        computed_sig = self.compute_signature(
            log_entry["event_type"],
            log_entry["user_id"],
            log_entry["timestamp_utc"],
            details_str
        )
        return expected_sig == computed_sig


# Instancia global por defecto
default_audit_logger = AuditLogger()
