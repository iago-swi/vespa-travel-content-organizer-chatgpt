# Vespa travel content organizer — 2.7.0

Version 2.7.0 : l’arborescence des paramètres est une structure prévisionnelle
immédiate, sans analyse et sans fichiers individuels. Les cases cochées déterminent
les dossiers affichés ; PHOTO/VIDEO sont des possibilités. La copie continue à
créer uniquement les dossiers qui contiennent des fichiers.

Un journal de diagnostic local enregistre la version, les réglages utiles aux
opérations, les chemins des sources, les événements et les erreurs détaillées.
Il se trouve dans `%APPDATA%/Vespa travel content organizer/logs/diagnostic.log`.
Rotation : 2 Mio par fichier, avec trois archives (environ 8 Mio maximum).
En cas de bug, utilisez **Aide > Exporter le diagnostic…**, puis transmettez le ZIP.
Le ZIP contient seulement les journaux et les informations de version, pas les
médias ni le fichier de préférences. Aucun envoi automatique n’est effectué.

Version 2.6.1 : reconnaissance Auto élargie pour tous les appareils et journaux :
abréviations, marques facultatives, variantes de séparateurs, préfixes numériques
et mots descriptifs usuels (photos, vidéos, exports, traces…). Les modèles
différents et les noms ambigus restent à identifier manuellement.

Version 2.6.0 : bouton Auto… pour ajouter le dossier racine d’un voyage. Les noms
des sous-dossiers servent à reconnaître les sources, avec validation des
affectations avant ajout. Voir Guide-Auto-FR.md pour la procédure et les limites.

Version 2.5.1 : la liste des sources de l’aperçu contient uniquement les appareils
et journaux actifs. Sélection et les canaux de publication n’y figurent plus.

Extraire entièrement le ZIP Windows, puis lancer « Vespa travel content organizer.exe ».
Conserver le dossier _internal à côté. Windows x64 ; Python non nécessaire.

## Nouveautés de la version 2.5.0

L’arborescence est intégrée à droite des Paramètres du voyage et reste visible dans
toutes les rubriques. Sa largeur est réglable ; le texte défile dans les deux sens.
Le bouton Copier copie le texte affiché. Les cases, le nom, les dates, la région
et les noms des journées actualisent immédiatement la structure prévue, sans analyse ni fichiers individuels.
La rubrique Journées permet de modifier les libellés sans quitter les paramètres.
Appliquer réanalyse les sources ; Annuler abandonne les changements.
Les anciens onglets Arborescence ont été supprimés.

Les photos de frames X5 restent acceptées : PHOTO et VIDEO sont prévus dans la
structure et créés sur disque selon les fichiers présents. Les originaux 360 restent refusés. Les sources
désactivées sont ignorées à l’ingestion et dans les statistiques.

## Workflow

Garmin : trace GPS. Pixel 8 : OsmAnd et Geo-Log, navigation et journal, aucun dossier PIXEL8.
Pixel 11 : photos et vidéos ; téléchargement de l’album Google Photos avant les exports
Insta360/DJI, USB en plan B. Décompresser et vérifier les dates des médias.
X5 : photos de frames et vidéos plates déjà recadrées et exportées dans Studio. Ace Pro 2 : vidéo seulement.
Neo 2, Mini 4 Pro et Air 3 : sélection selon le voyage, PHOTO/VIDEO selon le contenu.
Mini 4 Pro et Air 3 peuvent être activés ensemble. X5 active Studio ; tout appareil vidéo active LosslessCut.
Publication : WhatsApp, Instagram et Facebook. WhatsApp contient au maximum une photo
et une vidéo finales par jour. Instagram/Facebook partagent leur dossier si le miroir est activé.
Organizer classe et copie les fichiers ; publier depuis les applications des réseaux.

## Utilisation

1. Vérifier les Paramètres du voyage et charger ou enregistrer un preset.
2. Ajouter les sources par appareil ; imposer une journée aux exports Geo-Log.
3. Analyser et contrôler l’arborescence, les dates et la synthèse par appareil/type.
4. Copier les fichiers prêts. Les sources restent intactes ; aucun dossier vide inutile.
5. Workflow > Gérer les fichiers… : ajouter sélections et médias finaux avec leur journée.
6. Vérifier la copie et sauvegarder sur un second support.

Les profils version 2 sont nettoyés à leur chargement : seules les catégories prises en
charge restent disponibles. Réenregistrer un profil actualise son fichier. Les presets
et valeurs par défaut sont filtrés à la lecture et à l’enregistrement des préférences.
Les archives de voyages existantes ne sont pas modifiées automatiquement.

ExifTool est facultatif, installé séparément. Réglages > ExifTool… permet de choisir
son emplacement ; Retester vérifie sa disponibilité. Vérifier les dates avant de copier.

## Documentation

Le dépôt contient les manuels français et anglais en Markdown, Guide-rapide-FR.md et Guide-Auto-FR.md.
Les PDF et captures historiques restent dans la distribution Windows d’origine.
L’interface est en français. 

L’exécutable portable n’est pas signé. Voir VALIDATION.md pour la portée des essais.

## À propos — version 2.4.1

Aide > À propos affiche le nom, la version, la date du build, les technologies et la mention « Vibe-codé avec ChatGPT ». Aide > Mode d’emploi conserve l’aide existante.

Maintenance : modifier VERSION dans app_info.py. Vespa.spec lance prepare_build.py, qui fixe BUILD_DATE au jour de construction et génère version_info.txt depuis ces mêmes informations. SOURCE_DATE_EPOCH permet de fixer une date reproductible (UTC). La date affichée reste celle du build, pas celle du lancement.

Version 2.4.2 : suppression du cadre pointillé de focus autour de l’animation Vespa.

Version 2.5.0 : X5 dans PHOTO et/ou VIDEO selon le contenu ; originaux 360 refusés. Dans Réglages, « Exclure les SRT/LRV de la copie » est placé sous RAW/DNG. Cette case, cochée par défaut comme RAW/DNG, est enregistrée dans le profil. Cochée, elle exclut SRT/LRV de l’aperçu et de la copie. Décochée, les annexes associées à un média admis peuvent être copiées. Aucun fichier source supprimé.


Version 2.4.4 : infobulles jaunes et plus compactes. Les exclusions RAW/DNG et SRT/LRV sont cochées par défaut. Un choix explicite enregistré dans un profil est conservé au chargement.

Version 2.4.5 : LosslessCut peut raccourcir toute vidéo (Ace Pro 2, Pixel 11, drone, export plat X5). Il est activé dès qu’un appareil vidéo est coché. Aucun lancement automatique ni dossier supplémentaire.

Version 2.5.0 : infobulles arrondies, marges réduites et police 12 px. Pixel 11 utilisé GPS désactivé : ses médias peuvent manquer de coordonnées. Vérifier chaque fichier, y compris DJI et X5. La trace Garmin peut servir dans un outil séparé, après contrôle des heures et fuseaux ; Organizer ne réalise pas ce géomarquage.
