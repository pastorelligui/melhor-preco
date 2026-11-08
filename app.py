import json
import math
import os
import re
import unicodedata
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="public/static", static_url_path="/static")

LOJAS = (
    "carrefour", "pao de acucar", "extra", "coop", "nagumo", "sonda", "mambo",
    "atacadao", "assai", "mercado", "clube extra", "tenda", "hirota", "baba",
    "swift", "lopes", "shibata", "trimais", "vovo zuzu", "peg pese",
)


def normalizar(texto):
    sem_acentos = unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos).strip()


def url_https(valor, aceitar_relativo=False):
    if not isinstance(valor, str) or not valor:
        return None
    if aceitar_relativo and valor.startswith("/") and not valor.startswith("//"):
        valor = "https://www.google.com" + valor
    try:
        url = urlsplit(valor)
        if url.scheme == "https" and url.hostname and not (url.username or url.password):
            return valor
    except ValueError:
        pass
    return None


def formatar_ofertas(resultados):
    ofertas = []
    for resultado in resultados:
        loja = resultado.get("source")
        titulo = resultado.get("title")
        if not isinstance(loja, str) or not isinstance(titulo, str) or not titulo.strip():
            continue
        loja_normalizada = f" {normalizar(loja)} "
        if not any(f" {nome} " in loja_normalizada for nome in LOJAS):
            continue

        preco = resultado.get("extracted_price")
        if type(preco) not in (int, float) or not math.isfinite(preco) or preco <= 0:
            preco = None

        ofertas.append({
            "loja": loja,
            "produto": titulo,
            "preco": preco,
            "link": url_https(resultado.get("link"), aceitar_relativo=True)
            or url_https(resultado.get("product_link"), aceitar_relativo=True),
            "thumbnail": url_https(resultado.get("thumbnail")),
        })
    return sorted(ofertas, key=lambda oferta: oferta["preco"] if oferta["preco"] is not None else math.inf)


@app.get("/")
def index():
    return send_from_directory("public", "index.html")


@app.get("/api/ofertas")
def buscar_ofertas():
    item = request.args.get("q", "").strip()
    if not 2 <= len(item) <= 120:
        return jsonify(erro="Digite um produto com 2 a 120 caracteres."), 400

    chave = os.environ.get("SERPAPI_API_KEY")
    if not chave:
        app.logger.error("SERPAPI_API_KEY ausente.")
        return jsonify(erro="A busca está temporariamente indisponível. Tente novamente mais tarde."), 503

    parametros = urlencode({
        "engine": "google_shopping", "q": item, "hl": "pt", "gl": "br", "api_key": chave,
    })
    try:
        with urlopen(f"https://serpapi.com/search.json?{parametros}", timeout=12) as resposta:
            dados = json.load(resposta)
        if dados.get("error") or dados.get("search_metadata", {}).get("status") == "Error":
            raise ValueError("Falha na busca")
        return jsonify(ofertas=formatar_ofertas(dados.get("shopping_results", [])))
    except (URLError, OSError, ValueError, AttributeError, TypeError) as erro:
        app.logger.warning("Falha na consulta à SerpApi (%s).", type(erro).__name__)
        return jsonify(erro="Não foi possível consultar as ofertas agora. Tente novamente."), 502


if __name__ == "__main__":
    app.run()
