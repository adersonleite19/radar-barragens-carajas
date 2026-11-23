import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from dados.referencias import BARRAGEM_PADRAO
from simulacao.motor_rompimento import calcular_simulacao_rompimento

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BARRAGENS = os.path.join(BASE_DIR, "barragens_vale_pa.json")

TIPOS_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
}


def carregar_barragens():
    if not os.path.exists(ARQUIVO_BARRAGENS):
        return [BARRAGEM_PADRAO]
    with open(ARQUIVO_BARRAGENS, "r", encoding="utf-8") as f:
        dados = json.load(f)
    if isinstance(dados, dict) and "barragens" in dados:
        return dados["barragens"]
    if isinstance(dados, list):
        return dados
    return [BARRAGEM_PADRAO]


class ManipuladorBarragens(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def _enviar_json(self, status_code, payload):
        corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def _enviar_arquivo(self, nome_relativo):
        caminho_limpo = os.path.normpath(nome_relativo).lstrip("/")
        if caminho_limpo.startswith(".."):
            self._enviar_json(403, {"erro": "Acesso negado."})
            return

        caminho_completo = os.path.join(BASE_DIR, caminho_limpo)
        if not os.path.isfile(caminho_completo):
            self._enviar_json(404, {"erro": f"Arquivo não encontrado: {nome_relativo}"})
            return

        _, ext = os.path.splitext(caminho_completo.lower())
        content_type = TIPOS_MIME.get(ext, "application/octet-stream")

        with open(caminho_completo, "rb") as f:
            conteudo = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(conteudo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(conteudo)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        caminho = urlparse(self.path).path.rstrip("/") or "/"

        if caminho == "/api/barragens":
            barragens = carregar_barragens()
            self._enviar_json(200, {"barragens": barragens, "total": len(barragens)})
            return

        if caminho in ("/", "/inicio.html"):
            self._enviar_arquivo("inicio.html")
            return

        if caminho in ("/radar.html", "/index.html"):
            self._enviar_arquivo("index.html")
            return

        if caminho == "/barragens.html":
            self._enviar_arquivo("barragens.html")
            return

        if caminho == "/sobre.html":
            self._enviar_arquivo("sobre.html")
            return

        self._enviar_arquivo(caminho)

    def do_POST(self):
        caminho = urlparse(self.path).path
        if caminho != "/api/simular-rompimento":
            self._enviar_json(404, {"erro": "Endpoint não encontrado."})
            return

        tamanho = int(self.headers.get("Content-Length", "0"))
        corpo_bruto = self.rfile.read(tamanho) if tamanho > 0 else b"{}"

        try:
            dados_req = json.loads(corpo_bruto.decode("utf-8"))
        except Exception:
            self._enviar_json(400, {"erro": "JSON inválido na requisição."})
            return

        barragens = carregar_barragens()
        id_barragem = dados_req.get("barragem_id") or dados_req.get("id")
        barragem = next(
            (b for b in barragens if str(b.get("id")) == str(id_barragem)),
            None,
        )
        if barragem is None:
            barragem = barragens[0] if barragens else BARRAGEM_PADRAO

        try:
            percentual_ruptura = float(dados_req.get("percentual_ruptura", 50))
            velocidade_kmh = float(dados_req.get("velocidade_kmh", 25))
        except (TypeError, ValueError):
            self._enviar_json(400, {"erro": "Parâmetros numéricos inválidos."})
            return

        resultado = calcular_simulacao_rompimento(
            barragem=barragem,
            percentual_ruptura=percentual_ruptura,
            velocidade_kmh=velocidade_kmh,
        )
        self._enviar_json(200, resultado)


if __name__ == "__main__":
    host = "0.0.0.0"
    porta = int(os.environ.get("PORT", 8002))
    servidor = ThreadingHTTPServer((host, porta), ManipuladorBarragens)
    print(f"Servidor rodando em http://{host}:{porta}")
    servidor.serve_forever()
