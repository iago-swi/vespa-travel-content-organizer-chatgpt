# Ajouter un voyage en mode Auto — version 2.6.1

Dans **Sources à importer**, cliquez sur **Auto…**, puis choisissez le dossier
racine du voyage, par exemple `20260911 - Cols des Préalpes`.

L’application examine les noms des sous-dossiers directs et propose les sources :

| Sous-dossier | Source |
|---|---|
| X5 / Insta360 X5 / Insta X5 | Insta360 X5 |
| Ace Pro 2 / AcePro2 / Ace2 / Insta Ace Pro 2 | Insta360 Ace Pro 2 |
| Neo 2 / DJI Neo 2 | DJI Neo 2 |
| Mini 4 Pro / Mini4 / M4Pro / M4P (avec ou sans DJI) | DJI Mini 4 Pro |
| Air 3 / DJI Air 3 | DJI Air 3 |
| Pixel / Pixel11 / Pixel 11 Pro / P11 / P11Pro (avec ou sans Google) | Pixel 11 |
| Garmin / Instinct3 / Instinct3Solar / Garmin Instinct 3 Solar | Garmin |
| Geo-Log / GeoLog / Géo Log | Geo-Log |

Espaces, tirets, underscores, majuscules et préfixes numériques sont acceptés.
Les accents sont normalisés. Les mots descriptifs séparés comme photos, vidéos,
exports, clips, médias, fichiers, caméra, drone, GPS, GPX, traces ou journal sont
ignorés : `03_DJI_Mini4Pro_exports` et `Photos - Insta X5` sont reconnus.
Un nom contenant plusieurs appareils ou un autre modèle reste à identifier :
Air 3S n’est pas Air 3, Pixel 8 n’est pas Pixel 11. Le Pixel 8 et les logiciels
d’édition ne deviennent pas des sources de médias.
Le nom du dossier détermine la source : les métadonnées ne remplacent pas cette
affectation. Ainsi, un fichier DJI placé dans Pixel sera classé comme Pixel.

Vérifiez les affectations. Un dossier inconnu reste décoché : choisissez sa source
et cochez-le pour l’inclure. Les appareils désactivés restent exclus ; activez-les
dans Paramètres du voyage avant de relancer Auto. Sélection et les réseaux sociaux
ne sont pas des sources à détecter : utilisez les commandes du workflow.

Laissez la journée vide pour conserver les dates des médias. Pour Geo-Log,
indiquez une journée de classement : un journal multijour reste groupé sous cette
journée. Imposer une journée aux autres sources affecte tous leurs fichiers.

Cliquez sur **Ajouter les sources**, puis **Analyser / aperçu**. Auto ajoute une
entrée distincte par sous-dossier. Ses éventuels sous-dossiers internes sont lus
récursivement pendant l’analyse. Les fichiers directement à la racine ne sont pas
inclus ; leur nombre est affiché. Aucun fichier n’est copié pendant la détection.

Les doublons de sources et les dossiers qui se recouvrent sont bloqués. Pour
remplacer une configuration existante, retirez d’abord ses entrées de la liste ;
cela ne supprime aucun fichier.
