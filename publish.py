#!/usr/bin/env python3
"""Build Pages from the selected round secret, without logging personal data."""
import json
import os
from pathlib import Path
import sys


def validate_zoom(payload):
    if set(payload) != {'mode', 'participants'} or payload['mode'] != 'zoom' or not isinstance(payload['participants'], list) or len(payload['participants']) != 120:
        raise ValueError('Dados do Zoom inválidos.')
    ids, codes, names = set(), set(), set()
    for person in payload['participants']:
        if set(person) != {'id', 'name', 'code'}:
            raise ValueError('Campos não permitidos no modo Zoom.')
        if any(not isinstance(person[key], str) or not person[key].strip() for key in ('id', 'name', 'code')):
            raise ValueError('Código ou nome ausente.')
        if not person['code'].isascii() or not person['code'].isdigit() or len(person['code']) != 4:
            raise ValueError('Código deve conter quatro dígitos.')
        if person['id'] in ids or person['code'] in codes or person['name'].strip().casefold() in names:
            raise ValueError('Registro duplicado no modo Zoom.')
        ids.add(person['id']); codes.add(person['code']); names.add(person['name'].strip().casefold())


def render(payload, selected, template):
    if selected not in range(5) or set(payload) != {'round', 'teams', 'participants'} or payload['round'] != selected:
        raise ValueError('Rodada inválida.')
    if payload['teams'] != list(range(1, 31)) or len(payload['participants']) != 120:
        raise ValueError('Quantidade de times ou participantes inválida.')
    ids = set()
    counts = {side: {team: 0 for team in payload['teams']} for side in ('from', 'to')}
    for person in payload['participants']:
        if set(person) != {'id', 'name', 'from', 'to'}:
            raise ValueError('Campos não permitidos.')
        if not isinstance(person['id'], str) or person['id'] in ids:
            raise ValueError('Identificador inválido.')
        ids.add(person['id'])
        if not isinstance(person['name'], str) or not person['name'].strip():
            raise ValueError('Nome ausente.')
        for side in counts:
            if type(person[side]) is not int or person[side] not in counts[side]:
                raise ValueError('Time inválido.')
            counts[side][person[side]] += 1
        if selected == 0 and person['from'] != person['to']:
            raise ValueError('A rodada inicial não pode ter trocas.')
    if any(count != 4 for side in counts.values() for count in side.values()):
        raise ValueError('Cada time deve ter quatro integrantes.')
    marker = '/*__ROUND_DATA__*/null'
    if template.count(marker) != 1:
        raise ValueError('Template inválido.')
    return template.replace(marker, json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c'))


def main():
    try:
        choice = os.environ['SELECTED_ROUND']
        template = Path(__file__).with_name('index.html').read_text()
        if choice == 'Fechar página':
            payload = {'closed': True}
        elif choice == 'Códigos do Zoom':
            payload = json.loads(os.environ['ZOOM_DATA'])
            validate_zoom(payload)
        else:
            selected = int(choice)
            payload = json.loads(os.environ['ROUND_DATA'])
            render(payload, selected, template)  # validate without embedding data
        html = template.replace('/*__ROUND_DATA__*/null', 'null')
    except (ValueError, KeyError, TypeError):
        print('Não foi possível validar os dados. Confira o secret correspondente; a publicação anterior será mantida.', file=sys.stderr)
        return 1
    output = Path('dist')
    output.mkdir(exist_ok=True)
    (output / 'index.html').write_text(html)
    (output / 'current.json').write_text(json.dumps(payload, ensure_ascii=False))
    print('Página validada. Pronta para publicação.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
