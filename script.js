/* global localStorage, fetch */
const GRID = document.getElementById('grid');
const CARD_TPL = document.getElementById('card-tpl');
const SELECT_PLATFORM = document.getElementById('platform');
const SEARCH = document.getElementById('search');
const MODAL = document.getElementById('modal');
const UPDATED = document.getElementById('updated');

const PLACEHOLDER = 'assets/placeholder.svg';

function byTitleAsc(a,b){
  return a.titreProgramme.localeCompare(b.titreProgramme, 'fr', {sensitivity:'base'});
}
function uniq(arr){ return Array.from(new Set(arr)); }

// Load data
(async function init(){
  const res = await fetch('data/catalogue.json');
  const data = await res.json();

  // Fill platform filter
  const plats = uniq(data.map(x => x.plateforme).filter(Boolean)).sort();
  for (const p of plats){
    const opt = document.createElement('option');
    opt.value = p;
    opt.textContent = p;
    SELECT_PLATFORM.appendChild(opt);
  }

  // Updated date (today)
  UPDATED.textContent = new Date().toLocaleDateString('fr-FR', {day:'2-digit', month:'long', year:'numeric'});

  // Render
  let state = { platform:'', q:'' };
  function apply(){
    let items = data.slice();
    if (state.platform) items = items.filter(x => x.plateforme === state.platform);
    if (state.q){
      const q = state.q.toLowerCase();
      items = items.filter(x => x.titreProgramme.toLowerCase().includes(q));
    }
    items.sort(byTitleAsc);
    render(items);
  }
  SELECT_PLATFORM.addEventListener('change', e => { state.platform = e.target.value; apply(); });
  SEARCH.addEventListener('input', e => { state.q = e.target.value.trim(); apply(); });

  apply();
})();

function render(items){
  GRID.innerHTML = '';
  items.forEach(item => {
    const node = CARD_TPL.content.firstElementChild.cloneNode(true);
    const img = node.querySelector('.cover');
    const title = node.querySelector('.title');
    const date = node.querySelector('.date');

    title.textContent = item.titreProgramme;
    date.textContent = item.dateDiffusion || '';

    setCover(img, item);

    node.addEventListener('click', () => openModal(item, img.src, title.textContent));
    GRID.appendChild(node);
  });
}

function openModal(item, coverSrc, alt){
  const cover = MODAL.querySelector('.modal-cover');
  cover.src = coverSrc || PLACEHOLDER;
  cover.alt = `Affiche — ${alt}`;
  MODAL.querySelector('.modal-title').textContent = item.titreProgramme;
  MODAL.querySelector('.modal-plat').textContent = item.plateforme || '—';
  MODAL.querySelector('.modal-cat').textContent = item.categorie || '—';
  MODAL.querySelector('.modal-eps').textContent = (item.episodesTraduits && item.episodesTraduits.length) ? item.episodesTraduits.join(', ') : '—';
  MODAL.querySelector('.modal-date').textContent = item.dateDiffusion || '—';
  if (typeof MODAL.showModal === 'function') MODAL.showModal(); else MODAL.setAttribute('open','');
}
MODAL.querySelector('.close').addEventListener('click', () => MODAL.close());

// --- Cover resolver with caching (TVMaze -> iTunes -> Wikipedia) ---
async function setCover(imgEl, item){
  const key = 'cover:' + item.titreProgramme.toLowerCase();
  const cached = localStorage.getItem(key);
  if (cached){
    imgEl.src = cached;
    imgEl.alt = `Affiche — ${item.titreProgramme}`;
    return;
  }
  const src = await resolveCover(item.titreProgramme);
  imgEl.src = src || PLACEHOLDER;
  imgEl.alt = `Affiche — ${item.titreProgramme}`;
  if (src) localStorage.setItem(key, src);
}

async function resolveCover(title){
  // Try TVMaze (no key)
  try{
    const r = await fetch('https://api.tvmaze.com/singlesearch/shows?q=' + encodeURIComponent(title));
    if (r.ok){
      const j = await r.json();
      if (j && j.image && (j.image.original || j.image.medium)){
        return j.image.original || j.image.medium;
      }
    }
  }catch{}

  // Try iTunes Search API
  try{
    const r = await fetch('https://itunes.apple.com/search?term=' + encodeURIComponent(title) + '&media=tvShow');
    if (r.ok){
      const j = await r.json();
      if (j && j.results && j.results[0] && j.results[0].artworkUrl100){
        return j.results[0].artworkUrl100.replace('100x100bb', '600x600bb');
      }
    }
  }catch{}

  // Try Wikipedia (French first, then English)
  const wikiTry = async (lang) => {
    try{
      const r = await fetch(`https://${lang}.wikipedia.org/api/rest_v1/page/summary/` + encodeURIComponent(title));
      if (r.ok){
        const j = await r.json();
        if (j && j.thumbnail && j.thumbnail.source) return j.thumbnail.source;
      }
    }catch{}
    return null;
  };
  let w = await wikiTry('fr');
  if (w) return w;
  w = await wikiTry('en');
  if (w) return w;

  // Fallback
  return null;
}
