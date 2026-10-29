import copy
import json
from pathlib import Path
import tempfile
import unittest
from build import build, project


def fixture():
    participants = [{'id': f'private-id-{i}', 'name': f'Pessoa Fictícia {i:03}', 'age': 'PRIVATE_AGE'} for i in range(120)]
    rounds = []
    previous = None
    for sequence in range(5):
        positions = {p['id']: ((i // 4 + (sequence if i % 4 == 0 else 0)) % 30) + 1 for i, p in enumerate(participants)}
        tables = [{'number': t, 'candidateIDs': [p for p, n in positions.items() if n == t]} for t in range(1, 31)]
        movements = [] if previous is None else [{'candidateID': p, 'fromTable': previous[p], 'toTable': t} for p, t in positions.items() if previous[p] != t]
        rounds.append({'sequence': sequence, 'tables': tables, 'movements': movements})
        previous = positions
    return {'state': {'proposal': {'event': {'participants': participants}, 'rounds': rounds}, 'token': 'PRIVATE_TOKEN'}}


class ProjectionTests(unittest.TestCase):
    def test_all_rounds_and_transitions(self):
        backup = fixture()
        untouched = copy.deepcopy(backup)
        for sequence in range(5):
            data = project(backup, sequence)
            self.assertEqual(len(data['teams']), 30)
            self.assertEqual(len(data['participants']), 120)
            changed = [p for p in data['participants'] if p['from'] != p['to']]
            self.assertEqual(len(changed), 30 if sequence else 0)
            for team in data['teams']:
                self.assertEqual(sum(p['to'] == team for p in data['participants']), 4)
        self.assertEqual(backup, untouched)

    def test_missing_round_or_previous(self):
        for sequence in (1, 2):
            backup = fixture()
            del backup['state']['proposal']['rounds'][1]
            with self.assertRaises(ValueError):
                project(backup, sequence)

    def test_duplicate_unknown_and_missing_participant(self):
        for replacement in ('private-id-4', 'unknown', None):
            backup = fixture()
            members = backup['state']['proposal']['rounds'][0]['tables'][0]['candidateIDs']
            if replacement is None:
                members.pop()
            else:
                members[0] = replacement
            with self.assertRaises(ValueError):
                project(backup, 0)

    def test_inconsistent_movement(self):
        backup = fixture()
        backup['state']['proposal']['rounds'][1]['movements'][0]['toTable'] = 30
        with self.assertRaises(ValueError):
            project(backup, 1)

    def test_only_current_projection_and_no_script_injection(self):
        backup = fixture()
        backup['state']['proposal']['event']['participants'][0]['name'] = '</script><script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as directory:
            build(backup, 1, directory)
            html = (Path(directory) / 'index.html').read_text()
            for secret in ('PRIVATE_TOKEN', 'PRIVATE_AGE', 'private-id-', '</script><script>alert', 'officialRounds', 'proposal'):
                self.assertNotIn(secret, html)
            payload = html.split('let data=', 1)[1].split(';\nconst $', 1)[0]
            self.assertEqual(json.loads(payload)['round'], 1)
            build(backup, 4, directory)
            html = (Path(directory) / 'index.html').read_text()
            self.assertEqual(json.loads(html.split('let data=', 1)[1].split(';\nconst $', 1)[0])['round'], 4)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ['index.html'])

    def test_failed_build_preserves_previous(self):
        with tempfile.TemporaryDirectory() as directory:
            build(fixture(), 0, directory)
            before = (Path(directory) / 'index.html').read_bytes()
            with self.assertRaises(ValueError):
                build(fixture(), 9, directory)
            self.assertEqual((Path(directory) / 'index.html').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
