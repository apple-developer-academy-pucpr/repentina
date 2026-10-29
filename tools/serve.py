#!/usr/bin/env python3
"""Local administration: no backup, password, or future round served to visitors."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import parse_qs
from build import build, OUTPUT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    backup = json.loads(args.backup.read_text())
    token = secrets.token_urlsafe(32)
    active = 0
    build(backup, active)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, body, content_type='text/html; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body.encode())

        def local_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{args.port}', f'localhost:{args.port}'}

        def do_GET(self):
            if not self.local_host():
                return self.send(403, 'Host inválido.')
            if self.path in ('/', '/index.html'):
                return self.send(200, (OUTPUT / 'index.html').read_text())
            if self.path != '/admin':
                return self.send(404, 'Página não encontrada.')
            options = ''.join(f'<option value="{r}" {"selected" if r == active else ""}>Rodada {r}</option>' for r in range(5))
            self.send(200, f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle de rodada</title>
<style>body{{font:17px system-ui;background:#f4f6ef;color:#17372d;max-width:540px;margin:12vh auto;padding:24px}}select,button{{font:inherit;padding:12px;border-radius:8px;border:1px solid #aab99d}}button{{background:#17372d;color:white}}p{{line-height:1.6}}a{{color:inherit}}</style>
<h1>Controle de rodada</h1><p>Prévia local · rodada atual: <strong>{active}</strong></p>
<form method="post" action="/admin"><input type="hidden" name="token" value="{token}"><label for="round">Liberar </label><select id="round" name="round">{options}</select> <button>Aplicar na prévia</button></form>
<p><a href="/" target="_blank" rel="noopener">Abrir a página dos participantes ↗</a></p><p>Este painel altera somente a prévia neste computador. Nenhum dado é enviado ao GitHub. A publicação ainda não está configurada.</p></html>''')

        def do_POST(self):
            nonlocal active
            if not self.local_host() or self.path != '/admin':
                return self.send(403, 'Solicitação inválida.')
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length < 1024:
                    raise ValueError()
                form = parse_qs(self.rfile.read(length).decode())
                if not secrets.compare_digest(form.get('token', [''])[0], token):
                    return self.send(403, 'Token inválido.')
                selected = int(form['round'][0])
                if selected not in range(5):
                    raise ValueError()
                build(backup, selected)
                active = selected
            except (ValueError, KeyError):
                return self.send(400, 'Não foi possível aplicar a rodada. A anterior foi mantida.')
            self.send_response(303)
            self.send_header('Location', '/admin')
            self.end_headers()

    print(f'Painel local: http://127.0.0.1:{args.port}/admin', flush=True)
    HTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
