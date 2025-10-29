import json
import os
from pathlib import Path

# === CONFIGURATION ===
JSON_PATH = "data/catalogue.json"  # ou "data/catalogue_normalise.json"
OUTPUT_HTML = "check_covers.html"

# --- Charger le JSON ---
with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

# --- Générer le HTML ---
html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Vérification des affiches</title>
<style>
  body { font-family: Arial, sans-serif; background: #f8f8f8; margin: 2em; }
  h1 { text-align: center; color: #333; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }
  .card { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
  .card img { width: 100%; height: 260px; object-fit: cover; border-radius: 8px; }
  .missing { border: 2px dashed red; }
  p { font-size: 14px; color: #333; margin-top: 6px; }
</style>
</head>
<body>
<h1>🖼️ Vérification des affiches locales</h1>
<div class="grid">
"""

count_total, count_missing = 0, 0

for item in data:
    titre = item.get("titreProgramme", "Sans titre")
    cover = item.get("coverUrl", "")
    count_total += 1

    if cover and os.path.exists(cover):
        html += f'<div class="card"><img src="{cover}" alt="{titre}"><p>{titre}</p></div>\n'
    else:
        html += f'<div class="card missing"><p>🚫 {titre}</p></div>\n'
        count_missing += 1

html += f"""
</div>
<h2 style="text-align:center; margin-top:30px;">✅ {count_total - count_missing} affiches trouvées / ❌ {count_missing} manquantes</h2>
</body>
</html>
"""

# --- Écriture du fichier ---
Path(OUTPUT_HTML).write_text(html, encoding="utf-8")
print(f"✅ Page de vérification créée : {OUTPUT_HTML}")
print("👉 Ouvre-la dans ton navigateur pour vérifier les affiches.")
