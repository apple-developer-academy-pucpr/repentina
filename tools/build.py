#!/usr/bin/env python3
"""Export only one round; the backup never becomes a website asset."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / 'private-data' / 'team-changes-preview'


def project(backup, sequence):
    state = backup['state']
    rounds = state['proposal']['rounds']
    by_sequence = {r['sequence']: r for r in rounds}
    if len(by_sequence) != len(rounds) or sequence not in by_sequence:
        raise ValueError('Rodada ausente ou sequência duplicada.')
    participants = state['proposal']['event']['participants']
    names = {p['id']: p['name'] for p in participants}
    if len(names) != len(participants) or any(not isinstance(n, str) or not n.strip() for n in names.values()):
        raise ValueError('Participantes duplicados ou sem nome.')

    def positions(r):
        result = {}
        table_numbers = set()
        for table in r['tables']:
            number = table['number']
            if not isinstance(number, int) or number in table_numbers:
                raise ValueError('Número de time inválido ou duplicado.')
            table_numbers.add(number)
            for candidate in table['candidateIDs']:
                if candidate not in names or candidate in result:
                    raise ValueError('Participante desconhecido ou repetido na rodada.')
                result[candidate] = number
        if set(result) != set(names):
            raise ValueError('A rodada não inclui todos os participantes.')
        return result, table_numbers

    current, numbers = positions(by_sequence[sequence])
    previous = current
    if sequence:
        if sequence - 1 not in by_sequence:
            raise ValueError('Rodada anterior ausente; não é possível calcular as trocas.')
        previous, previous_numbers = positions(by_sequence[sequence - 1])
        if previous_numbers != numbers:
            raise ValueError('Os times mudaram entre as rodadas.')
    # Compute the transition from memberships, and verify the exported movements.
    changes = {(p, previous[p], current[p]) for p in current if previous[p] != current[p]}
    recorded = by_sequence[sequence].get('movements', [])
    supplied = {(m['candidateID'], m['fromTable'], m['toTable']) for m in recorded}
    if supplied != changes or len(supplied) != len(recorded):
        raise ValueError('As movimentações não correspondem à transição entre times.')
    # Opaque local indices, never CloudKit IDs or additional participant fields.
    ids = {p: str(i) for i, p in enumerate(names)}
    return {
        'round': sequence,
        'participants': [{'id': ids[p], 'name': names[p], 'from': previous[p], 'to': current[p]} for p in names],
        'teams': sorted(numbers),
    }


def build(backup, sequence, output=OUTPUT):
    data = project(backup, sequence)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    # JSON in a script element must escape '<' to prevent closing the element.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    html = (ROOT / 'index.html').read_text().replace('/*__ROUND_DATA__*/null', payload)
    temporary = output / '.index.html.tmp'
    temporary.write_text(html)
    temporary.replace(output / 'index.html')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--round', type=int, required=True, choices=range(5))
    args = parser.parse_args()
    build(json.loads(args.backup.read_text()), args.round)
    print(f'Rodada {args.round} gerada em {OUTPUT}; nenhuma publicação realizada.')
