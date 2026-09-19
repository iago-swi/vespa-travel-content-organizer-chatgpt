# 23.1 Prepare the sources

## Pixel 11: Google Photos first
Before any Insta360 or DJI export, create a roadtrip album containing photos and videos actually captured by Pixel 11. Download that album to the PC and extract the ZIP into a dedicated folder. Add this folder as a Pixel 11 source in Organizer. USB is the backup method when offline or when media have not synchronized.

## Check the dates
Check several photos AND videos: capture date, day and camera model when available. Windows file dates may reflect downloading. In the preview, open Détails du fichier… and check Date issue de. Do not accept an export date as the shooting date. For a consistent batch, assign its verified day to the source.

## Prepare the cameras
X5: reframe in Insta360 Studio, then add only the folder of exported frame photos and flat, reframed videos. Select Insta360 X5; no confirmation checkbox is required. Never supply 360 originals. Ace Pro 2: videos only; enable its device checkbox if carried. Drones: one folder per model; LosslessCut can prepare useful clips upstream.

## Photos and journals
Sorting RAW/JPEG pairs in your usual viewer, such as FastRawViewer, remains optional. Organizer copies supplied files; it does not choose the best images. Garmin accepts tracks. Geo-Log requires a common source day to preserve HTML, photos and relative links. Extract ZIPs; tracks are not split.

# 23.2 Roadtrip settings

## Open the dialog
Click Paramètres du voyage. Enter the name, start/end dates and country/region. The name becomes the trip folder; use a valid Windows name. Dates filter ingestion. Region is descriptive: it does not automatically change the timezone, which is selected separately under Réglages.

## Default devices
Checked: DJI Mini 4 Pro, DJI Neo 2, Insta360 X5, Pixel 11 Pro, Pixel 8 Pro, Garmin Instinct 3 Solar. Unchecked: DJI Air 3, Insta360 Ace Pro 2. Mini 4 Pro and Air 3 are not mutually exclusive. Pixel 8 is navigation/information only, with no device folder. Garmin supplies tracking.

## Default software
Geo-Log, Insta360 Studio and LosslessCut are on. Any selected drone forces LosslessCut on. X5 forces Insta360 Studio on. These checkboxes are read-only and turn off when the related devices are disabled. Editors are informational: no folders and no automatic launch.

## Default social networks
WhatsApp, Instagram and Facebook are on. Facebook mirror is on initially: when BOTH Instagram and Facebook are enabled, final files can share INSTAGRAM_FACEBOOK. Otherwise enabled channels have their own folders.

## Apply
Checkboxes alone create nothing. The dialog preview filters the last known inventory. After Appliquer, already configured sources are scanned again; this analysis provides the exact tree before copying.

# 23.3 Presets and defaults

## Save a preset
Set devices, software, networks and trip information in the dialog. Click Enregistrer le preset… and name it: Alps 2-4 days, Alps + Ace Pro 2, Italy 2027. Reusing a name replaces that saved preset. Loading fills the dialog; Appliquer commits the choices.

## What a preset contains
Name, dates, region, device/software/network checkboxes, Facebook mirror and use of 06_SELECTION. Source and destination paths remain in the main window and are not replaced by an equipment preset.

## Save as defaults
Enregistrer comme valeurs par défaut remembers settings for future launches without importing. Preferences and presets live in %APPDATA%/Vespa travel content organizer/preferences.json. The manually selected ExifTool path is also remembered automatically. Unsaved changes are lost when closing.

## Complete trip profile
The main Enregistrer and Charger un profil buttons use version 2 JSON files containing sources, destination, settings, day labels, timezone and ExifTool. Keep that profile with the project. Old version 1 profiles are rejected to avoid ambiguous Drone/Insta360 categories: recreate sources with exact models.

## Dates and variants
Always check dates after loading a preset. For the next two-day departure, start from Alps, enable Ace Pro 2 if carried, enable Mini 4 Pro and disable Air 3 if absent. Save a variant if you want to keep both configurations.

# 23.4 Analyze without copying

## Add sources
Choose a destination and add prepared folders with + Ajouter. Specify the model when names or metadata are ambiguous. Auto does not infer a model from DJI_0001.mp4. Sources cannot overlap or contain the destination trip folder.

## Run preview
Click 1. Analyser / aperçu. No trip folders are created and no media are copied. Analysis reads dates, identifies devices, applies settings and hashes classifiable files. Forbidden 360/proxy files are excluded before metadata reading.

## Read the results
The tree is integrated on the right of Paramètres du voyage, with scrolling and a Copier button. Fields, day names and checkboxes update the folder template immediately, without scanning or showing individual files. Only populated folders are created during copying. Fichiers: name, device, type, day and status, with search and filtering. Détails du fichier: full path, date source, destination and reason for a block. Synthèse: read, ready, copied, duplicate, review, excluded and volume by device/type. Journal: events and ExifTool issues.

## Correct before copying
Prêt = eligible. À vérifier = missing date or model. Exclu = disabled device or rejected type. Hors période = date outside the filter. Conflit = different content at the same destination or WhatsApp quota. Erreur = access, reading or other failure. Correct the issue and analyze again.

## No empty structure
PHOTO or VIDEO appears only with content. A media sidecar follows a same-stem associated file; an orphan camera sidecar is excluded. Source subfolders are preserved. Changing settings invalidates permission to copy an earlier preview.

# 23.5 Copy and resume

## Execute the import
After review, click 2. Copier. Only Prêt files are processed. Sources stay intact. Copying uses a temporary file, verifies SHA-256 when enabled, then commits without overwriting an existing file. Keep verification enabled.

