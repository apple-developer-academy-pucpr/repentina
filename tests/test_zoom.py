import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from import_zoom import extract
from publish import validate_zoom


def payload():
    return {'mode': 'zoom', 'participants': [
        {'id': str(i), 'name': f'Pessoa Fictícia {i}', 'code': f'{i:04}'} for i in range(120)
    ]}


class ZoomTests(unittest.TestCase):
    def test_import_only_allowed_columns_and_preserve_zeroes(self):
        ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        def cell(address, text):
            return f'<c r="{address}" t="inlineStr"><is><t>{text}</t></is></c>'
        rows = ['<row r="1">'+cell('A1','cod')+cell('B1','nome')+cell('C1','cpf')+'</row>']
        for i in range(120):
            n = i+2
            # If the importer reads the document column, its formula guard fails.
            rows.append(f'<row r="{n}">'+cell(f'A{n}',f'{i:04}')+cell(f'B{n}',f'Pessoa Fictícia {i}')+f'<c r="C{n}"><f>PRIVATE_DOCUMENT</f></c></row>')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'fixture.xlsx'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="{ns}"><sheetData>'+''.join(rows)+'</sheetData></worksheet>')
            result = extract(path)
            self.assertEqual(result, payload())
            self.assertNotIn('cpf',json.dumps(result))
            self.assertNotIn('PRIVATE_DOCUMENT',json.dumps(result))

    def test_validation_rejects_duplicates_extra_fields_missing_and_invalid_codes(self):
        for variant in ('duplicate','extra','missing','numeric','long'):
            data = payload()
            if variant=='duplicate': data['participants'][1]['code']='0000'
            elif variant=='extra': data['participants'][0]['cpf']='PRIVATE_DOCUMENT'
            elif variant=='missing': data['participants'].pop()
            elif variant=='numeric': data['participants'][0]['code']=1
            else: data['participants'][0]['code']='12345678900'
            with self.assertRaises(ValueError): validate_zoom(data)

    def test_zoom_closed_round_transitions(self):
        from build import project
        from test_build import fixture
        with tempfile.TemporaryDirectory() as directory:
            for choice in ('Códigos do Zoom','Fechar página','2'):
                env=dict(os.environ,SELECTED_ROUND=choice)
                env.pop('ZOOM_DATA',None);env.pop('ROUND_DATA',None)
                if choice=='Códigos do Zoom':env['ZOOM_DATA']=json.dumps(payload())
                elif choice=='2':env['ROUND_DATA']=json.dumps(project(fixture(),2))
                result=subprocess.run([sys.executable,str(Path(__file__).with_name('publish.py'))],cwd=directory,env=env,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                state=json.loads((Path(directory)/'dist/current.json').read_text())
                self.assertNotIn('Pessoa Fictícia',(Path(directory)/'dist/index.html').read_text())
                if choice=='Códigos do Zoom': self.assertEqual(state,payload());self.assertNotIn('teams',state)
                elif choice=='Fechar página':self.assertEqual(state,{'closed':True})
                else:self.assertNotIn('code',state['participants'][0])
