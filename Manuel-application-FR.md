# 23.1 Préparer les sources

## Pixel 11 : Google Photos en priorité
Avant tout export depuis Insta360 ou DJI, crée un album du roadtrip avec les photos et vidéos réellement prises avec le Pixel 11. Télécharge cet album sur le PC et décompresse le ZIP dans un dossier dédié. Dans Organizer, ajoute ce dossier comme source Pixel 11. USB reste le plan B sans Internet ou si les médias ne sont pas synchronisés.

## Coordonnées GPS
Vérifie les coordonnées de chaque fichier, quel que soit l’appareil. Le GPS du Pixel 11 est désactivé pour économiser la batterie : ses photos peuvent donc être sans position, comme les exports X5 ou certains fichiers DJI. Pour les fichiers sans coordonnées, utilise si nécessaire la trace Garmin de la journée dans un outil de géomarquage, après contrôle de l’heure de prise de vue et du fuseau. Conserve les coordonnées valides déjà présentes. Organizer classe et copie ; il n’applique pas lui-même la trace GPS aux médias.

## Contrôler les dates
Vérifie plusieurs photos ET vidéos : date de capture, journée et modèle quand disponible. La date du fichier Windows peut correspondre au téléchargement. Dans l’aperçu, consulte « Détails du fichier… » et « Date issue de ». Ne valide pas une date d’export à la place de la date du tournage. Pour un lot homogène, impose la vraie journée à la source.

## Préparer les caméras
X5 : effectue le recadrage dans Insta360 Studio, puis ajoute seulement le dossier de photos de frames et de vidéos plates exportées. Choisis Insta360 X5 : aucune case de confirmation à cocher. Ne fournis jamais les originaux 360. Ace Pro 2 : seulement les vidéos ; active sa case si emportée. Drones : ajoute un dossier par modèle ; LosslessCut peut raccourcir toute vidéo : Ace Pro 2, Pixel 11, drone ou export plat X5.

## Photos et journaux
Un tri préalable des paires RAW/JPEG dans ton outil habituel, par exemple FastRawViewer, reste facultatif. Dans Réglages, « Exclure les RAW/DNG de la copie » ignore les formats bruts (DNG, RAW, NEF, ARW, etc.) et conserve JPG, PNG et vidéos. Cochée par défaut, cette option est enregistrée dans le profil. Juste dessous, « Exclure les SRT/LRV de la copie » est aussi cochée : elle ignore ces annexes sans supprimer les sources. Décoche une case pour conserver ces fichiers ; les SRT/LRV doivent être associés à un média accepté. Les originaux restent intacts. Organizer ne choisit pas les meilleures images. Garmin accepte les traces. Dans la liste des sources, Geo-Log demande une journée commune à la source pour préserver HTML, photos et liens relatifs. Décompresse les ZIP ; les traces ne sont pas découpées.

# 23.2 Paramètres du voyage

## Ouvrir la fenêtre
Clique sur « Paramètres du voyage ». Renseigne nom, dates début/fin et pays/région. Le nom devient le dossier du voyage ; utilise un nom compatible Windows. Les dates filtrent l’ingestion. La région est descriptive : elle ne change pas automatiquement le fuseau, réglé séparément dans « Réglages ».

## Appareils par défaut
Cochés : DJI Mini 4 Pro, DJI Neo 2, Insta360 X5, Pixel 11 Pro, Pixel 8 Pro, Garmin Instinct 3 Solar. Décochés : DJI Air 3, Insta360 Ace Pro 2. Mini 4 Pro et Air 3 ne sont pas exclusifs. Pixel 8 est informatif/navigation : aucun dossier propre. Garmin alimente le tracking.

## Logiciels par défaut
Geo-Log, Insta360 Studio et LosslessCut cochés. Tout appareil vidéo coché active LosslessCut : Pixel 11, X5, Ace Pro 2 ou drone. X5 cochée force Insta360 Studio. Ces deux cases restent en lecture seule. Studio est décoché sans X5 ; LosslessCut est décoché si aucun appareil vidéo n’est actif. Les logiciels d’édition restent informatifs, sans dossier ni lancement automatique.

