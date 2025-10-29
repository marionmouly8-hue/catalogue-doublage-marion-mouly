import os
import json
import unicodedata
import difflib

DATA_PATH = "data/catalogue.json"
COVERS_DIR = "assets/covers"

def normalize_text(text):
    """Supprime les accents, espaces et ponctuation pour comparaison."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    for ch in [":", "!", "?", ",", ".", "'", "’", "-", "(", ")", "«", "»"]:
        text = text.replace(ch, "")
    text = text.replace(" ", "_")
    return text.strip()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Récupère tous les fichiers d’affiches
cover_files = [f for f in os.listdir(COVERS_DIR) if f.lower().endswith((".jpg", ".png"))]
normalized_files = {normalize_text(os.path.splitext(f)[0]): f for f in cover_files}

updated = 0
missing = []

for entry in data:
    titre = entry.get("titreProgramme", "").strip()
    if not titre:
        continue

    normalized_title = normalize_text(titre)
    if entry.get("coverUrl") and os.path.exists(entry["coverUrl"]):
        continue

    # Correspondance exacte
    if normalized_title in normalized_files:
        filename = normalized_files[normalized_title]
        entry["coverUrl"] = f"{COVERS_DIR}/{filename}"
        updated += 1
    else:
        # Recherche de correspondances proches
        close = difflib.get_close_matches(normalized_title, normalized_files.keys(), n=1, cutoff=0.6)
        if close:
            print(f"🔸 Correspondance probable : '{titre}' ↔ '{normalized_files[close[0]]}'")
            filename = normalized_files[close[0]]
            entry["coverUrl"] = f"{COVERS_DIR}/{filename}"
            updated += 1
        else:
            missing.append(titre)

# Sauvegarde le JSON
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ {updated} jaquettes liées automatiquement.")
if missing:
    print("\n❌ Aucune image trouvée pour :")
    for m in missing:
        print("   -", m)
