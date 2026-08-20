"""Module tests."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from machado.scripts.startproject import main


class StartProjectScriptTest(unittest.TestCase):
    """Test suite for StartProjectScript."""

    def test_main(self):
        """Test main."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_args = ["machado-startproject", tmpdir, "--verbosity=0"]
            with patch.object(sys, "argv", test_args):
                main()

            target = Path(tmpdir)
            self.assertTrue((target / ".env.example").exists())
            self.assertTrue((target / ".env").exists())
            self.assertTrue((target / "manage.py").exists())

    def test_main_overwrite(self):
        """Test main overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_args = ["machado-startproject", tmpdir, "--verbosity=0"]
            with patch.object(sys, "argv", test_args):
                main()

            # Running again without --overwrite
            with patch.object(sys, "argv", test_args):
                main()

            # Running with --overwrite
            test_args_overwrite = [
                "machado-startproject",
                tmpdir,
                "--overwrite",
                "--verbosity=0",
            ]
            with patch.object(sys, "argv", test_args_overwrite):
                main()

            target = Path(tmpdir)
            self.assertTrue((target / ".env").exists())


class EnvExampleDriftTest(unittest.TestCase):
    """The generated .env must document every landing-page setting.

    _ENV_EXAMPLE duplicates the setting names already declared in
    context_processors.DEFAULTS, so it can drift silently -- it documented
    none of the 20 pre-existing settings before this test existed, including
    MACHADO_ACCENT_COLOR, which is why an operator had to hand-edit it in.
    Comparing against DEFAULTS.keys() rather than a hardcoded list means the
    next new setting fails this test immediately if _ENV_EXAMPLE isn't
    updated, instead of silently repeating the same gap.
    """

    def test_every_default_key_is_documented(self):
        """Every context_processors.DEFAULTS key appears in _ENV_EXAMPLE."""
        import re

        from machado import context_processors
        from machado.scripts.startproject import _ENV_EXAMPLE

        documented = set(
            re.findall(r"^#?\s*(MACHADO_[A-Z0-9_]+)=", _ENV_EXAMPLE, re.MULTILINE)
        )
        expected = set(context_processors.DEFAULTS.keys())
        missing = expected - documented
        self.assertEqual(
            missing,
            set(),
            f"these DEFAULTS keys are not documented in _ENV_EXAMPLE: {missing}",
        )