## Réseaux par défaut
WhatsApp, Instagram et Facebook cochés. « Dossier commun Instagram / Facebook », sous les réseaux sociaux, est activé par défaut : si Instagram ET Facebook sont cochés, les fichiers finaux peuvent partager INSTAGRAM_FACEBOOK. Sinon les canaux activés ont leur propre dossier.

## Appliquer
L’arborescence affiche immédiatement la structure prévue selon les cases cochées, même sans sources ni analyse. Aucun fichier individuel n’est affiché. PHOTO et VIDEO indiquent les types possibles ; les dossiers réels ne seront créés que si leur contenu existe. Une journée type représente la structure commune aux journées du voyage.

# 23.3 Presets et valeurs par défaut

## Enregistrer un preset
Dans les paramètres, règle le matériel, les logiciels, les réseaux et les informations du voyage. Clique sur « Enregistrer le preset… », puis nomme-le : Court roadtrip (quelques jours), Court roadtrip + Ace Pro 2, Long roadtrip (quelques semaines). Le même nom remplace ce preset enregistré. Charger le preset remplit la fenêtre ; « Appliquer » valide les choix.

## Ce que contient un preset
Nom, dates, région, cases Appareils/Logiciels/Réseaux, mode miroir Facebook et utilisation de 06_SELECTION. Les chemins des sources et de destination sont volontairement conservés dans la fenêtre principale et ne sont pas remplacés par un preset de matériel.

## Enregistrer comme valeurs par défaut
Ce bouton mémorise les réglages pour les prochains démarrages, sans lancer d’import. Les préférences et presets sont stockés dans %APPDATA%/Vespa travel content organizer/preferences.json. Le chemin ExifTool manuel est aussi mémorisé automatiquement. Un changement non enregistré est perdu à la fermeture.

## Profil complet du voyage
Les boutons principaux « Enregistrer » et « Charger un profil » utilisent un fichier JSON version 2 : sources, destination, réglages, journées nommées, fuseau et ExifTool. Garde ce profil avec ton projet. Les anciens profils version 1 sont refusés pour éviter une affectation ambiguë des catégories Drone/Insta360 : recrée leurs sources avec les modèles exacts.

## Dates et variantes
Dans « Nommer les journées… », « + Ajouter une journée » propose le lendemain de la dernière ligne. La première date vient du début du roadtrip, sinon de la date du jour. Les dates restent modifiables et sont conservées même sans nom. Vérifie toujours les dates d’un preset rechargé. Pour ton prochain départ de deux jours, pars du preset Court roadtrip, active Ace Pro 2 si présente, coche Mini 4 Pro et décoche Air 3 si absent. Enregistre une variante si tu veux conserver les deux configurations.

# 23.4 Analyser sans rien copier

## Ajouter les sources
Choisis une destination et ajoute les dossiers préparés avec « + Ajouter ». Appareils et journaux activés sont proposés, dont Geo-Log. Pixel 8 ne fournit aucun dossier. Sélection et publications : « Workflow > Gérer les fichiers… ». Une source ne peut pas contenir une autre source ni la destination du voyage.

## Lancer l’aperçu
Clique sur « 1. Analyser / aperçu ». Aucun dossier voyage n’est créé, aucun média n’est copié. L’analyse lit les dates, identifie les appareils, applique les cases et calcule les empreintes des fichiers classables. Les originaux 360 et les annexes filtrées sont exclus avant la lecture des métadonnées.

## Lire les résultats
Arborescence : panneau permanent à droite dans Paramètres du voyage, avec défilement horizontal et vertical et bouton Copier. Il réagit aux cases, au nom, aux dates, à la région et aux noms des journées. La structure dépend uniquement des cases cochées, sans analyse et sans noms de fichiers. Les dossiers réels restent créés selon le contenu. Aucun onglet Arborescence séparé. Fichiers : nom, appareil, type, journée et état ; recherche et filtre disponibles. Détails du fichier : chemin complet, origine de date, destination et raison d’un blocage. Synthèse : lus, prêts, copiés, doublons, à examiner, exclus et volume par appareil/type. Journal : événements et problèmes ExifTool.

## Corriger avant de copier
Prêt = admissible. À vérifier = date ou appareil à vérifier. Exclu = appareil désactivé ou type refusé. Hors période = date filtrée. Conflit = même destination avec contenu différent ou quota WhatsApp. Erreur = lecture, accès ou autre incident. Corrige puis relance l’analyse.

