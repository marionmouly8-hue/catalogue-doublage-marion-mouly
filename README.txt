Catalogue VF — Marion Mouly (site statique)

Contenu :
- index.html
- style.css
- script.js
- assets/placeholder.svg
- data/catalogue.json  (votre catalogue propre)

Comment lancer en local (Windows) :
1) Ouvrez un terminal dans ce dossier
2) Lancez un petit serveur local :
   - Avec Python :    python -m http.server 8000
3) Ouvrez ensuite :   http://localhost:8000

Fonctionnalités :
- Grille de jaquettes avec titre + date
- Clic = fiche détaillée (plateforme, catégorie, épisodes, date)
- Recherche par titre et filtre par plateforme
- Récupération automatique des affiches via TVMaze / iTunes / Wikipedia (avec cache localStorage)
- Si aucune image n'est trouvée, une vignette générique est affichée.

Remplacement des données :
- Remplacez data/catalogue.json par votre dernier fichier JSON nettoyé.
