"""
test_integration.py — Suite de Pruebas de Integración para JullBrain Enterprise
"""

import sys
import os
import unittest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openwebui_pipeline import Pipeline
from notebook_manager import NotebookManager


class TestPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline()

    def test_openwebui_pipeline_execution(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.pipeline.on_startup())

        user_message = "¿Qué especifica el artículo 15 sobre auditoría interna?"
        body = {
            "user": {"id": "integration_test_user"},
            "notebook_id": "test_expediente"
        }

        response = self.pipeline.pipe(
            user_message=user_message,
            model_id=self.pipeline.valves.GRANITE_MODEL,
            messages=[{"role": "user", "content": user_message}],
            body=body
        )

        self.assertIsInstance(response, str)
        self.assertTrue(
            "No encontré evidencia suficiente" in response or "Respuesta Basada en Evidencia" in response
        )

        loop.run_until_complete(self.pipeline.on_shutdown())


if __name__ == "__main__":
    unittest.main()
