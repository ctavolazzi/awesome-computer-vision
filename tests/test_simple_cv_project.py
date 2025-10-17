"""Regression tests for the simple CV project MVP."""

from __future__ import annotations

import json
import threading
from contextlib import closing
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from examples.simple_cv_project import main as pipeline
from examples.simple_cv_project import server


EXPECTED_SUMMARY_IMAGES = {
    "scene": {"min": 40, "max": 210, "mean": 145.51},
    "grayscale": {"min": 40, "max": 210, "mean": 145.51},
    "blurred": {"min": 52, "max": 210, "mean": 145.51},
    "edges": {"min": 0, "max": 255, "mean": 31.07},
    "corners": {"min": 40, "max": 210, "mean": 145.42},
}


class PipelineTests(unittest.TestCase):
    def test_summary_matches_expected_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            scene = pipeline.create_synthetic_scene(size=128)
            outputs = pipeline.run_pipeline(scene)
            summary = pipeline.save_outputs(outputs, output_dir)

            self.assertEqual(summary["images"], EXPECTED_SUMMARY_IMAGES)
            self.assertEqual(summary["meta"], {"width": 128, "height": 128, "size": 128})
            self.assertIn("generated_at", summary)

    def test_pipeline_is_deterministic(self) -> None:
        scene_a = pipeline.create_synthetic_scene(size=128)
        scene_b = pipeline.create_synthetic_scene(size=128)
        outputs_a = pipeline.run_pipeline(scene_a)
        outputs_b = pipeline.run_pipeline(scene_b)

        with TemporaryDirectory() as tmpdir:
            summary_a = pipeline.save_outputs(outputs_a, Path(tmpdir) / "first")
            summary_b = pipeline.save_outputs(outputs_b, Path(tmpdir) / "second")

        self.assertEqual(summary_a["images"], summary_b["images"])
        self.assertEqual(summary_a["meta"], summary_b["meta"])


class ServerTests(unittest.TestCase):
    def test_regeneration_endpoint_returns_summary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            summary = server.ensure_outputs(output_dir, size=128)
            self.assertEqual(summary["meta"]["size"], 128)

            host, port = server.pick_port("127.0.0.1", 0)

            with server.serve(server.PROJECT_DIR, host, port, output_dir=output_dir) as httpd:
                thread = threading.Thread(target=httpd.serve_forever, daemon=True)
                thread.start()
                try:
                    with closing(
                        HTTPConnection(host, port, timeout=10)
                    ) as connection:
                        payload = json.dumps({"size": 128}).encode("utf-8")
                        connection.request(
                            "POST",
                            "/api/regenerate",
                            body=payload,
                            headers={"Content-Type": "application/json"},
                        )
                        response = connection.getresponse()
                        body = response.read().decode("utf-8")

                    self.assertEqual(response.status, 200, msg=body)
                    data = json.loads(body)
                    self.assertTrue(data.get("ok"))
                    self.assertEqual(data["size"], 128)
                    self.assertIn("summary", data)
                    self.assertEqual(
                        data["summary"]["meta"].get("size"),
                        128,
                    )
                finally:
                    httpd.shutdown()
                    thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
