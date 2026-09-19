# Guide rapide — 2.7.0

1. Ouvrir **Paramètres du voyage** : nom, dates, région, appareils et destinations. Charger un preset si utile. L’arborescence à droite se met à jour immédiatement, sans analyse et sans noms de fichiers. Copier permet de récupérer sa structure texte.
2. Préparer les fichiers : télécharger puis décompresser l’album Google Photos du Pixel 11 ; USB est l’alternative. Pour X5, exporter depuis Insta360 Studio les photos extraites de frames et les vidéos plates déjà recadrées. Les originaux `.insv`, `.insp` et `.360` sont refusés. Ace Pro 2 reçoit uniquement des vidéos.
3. Choisir un dossier de destination, puis ajouter chaque source ou utiliser **Auto…** et vérifier les appareils proposés. Pixel 8 Pro sert à la navigation et ne crée aucun dossier. Les logiciels Studio et LosslessCut n’ont pas de dossier propre.
4. Configurer ExifTool si disponible : **Réglages → ExifTool…**, sélectionner son exécutable et Retester. Sans ExifTool, la lecture interne reste disponible, avec une couverture plus limitée.
5. **Analyser / aperçu** : contrôler dates, fuseau, appareils, fichiers exclus et conflits. Imposer une journée aux journaux ou médias sans date fiable. L’application ne géomarque pas les fichiers à partir de la trace Garmin et ne recadre pas les vidéos.
6. **Copier** : seuls les fichiers prêts sont copiés, sans effacer les sources. Les dossiers PHOTO et VIDEO sont séparés selon le contenu réel ; les dossiers vides ne sont pas créés. Vérifier quelques fichiers et conserver une seconde sauvegarde.
7. Après tri, ajouter les médias retenus via **Workflow → Gérer les fichiers…**. Sélection est facultatif. WhatsApp a son dossier final ; Instagram et Facebook peuvent partager leur dossier lorsque le miroir est activé. La publication se fait dans les applications des réseaux.
8. En cas de problème : **Aide → À propos** indique la version ; **Aide → Exporter le diagnostic…** enregistre les journaux locaux et les informations de version dans un ZIP. Aucun média n’y est ajouté ; les journaux peuvent contenir des chemins locaux.

Ce qui est décoché n’est pas ingéré et n’apparaît ni dans la structure prévue ni dans les statistiques. L’aperçu est un modèle de dossiers possibles ; seules les copies effectives créent des dossiers sur disque.

Ace Pro 2 exclut également les annexes : seuls ses fichiers vidéo sont ingérés. Pour X5 et les autres appareils, les annexes associées suivent le média admis selon les options RAW/DNG et SRT/LRV.
