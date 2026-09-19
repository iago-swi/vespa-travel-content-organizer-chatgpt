# Validation — 2.7.0

67 tests passent. Structure visible sans sources et sans lecture du disque, cases et journées réactives, aucun nom de fichier affiché. Interface rendue et contrôlée. La logique de copie reste indépendante : aucun dossier vide créé.

Diagnostic : rotation bornée, traces d’exception et export ZIP testés. Commande Aide > Exporter le diagnostic… exercée avec succès. Aucun média ou fichier de préférences dans le ZIP.

Auto et ses règles de reconnaissance sont conservés. Le dépôt contient les guides en Markdown ; les PDF historiques restent dans la distribution Windows d’origine.

## Vérification pour l’import GitHub — 19 septembre 2026

L’exécutable fourni dans ChatGPT.zip est identique octet pour octet à celui conservé avec les sources 2.7.0 du 14 septembre (SHA-256 : `297e4c4218c8f8254be992cb3beb6ab827cd27b747cb2870a6243cb654e8b9c7`). La version applicative reste 2.7.0. Les photos extraites de frames X5 sont acceptées dans PHOTO et les vidéos déjà recadrées dans VIDEO ; les originaux 360 sont refusés.

Préparation du dépôt : README, guide rapide Markdown et .gitignore ajoutés. La référence Pillow dans requirements.txt est corrigée de 12.3.4.0 vers 12.3.0, version effectivement installée pour les tests et présente dans les licences livrées. Le contrôle de la boîte À propos tient compte de la commande Exporter le diagnostic ajoutée en 2.7.0. Aucun changement du moteur ni du comportement applicatif.

Les tests utilisent des fichiers synthétiques ; tous les appareils physiques et codecs ne sont pas couverts. L’application ne peut pas prouver qu’un MP4 a déjà été recadré. ExifTool reste externe et facultatif. Les médias de voyage, chemins personnels, préférences, journaux, caches et builds ne sont pas inclus dans le dépôt.
