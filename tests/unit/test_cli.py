"""Unit tests for continuity.cli.

Covers:
- Module entry point (python -m continuity)
- Console entry point (continuity)
- --help flag
- --version flag
- Unknown argument exits with non-zero code without traceback
"""

import subprocess
import sys
import unittest
import shutil


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run a command in a subprocess and capture output."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
    )


class TestModuleEntryPoint(unittest.TestCase):
    """python -m continuity invocation."""

    def test_help_exits_zero(self) -> None:
        result = _run(sys.executable, "-m", "continuity", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("continuity", result.stdout)

    def test_version_exits_zero(self) -> None:
        result = _run(sys.executable, "-m", "continuity", "--version")
        self.assertEqual(result.returncode, 0)
        # Version should be a non-empty string like "0.1.0"
        output = (result.stdout + result.stderr).strip()
        self.assertTrue(len(output) > 0, "version output should not be empty")

    def test_unknown_arg_exits_nonzero(self) -> None:
        result = _run(sys.executable, "-m", "continuity", "--unknown-flag-xyz")
        self.assertNotEqual(result.returncode, 0)
        # Must not include a Python traceback
        combined = result.stdout + result.stderr
        self.assertNotIn("Traceback", combined)


class TestConsoleEntryPoint(unittest.TestCase):
    """continuity console script invocation (requires editable install)."""

    def setUp(self) -> None:
        if shutil.which("continuity") is None:
            self.skipTest("continuity console script not found (requires editable install)")

    def test_help_exits_zero(self) -> None:
        result = _run("continuity", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("continuity", result.stdout)

    def test_version_exits_zero(self) -> None:
        result = _run("continuity", "--version")
        self.assertEqual(result.returncode, 0)
        output = (result.stdout + result.stderr).strip()
        self.assertTrue(len(output) > 0, "version output should not be empty")

    def test_unknown_arg_exits_nonzero(self) -> None:
        result = _run("continuity", "--unknown-flag-xyz")
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        self.assertNotIn("Traceback", combined)


class TestVersionValue(unittest.TestCase):
    """Version string consistency."""

    def test_import_version_is_string(self) -> None:
        import continuity

        self.assertIsInstance(continuity.__version__, str)
        self.assertTrue(len(continuity.__version__) > 0)

    def test_module_version_matches_import(self) -> None:
        import continuity

        result = _run(sys.executable, "-m", "continuity", "--version")
        output = (result.stdout + result.stderr).strip()
        self.assertIn(continuity.__version__, output)


if __name__ == "__main__":
    unittest.main()
