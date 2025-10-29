import os
import json
import requests
from urllib.parse import quote

# =============================
# 🔧 CONFIGURATION
# =============================

TMDB_API_KEY = "72526fcb516105a6055782442bcb3691"
DATA_PATH = "data/catalogue.json"
COVERS_DIR = "assets/covers"

# =============================
# 🧠 FONCTIONS
# =============================

def search_tmdb(title):
    """Recherche une affiche officielle sur TMDB (film ou série)."""
    base_url = "https://api.themoviedb.org/3/search/multi"
    params = {"api_key": TMDB_API_KEY, "query": title, "language": "fr-FR"}
    r = requests.get(base_url, params=params)
    if r.status_code != 200:
        print(f"⚠️ Erreur TMDB ({r.status_code}) pour {title}")
        return None
    data = r.json()
    if not data.get("results"):
        print(f"❌ Aucune affiche trouvée pour {title}")
        return None
    poster_path = data["results"][0].get("poster_path")
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    print(f"❌ Pas d’affiche disponible pour {title}")
    return None


def download_image(url, dest_path):
    """Télécharge une image si elle n’existe pas déjà."""
    if os.path.exists(dest_path):
        print(f"✅ Déjà présent : {os.path.basename(dest_path)}")
        return False
    r = requests.get(url)
    if r.status_code == 200:
        with open(dest_path, "wb") as f:
            f.write(r.content)
        print(f"✅ Téléchargé : {os.path.basename(dest_path)}")
        return True
    print(f"⚠️ Erreur lors du téléchargement de {url}")
    return False


# =============================
# 🚀 LOGIQUE PRINCIPALE
# =============================

if not os.path.exists(DATA_PATH):
    print(f"❌ Fichier introuvable : {DATA_PATH}")
    exit()

os.makedirs(COVERS_DIR, exist_ok=True)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    title = entry.get("titreProgramme", "").strip()
    cover_path = entry.get("coverUrl", f"assets/covers/{title.replace(' ', '_')}.jpg")

    # Si le fichier existe déjà → on saute
    if os.path.exists(cover_path):
        continue

    poster_url = search_tmdb(title)
    if poster_url:
        filename = os.path.basename(cover_path)
        filepath = os.path.join(COVERS_DIR, filename)
        if download_image(poster_url, filepath):
            entry["coverUrl"] = f"assets/covers/{filename}"

# Sauvegarde finale du JSON
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n🎉 Recherche des affiches manquantes terminée !")