## Aucune structure fantôme
Sur le disque, PHOTO ou VIDEO est créé seulement avec son contenu. Une annexe de média suit le fichier associé de même nom ; une annexe orpheline de caméra est exclue. Les sous-dossiers source sont préservés. La modification des réglages invalide l’autorisation de copier l’ancien aperçu.

# 23.5 Copier et reprendre

## Exécuter l’import
Après contrôle, clique sur « 2. Copier ». Seuls les fichiers Prêt sont traités. Les sources restent intactes. La copie est écrite dans un fichier temporaire, vérifiée par SHA-256 si l’option est cochée, puis validée sans écraser un fichier existant. Laisse cette vérification activée.

## Doublons et conflits
Un contenu identique déjà présent au chemin prévu devient Doublon. Le contrôle ne recherche pas les mêmes fichiers dans toute l’archive : un autre nom ou un autre dossier peut créer une seconde copie. Un nom identique avec contenu différent est bloqué. Sépare les sources conflictuelles dans des sous-dossiers explicites ou choisis une autre destination, puis réanalyse.

## Progression et arrêt
La barre suit lecture et copie. « Arrêter » interrompt le travail ; les copies déjà terminées restent disponibles et le fichier partiel est nettoyé. Relance une analyse pour reprendre. Ne retire pas un support avant l’arrêt effectif. Une source modifiée depuis l’aperçu provoque une erreur et exige une nouvelle analyse.

## CSV et journal
Après une exécution, un rapport daté est enregistré dans 00_TRIP/NOTES. « Exporter CSV » permet aussi de sauvegarder les résultats d’un aperçu. Le CSV détaille source, appareil, type, date, origine de date, destination, taille, état, détail et empreinte. « Enregistrer le journal… » sauvegarde les événements dans un fichier texte.

## Ouvrir et sauvegarder
« Ouvrir le voyage » ouvre le dossier créé. Un double-clic sur une ligne ouvre son dossier de destination, ou la source si la destination n’existe pas encore. Après import, ouvre quelques médias et fais une seconde sauvegarde indépendante.

# 23.6 Sélection et publication

## Créer 06_SELECTION uniquement si utile
Dans Paramètres du voyage > Sélection, coche « Conserver une copie des médias sélectionnés » si tu veux archiver tes choix. Tu choisis les fichiers toi-même ; cette copie supplémentaire est facultative. Prépare un dossier contenant uniquement tes choix, ajoute-le via « Workflow > Gérer les fichiers… > Sélection » et impose la journée. Après aperçu/copie, les photos et vidéos sont séparées. Si tu ne fournis aucune sélection, ce dossier n’existe pas.

## WhatsApp : deux fichiers au maximum
Prépare un dossier avec la photo finale et/ou la vidéo finale du jour, idéalement issues du Pixel 11. Ajoute-le via « Workflow > Gérer les fichiers… > WhatsApp » avec la journée imposée. La destination WHATSAPP reçoit photo.ext et video.ext, sans sous-dossier ni légende ni annexe. Plusieurs candidats du même type sont signalés comme conflits ; vérifie le fichier Prêt avant de copier. Une seule photo ou une seule vidéo reste possible.

## Remplacer un choix WhatsApp
Organizer n’écrase pas les médias déjà copiés. Pour modifier une publication finale, archive ou retire manuellement l’ancien fichier du dossier WHATSAPP, puis réanalyse la nouvelle source. La limite s’applique aussi entre extensions : une photo PNG ne s’ajoute pas à une photo JPG existante.

## Instagram / Facebook
Dans « Workflow > Gérer les fichiers… », ajoute les fichiers finaux pour Instagram ou Facebook avec leur journée. Photos, vidéos et légendes TXT sont admises ; les sous-dossiers CAROUSEL/REEL sont conservés si présents dans ta source. Avec les deux canaux et le miroir actifs, la destination est INSTAGRAM_FACEBOOK. N’importe pas deux fois le même lot sous des noms différents.

## Publication réelle
Organizer archive les fichiers finalisés : il ne publie rien, ne relie aucun compte et ne coche aucun statut publié. Publie ensuite dans les applications concernées.

