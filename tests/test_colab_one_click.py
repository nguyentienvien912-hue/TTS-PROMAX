"""Offline checks of launcher safety and temporary UI patching."""
import importlib.util
import json
from pathlib import Path
from contextlib import contextmanager
from uuid import uuid4
import unittest
from unittest.mock import patch
import sys

spec = importlib.util.spec_from_file_location('colab_one_click', Path(__file__).parents[1] / 'scripts/colab_one_click.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

@contextmanager
def working_folder():
    # Use normal inherited permissions; Windows managed runtimes may reject
    # traversal into tempfile's mode-0700 directories.
    root = Path(__file__).resolve().parents[1] / '.colab-test-artifacts' / uuid4().hex
    root.mkdir(parents=True)
    yield str(root)

class ColabLauncherTests(unittest.TestCase):
    def test_preset_uses_young_american_male_design(self):
        sys.path.insert(0, str(Path(__file__).parents[1] / 'backend'))
        from core.archetypes import get_archetype
        voice = get_archetype(launcher.PRESET_ID)
        self.assertEqual(voice['instruct'], 'male, young adult, moderate pitch, american accent')
        self.assertEqual(voice['use_case'], 'conversational')
        self.assertFalse(voice['facets']['whisper'])

    def test_preset_reuses_server_materializer(self):
        from io import BytesIO
        payload = b'{"profile_id":"saved123", "name":"PROMAX Natural Conversations"}'
        with patch.object(launcher.urllib.request, 'urlopen', side_effect=[BytesIO(payload), BytesIO(payload)]) as call:
            first = launcher.ensure_preset_voice()
            self.assertEqual(first, launcher.ensure_preset_voice())
        for args in call.call_args_list:
            request = args.args[0]
            self.assertEqual(request.method, 'POST')
            self.assertIn('/archetypes/' + launcher.PRESET_ID + '/use?', request.full_url)
            self.assertIn('name=PROMAX+Natural+Conversations', request.full_url)
            self.assertEqual(args.kwargs['timeout'], 900)

    def test_preset_failure_is_actionable(self):
        with patch.object(launcher.urllib.request, 'urlopen', side_effect=OSError('GPU unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'GPU unavailable'):
                launcher.ensure_preset_voice()

    def test_invalid_preset_response_cannot_claim_ready(self):
        from io import BytesIO
        with patch.object(launcher.urllib.request, 'urlopen', return_value=BytesIO(b'{}')):
            with self.assertRaises(RuntimeError):
                launcher.ensure_preset_voice()

    def test_patch_is_opt_in_and_requires_models(self):
        with working_folder() as folder:
            root = Path(folder)
            path = root / 'electron/src/renderer/src/components/setup-gate.tsx'
            path.parent.mkdir(parents=True)
            path.write_text('const completed = setupWasCompleted();')
            with patch.object(launcher, 'REPO_DIR', root):
                launcher.prepare_colab_ui()
                first = path.read_text()
                self.assertIn('__WEB_DEPLOYMENT__', first)
                self.assertIn("VITE_TTS_PROMAX_QUICK_START === '1'", first)
                self.assertIn('status.data.models_ready === true', first)
                launcher.prepare_colab_ui()
                self.assertEqual(first, path.read_text())

    def test_unknown_source_is_not_silently_bypassed(self):
        with working_folder() as folder:
            root = Path(folder)
            path = root / 'electron/src/renderer/src/components/setup-gate.tsx'
            path.parent.mkdir(parents=True)
            path.write_text('changed upstream gate')
            with patch.object(launcher, 'REPO_DIR', root):
                with self.assertRaises(RuntimeError):
                    launcher.prepare_colab_ui()
            self.assertEqual(path.read_text(), 'changed upstream gate')

    def test_unreachable_backend_is_not_ready(self):
        with patch.object(launcher.urllib.request, 'urlopen', side_effect=OSError('offline')):
            self.assertIsNone(launcher.get_json('/health'))

    def test_health_response_is_parsed(self):
        from io import BytesIO
        with patch.object(launcher.urllib.request, 'urlopen', return_value=BytesIO(b'{"status":"ok"}')):
            self.assertEqual(launcher.get_json('/health'), {'status': 'ok'})

if __name__ == '__main__':
    unittest.main()
