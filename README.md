# Vespa travel content organizer

Application Windows en français pour préparer, analyser et copier les médias d’un voyage à Vespa, avec classement par journée, appareil et type de contenu. Les fichiers sources sont conservés ; les copies existantes ne sont jamais écrasées.

## Version publiée : 2.7.0

Import fondé sur les sources complètes de la version 2.7.0 du 14 septembre 2026, retrouvées avec ses livrables Windows. L’exécutable fourni dans ChatGPT.zip est identique à celui conservé avec ces sources. Règle X5 confirmée : **photos extraites de frames et vidéos plates déjà recadrées**, exportées depuis Insta360 Studio. Les originaux 360 sont exclus.

Fonctions conservées :

- Arborescence immédiate dans **Paramètres du voyage**, sans analyse préalable ni fichiers individuels ; défilement, largeur réglable et bouton Copier.
- Appareils, logiciels, réseaux, dates et journées configurables ; presets et profils de voyage.
- PHOTO/VIDEO séparés selon le contenu pour Pixel 11, X5 et drones ; seuls les dossiers avec contenu sont créés sur disque. Ace Pro 2 : VIDEO uniquement.
- Google Photos comme méthode principale pour les médias Pixel 11 ; téléchargement et décompression avant ingestion, USB en alternative.
- Pixel 8 Pro réservé à la navigation ; aucun dossier propre. Insta360 Studio et LosslessCut ne créent aucun dossier.
- ExifTool facultatif et sélectionnable ; lecteur interne disponible.
- WhatsApp possède sa destination finale ; Instagram/Facebook peuvent partager un dossier.
- Boîte À propos, reconnaissance Auto des dossiers, journal de diagnostic local avec rotation et export ZIP.

## Démarrer depuis les sources

Windows 10/11 64 bits, Python 3.12 ou plus récent. Ouvrir un terminal à la racine du dépôt :

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Ou utiliser `Lancer.cmd`, qui prépare l’environnement au premier démarrage. ExifTool s’installe séparément et se configure dans **Réglages → ExifTool…**. L’application ne se connecte pas directement à Google Photos et ne recadre pas les vidéos.

## Construire l’application Windows

Lancer `Construire-Windows.cmd`. Le script installe les dépendances épinglées et PyInstaller, puis produit `dist/Vespa travel content organizer/`. Distribuer ce dossier entier, avec `_internal`, les guides et les licences. Les exécutables, caches et builds temporaires sont exclus de Git.

`app_info.py` définit la version. `prepare_build.py` génère la ressource Windows et la date de construction ; `SOURCE_DATE_EPOCH` permet de fixer une date reproductible. `resources_rc.py` est une ressource Qt intégrée conservée avec ses fichiers sources `resources.qrc` et `assets/`.

## Vérifier

```powershell
.venv\Scripts\python.exe -m unittest discover -s . -p "test_*.py"
New-Item -ItemType Directory -Force work
$env:QT_QPA_PLATFORM = "offscreen"
$env:VESPA_SETTINGS_DIR = "$PWD/work/test-settings"
.venv\Scripts\python.exe app.py --self-test work/self-test.json
```

Voir [VALIDATION.md](VALIDATION.md) pour les résultats et limites de la vérification. Les essais utilisent des données synthétiques, sans médias de voyage.

## Documentation et contenu

- [Guide rapide](Guide-rapide-FR.md)
- [Manuel français](Manuel-application-FR.md) et [manuel anglais](Manuel-application-EN.md)
- [Ajout automatique des sources](Guide-Auto-FR.md)
- [Notes de version et utilisation](LISEZ-MOI.md)
- [Licences des dépendances](LICENCES-TIERS.md), avec les textes dans `Licences/`
- `Profils-exemples/` : profils sans chemins personnels ni sources.

Les guides Markdown de ce dépôt font référence. Les fichiers de construction permettent de produire la distribution Windows ; les exécutables ne sont pas stockés dans Git.

Les profils réels, préférences, journaux, médias et archives de voyage restent hors du dépôt. Un diagnostic exporté peut contenir des chemins locaux ; le relire avant de le partager.
