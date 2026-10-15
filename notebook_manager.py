"""
notebook_manager.py — Gestor de Cuadernos/Expedientes Legal-RAG (Estilo NotebookLM)
JullBrain Enterprise Legal Platform
"""

import os
import uuid
import json
import shutil
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from audit_logger import default_audit_logger


class NotebookIntegrityError(Exception):
    """Excepción lanzada cuando la verificación de hash SHA-256 del cuaderno falla."""
    pass


class NotebookManager:
    """
    Administrador de Cuadernos (Expedientes Jurídicos aislados).
    Cada cuaderno posee su propio espacio de nombres, índice vectorial, notas e integridad SHA-256.
    """

    def __init__(self, storage_dir: str = "./RAG/notebooks_db", db_connection=None):
        self.storage_dir = os.path.abspath(storage_dir)
        self.db_conn = db_connection
        self.salt = os.getenv("JULLBRAIN_NOTEBOOK_SALT", "JullBrain_Legal_Salt_2026")
        os.makedirs(self.storage_dir, exist_ok=True)

    def calculate_notebook_hash(self, notebook_uuid: str, created_utc: str, name: str, user_id: str) -> str:
        """Calcula el hash SHA-256 inmutable del cuaderno."""
        raw = f"{notebook_uuid}|{created_utc}|{name}|{user_id}|{self.salt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def create_notebook(self, name: str, description: str, user_id: str) -> Dict[str, Any]:
        """
        Crea un nuevo expediente jurídico atado criptográficamente con SHA-256.
        """
        notebook_id = str(uuid.uuid4())
        created_utc = datetime.now(timezone.utc).isoformat()
        sha256_hash = self.calculate_notebook_hash(notebook_id, created_utc, name, user_id)

        notebook_meta = {
            "id": notebook_id,
            "name": name,
            "description": description,
            "user_id": user_id,
            "sha256_hash": sha256_hash,
            "created_at": created_utc,
            "updated_at": created_utc,
            "documents": [],
            "notes": []
        }

        # Directorio aislado del cuaderno
        nb_dir = os.path.join(self.storage_dir, notebook_id)
        os.makedirs(nb_dir, exist_ok=True)
        meta_file = os.path.join(nb_dir, "metadata.json")

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(notebook_meta, f, indent=2, ensure_ascii=False)

        # Auditoría
        default_audit_logger.log_event(
            event_type="CREATE_NOTEBOOK",
            user_id=user_id,
            notebook_id=notebook_id,
            action_details={"name": name, "sha256_hash": sha256_hash}
        )

        return notebook_meta

    def verify_and_load_notebook(self, notebook_id: str, user_id: str) -> Dict[str, Any]:
        """
        Carga un cuaderno verificando obligatoriamente su hash SHA-256.
        Si la firma difiere, rechaza la carga y registra un incidente de seguridad.
        """
        nb_dir = os.path.join(self.storage_dir, notebook_id)
        meta_file = os.path.join(nb_dir, "metadata.json")

        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"Expediente no encontrado: {notebook_id}")

        with open(meta_file, "r", encoding="utf-8") as f:
            notebook_meta = json.load(f)

        expected_hash = notebook_meta.get("sha256_hash")
        computed_hash = self.calculate_notebook_hash(
            notebook_meta["id"],
            notebook_meta["created_at"],
            notebook_meta["name"],
            notebook_meta["user_id"]
        )

        if expected_hash != computed_hash:
            default_audit_logger.log_event(
                event_type="SHA_VERIFICATION_FAILURE",
                user_id=user_id,
                notebook_id=notebook_id,
                action_details={
                    "expected_hash": expected_hash,
                    "computed_hash": computed_hash,
                    "alert": "Intento de apertura de expediente alterado o corrupto"
                }
            )
            raise NotebookIntegrityError(
                f"[ALERTA DE SEGURIDAD] La firma SHA-256 del cuaderno {notebook_id} no coincide. Acceso denegado."
            )

        default_audit_logger.log_event(
            event_type="READ_NOTEBOOK",
            user_id=user_id,
            notebook_id=notebook_id,
            action_details={"status": "SHA256_VERIFIED"}
        )

        return notebook_meta

    def delete_notebook_transactional(self, notebook_id: str, user_id: str) -> bool:
        """
        Elimina un cuaderno de forma transaccional (documentos, embeddings, caché, auditoría).
        Si alguna operación falla, ejecuta rollback.
        """
        nb_dir = os.path.join(self.storage_dir, notebook_id)
        backup_dir = f"{nb_dir}_backup_rollback"

        try:
            # Crear respaldo temporal para el rollback
            if os.path.exists(nb_dir):
                shutil.copytree(nb_dir, backup_dir)

            # Paso 1: Eliminar directorio de archivos e índices locales
            if os.path.exists(nb_dir):
                shutil.rmtree(nb_dir)

            # Paso 2: Registro en Auditoría Inmutable
            default_audit_logger.log_event(
                event_type="DELETE_NOTEBOOK",
                user_id=user_id,
                notebook_id=notebook_id,
                action_details={"status": "TRANSACTIONAL_DELETE_SUCCESS"}
            )

            # Limpiar respaldo de rollback
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

            return True

        except Exception as e:
            # ROLLBACK
            if os.path.exists(backup_dir) and not os.path.exists(nb_dir):
                shutil.copytree(backup_dir, nb_dir)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

            default_audit_logger.log_event(
                event_type="DELETE_NOTEBOOK_FAILED",
                user_id=user_id,
                notebook_id=notebook_id,
                action_details={"error": str(e), "status": "ROLLBACK_EXECUTED"}
            )
            raise RuntimeError(f"Fallo en la eliminación transaccional del cuaderno: {e}. Rollback ejecutado.")

    def list_notebooks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todos los cuadernos válidos en el sistema."""
        result = []
        if not os.path.exists(self.storage_dir):
            return result

        for item in os.listdir(self.storage_dir):
            meta_path = os.path.join(self.storage_dir, item, "metadata.json")
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if user_id is None or data.get("user_id") == user_id:
                            result.append(data)
                except Exception:
                    continue
        return result


# Instancia por defecto
default_notebook_manager = NotebookManager()
