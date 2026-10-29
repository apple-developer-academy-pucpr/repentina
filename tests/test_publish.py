import unittest
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from build import project
from publish import render
from test_build import fixture


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.template = Path(__file__).with_name('index.html').read_text()

    def test_each_round_is_standalone(self):
        for number in range(5):
            html = render(project(fixture(), number), number, self.template)
            self.assertIn(f'"round": {number}', html)
            self.assertNotIn('PRIVATE_TOKEN', html)
            self.assertNotIn('PRIVATE_AGE', html)

    def test_close_without_secret_and_reopen(self):
        script = Path(__file__).with_name('publish.py')
        with tempfile.TemporaryDirectory() as directory:
            for choice in ('0', 'Fechar página', '3'):
                env = dict(os.environ, SELECTED_ROUND=choice)
                env.pop('ROUND_DATA', None)
                if choice != 'Fechar página':
                    env['ROUND_DATA'] = json.dumps(project(fixture(), int(choice)))
                result = subprocess.run([sys.executable, str(script)], cwd=directory, env=env, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                html = (Path(directory) / 'dist/index.html').read_text()
                state = json.loads((Path(directory) / 'dist/current.json').read_text())
                self.assertNotIn('Pessoa Fictícia', html)
                self.assertIn('let data=null;', html)
                if choice == 'Fechar página':
                    self.assertIn('Página indisponível', html)
                    self.assertEqual(state, {'closed': True})
                else:
                    self.assertEqual(state['round'], int(choice))

    def test_invalid_release_preserves_page(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            output.mkdir()
            (output / 'index.html').write_text('previous page')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('publish.py'))], cwd=directory,
                env=dict(os.environ, SELECTED_ROUND='2', ROUND_DATA='invalid'), capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((output / 'index.html').read_text(), 'previous page')

    def test_mismatch_or_additional_data_rejected(self):
        data = project(fixture(), 2)
        with self.assertRaises(ValueError):
            render(data, 3, self.template)
        data['backup'] = fixture()
        with self.assertRaises(ValueError):
            render(data, 2, self.template)

    def test_incomplete_or_unbalanced_teams_rejected(self):
        for change in ('missing', 'unbalanced', 'duplicate'):
            data = project(fixture(), 2)
            if change == 'missing':
                data['participants'].pop()
            elif change == 'duplicate':
                data['participants'][0]['id'] = data['participants'][1]['id']
            else:
                data['participants'][0]['to'] = 30
            with self.assertRaises(ValueError):
                render(data, 2, self.template)


if __name__ == '__main__':
    unittest.main()
