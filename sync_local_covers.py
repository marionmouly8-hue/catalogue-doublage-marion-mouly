import os
import json
import unicodedata
import re
import shutil

# === CONFIGURATION ===
JSON_PATH = "data/catalogue.json"  # ou "data/catalogue_normalise.json"
COVERS_DIR = "assets/covers"

def normalize_text(text):
    """Supprime accents, apostrophes, ponctuation et met en minuscule."""
    if not text:
        return ""
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

# --- Charger les données ---
with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

# --- Lister les fichiers locaux ---
local_files = [f for f in os.listdir(COVERS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
normalized_local = {normalize_text(os.path.splitext(f)[0]): f for f in local_files}

linked, renamed, missing = [], [], []

for item in data:
    titre = item.get("titreProgramme", "").strip()
    if not titre:
        continue

    norm_title = normalize_text(titre)
    match = None

    # 1. Correspondance exacte
    if norm_title in normalized_local:
        match = normalized_local[norm_title]
    else:
        # 2. Correspondance partielle tolérante
        for key, filename in normalized_local.items():
            if norm_title in key or key in norm_title:
                match = filename
                break

    # 3. Si correspondance trouvée
    if match:
        # Vérifie si le nom du fichier correspond à la clé attendue
        expected_filename = f"{norm_title}.jpg"
        expected_path = os.path.join(COVERS_DIR, expected_filename)
        current_path = os.path.join(COVERS_DIR, match)

        # Renomme si différent
        if match != expected_filename:
            try:
                shutil.move(current_path, expected_path)
                renamed.append((match, expected_filename))
            except Exception as e:
                print(f"⚠️ Impossible de renommer {match} → {expected_filename}: {e}")

        item["coverUrl"] = f"assets/covers/{expected_filename}"
        linked.append((titre, expected_filename))
    else:
        missing.append((titre, norm_title))

# --- Sauvegarde du JSON ---
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# --- Rapport ---
print(f"\n✅ {len(linked)} jaquettes locales associées automatiquement.")
if renamed:
    print(f"🔄 {len(renamed)} fichiers renommés pour correspondre à leur titre :")
    for old, new in renamed:
        print(f"   • {old} → {new}")

if missing:
    print(f"⚠️ {len(missing)} programmes sans image correspondante :")
    for titre, norm in missing:
        print(f"  ❌ {titre}  ➜  (clé normalisée : {norm})")
else:
    print("🎉 Toutes les affiches locales ont été liées avec succès !")
