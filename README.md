# Melhor Preço

Compare ofertas de produtos de supermercado retornadas pelo Google Shopping via SerpApi. A lista é ordenada pelo preço anunciado, com filtro por loja e opções para abrir ou copiar o link quando disponível. Confira o preço final, o estoque e o frete no site da loja.

## Executar localmente

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure `SERPAPI_API_KEY` no ambiente e execute `python app.py`. Abra `http://127.0.0.1:5000`. A interface abre sem a chave e a consulta retorna indisponibilidade até que ela seja configurada.

## Publicar a interface na Netlify

A interface em `public/` é estática. O Flask serve essa mesma interface localmente e no Render e responde à consulta `GET /api/ofertas?q=...`. Na Netlify, o build gera uma regra de proxy para o backend, mantendo a consulta na mesma origem da interface.

1. No Render, configure uma nova `SERPAPI_API_KEY` como variável de ambiente e publique o backend desta versão. Comandos de build e start: `pip install -r requirements.txt` e `gunicorn app:app`.
2. Confirme que `https://<backend>/api/ofertas?q=arroz` responde com JSON.
3. Importe este repositório na Netlify e adicione `API_ORIGIN` ao ambiente de build com a origem HTTPS do backend, por exemplo `https://nome-do-servico.onrender.com`, sem caminho adicional. A Netlify lê o comando de build e a pasta de publicação do `netlify.toml`.
4. Confira a busca na prévia de deploy da Netlify. Uma instância do Render que esteja suspensa pode demorar a acordar e ultrapassar o prazo do proxy.

A chave da SerpApi fica no ambiente do backend. Revogue no painel da SerpApi qualquer chave publicada anteriormente no histórico do GitHub.

## Evoluções

- Limitar o volume de buscas e armazenar resultados por um curto período para proteger a cota da SerpApi.
- Refinar a lista de lojas e comparar produtos de mesma marca, peso e volume. As ofertas atuais são ordenadas pelo valor anunciado de cada resultado.
- Incluir filtros por região e disponibilidade quando houver dados confiáveis de entrega.