## Duplicates and conflicts
Identical content already at the planned path becomes Doublon. This does not search the whole archive: a different name or folder may create another copy. An identical name with different content is blocked. Separate conflicting inputs under explicit subfolders or choose another destination, then analyze again.

## Progress and stopping
The progress bar follows reading and copying. Arrêter stops processing; completed copies remain and the partial file is cleaned up. Analyze again to resume. Do not remove storage before processing stops. A source changed since preview triggers an error and requires a new scan.

## CSV and log
After execution, a timestamped report is saved under 00_TRIP/NOTES. Exporter CSV also exports preview results. CSV fields include source, device, type, date, date origin, destination, size, status, detail and hash. Enregistrer le journal… saves events to a text file.

## Open and back up
Ouvrir le voyage opens the created trip folder. Double-clicking a row opens its destination folder, or the source if the destination does not yet exist. Open sample media after importing and make a second independent backup.

# 23.6 Selection and publishing

## Create 06_SELECTION only when useful
Keep Utiliser 06_SELECTION checked if you want a shortlist. Prepare a folder containing only chosen files, add it as a Sélection source and assign its day. After preview/copy, photos and videos are separated. Without supplied selections, this folder does not exist.

## WhatsApp: at most two files
Prepare a folder with the day’s final photo and/or video, preferably from Pixel 11. Add it as a WhatsApp source with an explicit day. WHATSAPP receives photo.ext and video.ext, with no subfolders, caption or sidecar. Extra candidates of the same type are conflicts; review the Prêt choice before copying. A photo alone or video alone is allowed.

## Replace a WhatsApp choice
Organizer does not overwrite copied media. To change a final choice, manually archive or remove the previous file from WHATSAPP, then scan the new source. The limit applies across extensions: a PNG cannot be added alongside an existing JPG photo.

## Instagram / Facebook
Add a folder of final files as an Instagram or Facebook source and assign its day. Photos, videos and TXT captions are accepted; CAROUSEL/REEL subfolders are preserved if present in the source. With both channels and mirror enabled, the destination is INSTAGRAM_FACEBOOK. Avoid importing the same batch under different names.

## Actual publishing
Organizer archives finalized files: it does not publish, link accounts or mark posts as published. Publish separately using the relevant applications.

# 23.7 ExifTool: path and status

## Automatic discovery
The app looks for exiftool.exe beside the application, in tools subfolders, in the parent location and in PATH. The field displays the detected or selected path. Auto clears a manual choice and repeats discovery.

## Choose manually
Click ExifTool… under Réglages and choose exiftool.exe. The path is saved in preferences and full profiles. If it becomes unavailable, it remains visible for correction; the app does not silently substitute another executable.

## Retest
Click Retester to read the version and check status. The version is also checked at each preview; the log identifies the tool used. ExifTool only reads metadata. If it fails, the internal reader takes over and records the issue in the log.

## Separate installation
ExifTool is not included in the Windows ZIP. Install the official Windows distribution. If named exiftool(-k).exe, rename it exiftool.exe; keep supporting files, including exiftool_files when supplied, beside it. Do not select a shortcut or ZIP.

## Without ExifTool
The internal reader uses accessible photo EXIF, QuickTime dates in some MP4/MOV files, GPX/KML/TCX dates and dated filenames. Support is narrower, particularly for HEIC, DNG or FIT. If no usable date exists, the file remains À vérifier; assign a verified source day.

# 23.8 Limits, troubleshooting and code

## Dates and timezones
Order: assigned day; ExifTool metadata then internal readers; dated filename; modification time only when enabled. Zoned dates convert to Europe/Zurich by default. Dates without zones are local; integer QuickTime timestamps are considered UTC. Per-source clock correction does not affect an explicitly assigned day.

## Exports and associated files
An MP4 may carry its export date. The X5 folder must contain only flat, reframed exports: the MP4 extension alone does not prove reframing. Extract ZIPs; KMZ and FIT may need ExifTool or an assigned day. Multi-day journals stay together under the chosen day, without splitting tracks or rewriting links.

## Executable and sources
Fully extract the Windows ZIP and launch Vespa travel content organizer.exe. Keep _internal beside it. Windows 10/11 64-bit; the distribution needs no Python installation. Source code includes app.py, engine.py, exiftool_support.py, vespa_ingest.py CLI, tests, licenses and Construire-Windows.cmd.

## CLI usage
With dependencies installed: python vespa_ingest.py --config profile.json --dry-run; use --execute to copy. --report report.csv exports results. Profiles use version 2. The engine is shared with the GUI. Installing dependencies and rebuilding needs Internet; regular operation is local.

## References and validation scope
Google Photos download help: https://support.google.com/photos/answer/7652919?hl=en ; ExifTool: https://exiftool.org/. These references support checking downloaded files. See VALIDATION.md for performed tests. Synthetic fixtures do not guarantee every physical device, codec or export format.
## Update 2.4.3
X5 exported frame photos go to PHOTO; reframed videos go to VIDEO. Only folders with content exist; 360 originals are rejected. Under Réglages, select Exclure les SRT/LRV de la copie to skip these sidecars without deleting source files. Checked by default; saved in the profile.


Version 2.4.4 : infobulles jaunes et plus compactes. Les exclusions RAW/DNG et SRT/LRV sont cochées par défaut. Un choix explicite enregistré dans un profil est conservé au chargement.


## Local diagnostic log
Aide > Exporter le diagnostic… saves a ZIP with version information and rotating diagnostic logs (four files of up to 2 MiB each). It records operation settings, paths and errors, without media contents or preference files. Share the ZIP when reporting a bug; nothing is sent automatically.
