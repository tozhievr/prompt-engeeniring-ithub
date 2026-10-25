import tempfile
from pathlib import Path
import unittest
from scripts.project_ci import validate, build

class ProjectCITests(unittest.TestCase):
    def test_missing_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / "demo-game"
            project.mkdir()
            self.assertTrue(any("missing index.html" in x for x in validate(project)))

    def test_valid_minimal_project(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / "demo-game"
            project.mkdir()
            (project / "index.html").write_text("<html><head><title>Demo</title></head></html>")
            (project / "README.md").write_text("# Demo")
            self.assertEqual(validate(project), [])
            output = Path(d) / "site"
            build(output, [project])
            self.assertTrue((output / "projects" / "demo-game" / "index.html").is_file())
            self.assertIn("demo-game", (output / "manifest.json").read_text())

if __name__ == "__main__":
    unittest.main()
