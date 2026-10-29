# Repentina · Apple Developer Academy PUCPR

Site público: https://apple-developer-academy-pucpr.github.io/repentina/

## Operação

No GitHub, abra **Actions → Controlar página da Repentina → Run workflow**.
Escolha uma rodada (0 a 4), **Códigos do Zoom** ou **Fechar página**. Aguarde o
workflow terminar com sucesso. Apenas pessoas com acesso de escrita ao repo
podem executar ações. A página consulta o estado atual sem cache e apaga o
conteúdo quando fechada. Isso não revoga cópias já salvas por visitantes.

O site entrega apenas o modo selecionado. Rodadas e códigos são secrets do
Actions. O workflow de rodadas lê `ROUND_0` a `ROUND_4`; Zoom lê `ZOOM_CODES`.
Ao fechar, não carrega secrets e publica apenas `{"closed": true}` em
`current.json`. A planilha-fonte e CPF nunca devem ser commitados.

## Atualizar códigos do Zoom

A raiz guarda o site (`index.html`, `publish.py`), o workflow em
`.github/workflows/change-round.yml` e código de manutenção abaixo.

`tools/import_zoom.py` lê somente as colunas `cod` e `nome`, valida 120 códigos
únicos com quatro dígitos e grava a projeção em `private-data/zoom-codes.json`.

```sh
python3 tools/import_zoom.py /caminho/candidatos_codigos.xlsx
```

O arquivo gerado é local e ignorado pelo Git. Nunca use o workbook como artefato,
entrada de log, commit ou upload. Para implantar uma nova lista, revisar a
projeção local e atualizar o secret GitHub Actions `ZOOM_CODES`.

## Prévia local e testes

```sh
python3 tools/serve.py /caminho/hackathon-backup.json
PYTHONPATH=tools python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_ui.cjs
node tests/test_sync.cjs
```

O backup também fica local. Use apenas dados fictícios em testes e nunca envie
nomes ou códigos reais para logs de CI.
