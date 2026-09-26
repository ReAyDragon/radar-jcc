# Radar JCC

Application web installable qui suit les prochaines sorties du jeu de cartes Pokémon en français : dates, prix conseillés, statut (officiel, annoncé, reporté) et liens d'achat.

- `index.html` : l'application.
- `data.json` : le calendrier, mis à jour chaque matin par une tâche planifiée Claude.
- `sw.js` et `manifest.webmanifest` : installation sur l'écran d'accueil et fonctionnement hors connexion.
- `tools/export.py` : génère `data.json` à partir de la base du radar.
- `tools/icons.py` : dessine les icônes.

## Installer l'application

- **Android (Chrome)** : ouvre le site, puis touche « Installer l'appli » ou le menu ⋮ → « Installer l'application ».
- **iPhone (Safari)** : ouvre le site, touche Partager, puis « Sur l'écran d'accueil ».

Application de suivi non officielle. Pokémon et ses marques appartiennent à leurs propriétaires.
