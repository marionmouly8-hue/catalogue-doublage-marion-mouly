import os
import json
import requests
import re

# --- CONFIGURATION ---
TMDB_API_KEY = "72526fcb516105a6055782442bcb3691"
DATA_PATH = "data/catalogue.json"
COVERS_DIR = "assets/covers"

os.makedirs(COVERS_DIR, exist_ok=True)

# --- Nettoyage du nom de fichier ---
def safe_filename(name):
    """Supprime les caractères interdits dans les noms de fichiers (Windows)."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# --- CHARGEMENT DU JSON ---
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def search_tmdb_poster(title):
    """Recherche une affiche sur TMDB."""
    query = title.strip()
    if not query:
        return None

    url = f"https://api.themoviedb.org/3/search/multi"
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "fr-FR"}
    r = requests.get(url, params=params)

    if r.status_code != 200:
        print(f"⚠️ Erreur TMDB pour {title}: {r.status_code}")
        return None

    results = r.json().get("results")
    if not results:
        return None

    poster_path = results[0].get("poster_path")
    if not poster_path:
        return None

    return f"https://image.tmdb.org/t/p/w500{poster_path}"

def download_image(url, dest_path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return True
    return False

# --- TRAITEMENT ---
updated = 0
for item in data:
    titre = item.get("titreProgramme", "")
    if not titre or ("coverUrl" in item and item["coverUrl"]):
        continue

    poster_url = search_tmdb_poster(titre)
    if poster_url:
        # Nettoyage du nom de fichier
        filename = safe_filename(f"{titre}.jpg")
        filepath = os.path.join(COVERS_DIR, filename)
        if download_image(poster_url, filepath):
            item["coverUrl"] = f"assets/covers/{filename}"
            updated += 1
            print(f"✅ {titre} -> {filename}")
    else:
        print(f"❌ Aucune affiche trouvée pour {titre}")

# --- SAUVEGARDE ---
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n🎬 {updated} affiches ajoutées et catalogue mis à jour !")
