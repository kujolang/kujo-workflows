import importlib.util
from pathlib import Path
import unittest

module_path = Path(__file__).resolve().parents[1] / 'workcell-execution-gate/scripts/configure_profile.py'
spec = importlib.util.spec_from_file_location('profile', module_path)
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class WorkcellProfileTests(unittest.TestCase):
    def test_identity_only_tracks_observed_rootless_signal(self):
        definition = {'workspace': {'strategy': 'git-worktree'}, 'network': {'mode': 'none'}, 'filesystem': {'read_only_root': True}, 'trust_profile': 'contained-standard'}
        for options, expected in [(['name=seccomp,profile=builtin', 'name=apparmor'], 'host'), (['name=seccomp,profile=builtin', 'name=rootless'], 'rootless'), (['name=notrootless'], 'host')]:
            selected = profile.configure(definition, options)
            self.assertEqual(selected['workspace'].pop('run_as'), expected)
            self.assertEqual(selected, definition)
        self.assertNotIn('run_as', definition['workspace'])

    def test_invalid_observation_rejected(self):
        for invalid in (None, {}, ['name=rootless', 1]):
            with self.assertRaises(ValueError):
                profile.configure({}, invalid)
