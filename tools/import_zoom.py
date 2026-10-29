"""Read only code and name columns; never include the workbook in deployment."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from publish import validate_zoom

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def extract(path):
    with zipfile.ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rows = ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('.//m:sheetData/m:row', NS)

        def value(cell):
            if cell.find('m:f', NS) is not None:
                raise ValueError('Fórmulas não são aceitas nas colunas de código e nome.')
            if cell.get('t') == 'inlineStr':
                return ''.join(cell.find('m:is', NS).itertext()).strip()
            node = cell.find('m:v', NS)
            raw = node.text if node is not None else ''
            return (shared[int(raw)] if cell.get('t') == 's' else raw).strip()

        headers = {''.join(c for c in cell.get('r') if c.isalpha()): value(cell).casefold() for cell in rows[0]}
        columns = {label: col for col, label in headers.items() if label in ('cod', 'nome')}
        if set(columns) != {'cod', 'nome'}:
            raise ValueError('Colunas cod e nome não encontradas.')
        participants = []
        for row in rows[1:]:
            cells = {''.join(c for c in cell.get('r') if c.isalpha()): cell for cell in row}
            # Do not extract any other column, including personal document numbers.
            code = value(cells[columns['cod']]) if columns['cod'] in cells else ''
            name = value(cells[columns['nome']]) if columns['nome'] in cells else ''
            if not code and not name:
                continue
            participants.append({'id': str(len(participants)), 'name': name, 'code': code})
    payload = {'mode': 'zoom', 'participants': participants}
    validate_zoom(payload)
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', type=Path)
    args = parser.parse_args()
    payload = extract(args.workbook)
    output = Path(__file__).resolve().parent.parent / 'private-data' / 'zoom-codes.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False))
    print('120 códigos validados; projeção salva apenas em private-data.')
