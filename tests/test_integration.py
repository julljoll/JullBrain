"""
test_integration.py — Suite de Pruebas de Integración para JullBrain Enterprise
Verifica la integración completa del pipeline legal:
Legalizer -> MetadataExtractor -> Validator -> GraniteEmbedder -> AuditLogger.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from legalizer import legalize
from metadata_extractor import extract_metadata, inject_frontmatter
from validator import validate_md_file
from granite_embedder import GraniteEmbedder
from audit_logger import AuditLogger


class TestPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AuditLogger()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_pipeline_flow(self):
        # 1. Simular Markdown crudo extraído de Docling
        raw_docling_md = (
            "# CODIGO ORGANICO PROCESAL PENAL\n\n"
            "Gaceta Oficial N° 6.644 Extraordinario de fecha 15 de septiembre de 2021\n\n"
            "## TITULO PRELIMINAR\n"
            "Principios y Garantias Procesales\n\n"
            "Articulo 1. Juicio previo y debido proceso. Nadie podra ser condenado sin un juicio previo, "
            "oral y publico, realizado sin dilaciones indebidas, ante un juez o jueza imparcial.\n\n"
            "Articulo 2. Ejercicio de la jurisdiccion. La potestad de administrar justicia penal emana de los ciudadanos.\n\n"
            "Articulo 3. Participacion ciudadana. Los ciudadanos y ciudadanas participan en la administracion de la justicia penal."
        )

        # 2. Paso Legalizer: Estructurar jerarquía venezolana
        legalized_md = legalize(raw_docling_md)
        self.assertIn("Articulo 1", legalized_md)
        self.assertIn("Articulo 2", legalized_md)

        # 3. Paso Metadata Extractor: Inyectar frontmatter YAML
        final_md = inject_frontmatter(legalized_md, filename="COPP_Test.md")
        self.assertTrue(final_md.startswith("---\n"))
        self.assertIn("tipo_instrumento: \"Codigo\"", final_md)
        self.assertIn("gaceta_oficial: \"6.644 Extraordinario\"", final_md)

        # 4. Guardar archivo procesado temporal para validación
        temp_file = Path(self.temp_dir) / "test_normativa.md"
        temp_file.write_text(final_md, encoding="utf-8")

        # 5. Paso Validator: Ejecutar validación de calidad
        report = validate_md_file(str(temp_file))
        self.assertEqual(report.articles_found, 3)
        self.assertEqual(len(report.sequence_gaps), 0)
        self.assertEqual(len(report.duplicates), 0)
        self.assertTrue(report.has_frontmatter)
        self.assertEqual(report.overall_status, "OK")

        # 6. Paso Audit Logger: Registrar en cadena de custodia
        audit_entry = self.logger.log_event(
            event_type="PIPELINE_CONVERSION_SUCCESS",
            user_id="test_suite_operator",
            action_details={
                "filename": "test_normativa.md",
                "articles_found": report.articles_found,
                "quality_score": report.quality_score
            }
        )
        self.assertIsNotNone(audit_entry.get("signature_hash"))
        self.assertTrue(self.logger.verify_audit_integrity(audit_entry))


if __name__ == "__main__":
    unittest.main()
