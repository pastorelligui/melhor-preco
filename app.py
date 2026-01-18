from flask import Flask, render_template, request
from serpapi import GoogleSearch

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
API_KEY = "9a0b81b580e2ef642dc8590adc7f564ffcb9d83d9f8ce3646a8d5af134633056" 

# Filtro de lojas de alimentos e limpeza
SITES_PERMITIDOS = [
    "carrefour", "pao de acucar", "extra", "coop", "nagumo", "sonda", "mambo", 
    "atacadão", "assai", "mercado", "clube extra", "tenda", "hirota", "baba",
    "swift", "lopes", "shibata", "trimais", "vovo zuzu", "peg pese"
]

def buscar_google_shopping(item):
    params = {
        "engine": "google_shopping",
        "q": item,
        "hl": "pt",
        "gl": "br",
        "api_key": API_KEY
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])
        
        lista_final = []
        for res in shopping_results:
            loja = res.get("source", "").lower()
            
            # FILTRO: Só adiciona se a loja estiver na nossa lista permitida
            if any(site in loja for site in SITES_PERMITIDOS):
                link = res.get("link") or res.get("product_link") or ""
                if link.startswith("/"):
                    link = "https://www.google.com" + link
                
                lista_final.append({
                    "loja": res.get("source", "Loja"),
                    "produto": res.get("title", "Produto"),
                    "preco_exibicao": res.get("price", "Consultar"),
                    "preco_num": res.get("extracted_price", 999999),
                    "link": link,
                    "thumbnail": res.get("thumbnail")
                })
        
        # Ordenar por menor preço
        return sorted(lista_final, key=lambda x: x['preco_num'])
    except Exception as e:
        print(f"Erro: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    item_buscado = ""
    if request.method == 'POST':
        item_buscado = request.form.get('item')
        if item_buscado:
            resultados = buscar_google_shopping(item_buscado)
    return render_template('index.html', resultados=resultados, item=item_buscado)

if __name__ == '__main__':
    app.run(debug=True)