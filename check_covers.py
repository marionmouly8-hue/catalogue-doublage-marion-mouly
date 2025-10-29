import json, os

# Chemin vers ton fichier JSON
json_path = "data/catalogue.json"  # ou "data/catalogue_normalise.json"
covers_dir = "assets/covers"

# Lecture du fichier JSON
with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

missing = []

# Vérification de chaque affiche
for item in data:
    cover = item.get("coverUrl", "")
    if not cover:
        continue
    path = cover.replace("/", os.sep)
    full_path = os.path.join(os.getcwd(), path)
    if not os.path.exists(full_path):
        missing.append(cover)

# Résultats
print(f"\n🖼️ {len(missing)} affiches manquantes dans le dossier local :")
for m in missing:
    print("  ❌", m)
print("\n✅ Vérification terminée.")
