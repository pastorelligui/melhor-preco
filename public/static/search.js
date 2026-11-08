const form = document.querySelector("#search-form");
const input = document.querySelector("#query");
const results = document.querySelector("#results");
const title = document.querySelector("#results-title");
const note = document.querySelector("#results-note");
const announcement = document.querySelector("#announcement");
const feedback = document.querySelector("#feedback");
const feedbackText = document.querySelector("#feedback-text");
const spinner = document.querySelector(".spinner");
const retry = document.querySelector("#retry");
const storeControl = document.querySelector("#store-control");
const store = document.querySelector("#store");
const list = document.querySelector("#offers");
const template = document.querySelector("#offer-template");
const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const collator = new Intl.Collator("pt-BR");

let offers = [];
let pending;
let lastQuery = "";

function showFeedback(message, { loading = false, canRetry = false } = {}) {
  feedback.hidden = !message;
  feedbackText.textContent = message;
  spinner.hidden = !loading;
  retry.hidden = !canRetry;
  announcement.textContent = message;
}

function renderOffers() {
  const visible = store.selectedIndex > 0
    ? offers.filter((offer) => offer.loja === store.value)
    : offers;
  const count = visible.length === 1 ? "1 oferta" : `${visible.length} ofertas`;
  note.textContent = `${count} · Menor preço primeiro`;
  announcement.textContent = note.textContent;
  const cards = visible.map((offer) => {
    const card = template.content.firstElementChild.cloneNode(true);
    card.querySelector(".store").textContent = offer.loja;
    card.querySelector(".product").textContent = offer.produto;
    const price = card.querySelector(".price");
    price.textContent = offer.preco === null ? "Preço sob consulta" : currency.format(offer.preco);
    price.classList.toggle("unavailable", offer.preco === null);

    if (offer.thumbnail) {
      const imageBox = card.querySelector(".offer-image");
      const icon = imageBox.querySelector("svg");
      const image = new Image();
      image.alt = "";
      image.loading = "lazy";
      image.addEventListener("load", () => { icon.hidden = true; }, { once: true });
      image.addEventListener("error", () => image.remove(), { once: true });
      image.src = offer.thumbnail;
      imageBox.append(image);
    }

    if (offer.link) {
      const visit = card.querySelector(".visit");
      visit.href = offer.link;
      visit.hidden = false;
      visit.setAttribute("aria-label", `Ver oferta de ${offer.produto} em nova aba`);
      const copy = card.querySelector(".copy");
      copy.hidden = false;
      copy.setAttribute("aria-label", `Copiar link de ${offer.produto}`);
      let resetCopy;
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(offer.link);
          copy.textContent = "Link copiado";
          copy.setAttribute("aria-label", `Link de ${offer.produto} copiado`);
          announcement.textContent = "Link da oferta copiado.";
          clearTimeout(resetCopy);
          resetCopy = setTimeout(() => {
            copy.textContent = "Copiar link";
            copy.setAttribute("aria-label", `Copiar link de ${offer.produto}`);
          }, 2000);
        } catch {
          announcement.textContent = "Não foi possível copiar o link. Use Ver oferta para abri-lo.";
          copy.textContent = "Falha ao copiar";
          copy.setAttribute("aria-label", `Falha ao copiar. Tentar novamente para ${offer.produto}`);
        }
      });
    } else {
      card.querySelector(".offer-actions").remove();
    }
    return card;
  });
  list.replaceChildren(...cards);
}

async function search(query) {
  if (pending && query === lastQuery) return;
  pending?.abort();
  const controller = new AbortController();
  pending = controller;
  lastQuery = query;
  input.value = query;

  title.textContent = `Ofertas para “${query}”`;
  results.hidden = false;
  storeControl.hidden = true;
  list.replaceChildren();
  note.textContent = "";
  title.focus();
  showFeedback("Buscando ofertas…", { loading: true });

  try {
    const params = new URLSearchParams({ q: query });
    const response = await fetch(`/api/ofertas?${params}`, { signal: controller.signal });
    const data = await response.json();
    if (controller.signal.aborted) return;
    if (!response.ok || !Array.isArray(data.ofertas)) {
      showFeedback(data.erro || "Não foi possível buscar ofertas agora.", { canRetry: true });
      return;
    }

    offers = data.ofertas;
    if (!offers.length) {
      showFeedback("Nenhuma oferta encontrada. Tente buscar pelo nome, pela marca ou pelo tamanho da embalagem.");
      return;
    }

    const stores = [...new Set(offers.map((offer) => offer.loja))].sort(collator.compare);
    store.replaceChildren(new Option("Todas as lojas", ""), ...stores.map((name) => new Option(name, name)));
    storeControl.hidden = stores.length < 2;
    showFeedback("");
    renderOffers();
  } catch {
    if (!controller.signal.aborted) {
      showFeedback("Não foi possível buscar ofertas agora. Verifique sua conexão e tente novamente.", { canRetry: true });
    }
  } finally {
    if (pending === controller) pending = undefined;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (query.length < 2) {
    input.setCustomValidity("Digite pelo menos 2 caracteres.");
    input.reportValidity();
    return;
  }
  search(query);
});
input.addEventListener("input", () => input.setCustomValidity(""));
document.querySelectorAll("[data-query]").forEach((button) => {
  button.addEventListener("click", () => {
    input.setCustomValidity("");
    search(button.dataset.query);
  });
});
store.addEventListener("change", renderOffers);
retry.addEventListener("click", () => search(lastQuery));
