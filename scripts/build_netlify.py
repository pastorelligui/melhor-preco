"""Prepara a interface e a rota de busca para a Netlify."""

import os
import shutil
from pathlib import Path
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[1]
origin = os.environ.get("API_ORIGIN", "").strip().rstrip("/")
parsed = urlsplit(origin)
if (
    parsed.scheme != "https"
    or not parsed.hostname
    or parsed.username
    or parsed.password
    or parsed.path
    or parsed.query
    or parsed.fragment
    or any(char.isspace() for char in origin)
):
    raise SystemExit("Configure API_ORIGIN com a origem HTTPS do backend Flask (sem caminho).")

dist = root / "dist"
if dist.exists():
    shutil.rmtree(dist)
shutil.copytree(root / "public", dist)
(dist / "_redirects").write_text(f"/api/ofertas {origin}/api/ofertas 200\n", encoding="utf-8")