# 23.7 ExifTool : chemin et statut

## Recherche automatique
L’application cherche exiftool.exe près de l’application, dans un sous-dossier tools, au niveau parent et dans le PATH. Le champ affiche le chemin détecté ou choisi. Le bouton Auto abandonne le chemin manuel et relance cette recherche.

## Choisir manuellement
Clique sur « ExifTool… » dans Réglages et sélectionne exiftool.exe. Le chemin est enregistré dans les préférences et les profils complets. S’il devient inaccessible, il reste visible afin de pouvoir le corriger ; l’application ne lui substitue pas silencieusement un autre exécutable.

## Retester
Clique sur « Retester » pour lire la version et vérifier le statut. La version est aussi vérifiée à chaque aperçu ; le journal indique l’outil utilisé. ExifTool est lancé uniquement pour lire les métadonnées. En cas d’erreur, la lecture interne prend le relais avec un message dans le journal.

## Installation séparée
ExifTool n’est pas inclus dans le ZIP Windows. Installe la distribution Windows officielle. Si le fichier porte le nom exiftool(-k).exe, renomme-le exiftool.exe ; conserve les fichiers de support, notamment exiftool_files lorsque fourni, à côté. Ne sélectionne pas un raccourci ou un ZIP.

## Sans ExifTool
La lecture interne exploite les EXIF photo accessibles, la date QuickTime de certains MP4/MOV, les dates GPX/KML/TCX et les noms datés. La prise en charge est plus limitée, notamment pour HEIC, DNG ou FIT. Si aucune date n’est exploitable, le fichier reste À vérifier ; impose alors une journée confirmée.

# 23.8 Limites, dépannage et code

## Dates et fuseaux
Ordre : journée imposée ; métadonnées ExifTool puis lecteur interne ; nom daté ; date de modification seulement si activée. Les dates avec fuseau sont converties vers Europe/Zurich par défaut. Les dates sans fuseau sont considérées locales ; les temps entiers QuickTime sont considérés UTC. La correction d’horloge par source ne s’applique pas à une journée imposée.

## Exports et fichiers associés
Un MP4 peut porter une date d’export. Le dossier X5 doit contenir des exports plats déjà recentrés. Aucune confirmation n’est demandée ; l’extension MP4 seule ne prouve pas le recadrage. Les ZIP sont à extraire ; les KMZ et FIT peuvent nécessiter ExifTool ou une date imposée. Les journaux multijours sont conservés ensemble sous la journée choisie, sans découpage ni réécriture des liens.

## Interface et version
Aide > À propos affiche la version et le build. Aide > Exporter le diagnostic… crée un ZIP à transmettre en cas de bug : version, étapes de traitement, chemins des sources et erreurs détaillées, sans médias. Le journal local est limité à quatre fichiers de 2 Mio, avec rotation automatique. Aucun envoi automatique.

## Exécutable et sources
L’icône Vespa est intégrée au programme. Clic ou Espace sur la petite Vespa du bandeau : pause/reprise de l’animation, mémorisée. Survole les commandes pour leur infobulle. Extrais intégralement le ZIP Windows et lance « Vespa travel content organizer.exe ». Garde le dossier _internal à côté. Windows 10/11 64 bits ; Python n’est pas nécessaire pour cette distribution. Le code source inclut app.py, engine.py, exiftool_support.py, la CLI vespa_ingest.py, les tests, les licences et Construire-Windows.cmd.

## Utilisation de la CLI
Avec les dépendances installées : python vespa_ingest.py --config profil.json --dry-run ; puis --execute pour copier. --report rapport.csv exporte le rapport. Les profils sont en version 2. Le moteur est partagé avec l’interface. Installer les dépendances et reconstruire nécessite Internet ; l’usage courant est local.

## Références et portée de la validation
Aide téléchargement Google Photos : https://support.google.com/photos/answer/7652919?hl=fr ; ExifTool : https://exiftool.org/. Ces liens complètent le contrôle des fichiers téléchargés. Voir VALIDATION.md pour les tests effectués. Les supports réels, tous les codecs et tous les exports de chaque appareil ne peuvent être garantis par les seuls essais synthétiques.