"""Folder-name discovery, without reading media or changing source files."""
import re
import unicodedata
from pathlib import Path
from engine import Source, enabled, is_within

ALIASES={
    'Insta360 X5':('x5','insta360x5','instax5'),
    'Insta360 Ace Pro 2':('acepro2','ace2','insta360acepro2','instaacepro2','insta360ace2','instaace2'),
    'DJI Mini 4 Pro':('mini4pro','mini4','m4pro','m4p','djimini4pro','djimini4','djim4pro','djim4p'),
    'DJI Neo 2':('neo2','djineo2'),
    'DJI Air 3':('air3','djiair3'),
    'Pixel 11':('pixel','pixel11','pixel11pro','p11','p11pro','googlepixel','googlepixel11','googlepixel11pro','googlep11','googlep11pro'),
    'Garmin':('garmin','instinct3','instinct3solar','garmininstinct3','garmininstinct3solar'),
    'Geo-Log':('geolog','geologjournal','journalgeolog'),
}
# Only standalone descriptive words are ignored; model numbers and unknown words
# remain significant. Never use substring/fuzzy matching (Air 3 != Air 3S).
DESCRIPTORS=set('photo photos video videos image images media medias export exports exported recadre recadres recadree recadrees reframed clip clips footage source sources fichier fichiers file files dossier folder camera appareil drone smartphone telephone gps gpx kml fit trace traces track tracks tracking journal journaux log logs'.split())

def identify_folder(name):
    plain=unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()
    words=re.sub(r'[^a-z0-9]+',' ',plain).strip().split()
    # A leading number may be a list index or date, including an attached prefix.
    if words:words[0]=re.sub(r'^\d+(?=[a-z])','',words[0])
    while words and words[0].isdigit():words.pop(0)
    words=re.sub(r'\bgeo\s+log\b','geolog',' '.join(words)).split()
    compact=''.join(word for word in words if word not in DESCRIPTORS)
    matches=[device for device,names in ALIASES.items() if compact in names]
    return matches[0] if len(matches)==1 else ''

def discover(root):
    root=Path(root)
    if not root.is_dir():raise ValueError('Choisissez un dossier existant.')
    entries=sorted(root.iterdir(),key=lambda p:p.name.casefold())
    folders=[p for p in entries if p.is_dir() and not p.is_symlink() and not p.is_junction()]
    return [(str(p),identify_folder(p.name)) for p in folders],sum(p.is_file() for p in entries)

def validate_choices(choices,config,existing):
    from datetime import datetime
    if not choices:raise ValueError('Choisissez au moins un dossier.')
    for s in choices:
        if not s.device:raise ValueError('Identifiez chaque dossier choisi ou décochez-le.')
        if not enabled(config,s.device):raise ValueError('Source désactivée : '+s.device)
        if s.date:datetime.strptime(s.date,'%Y-%m-%d')
        if s.device=='Geo-Log' and not s.date:raise ValueError('Geo-Log : indiquez la journée de classement du journal. Un journal multijour reste groupé sous cette journée.')
        if not Path(s.path).is_dir():raise ValueError('Dossier introuvable : '+s.path)
    for i,s in enumerate(choices):
        for other in existing+choices[:i]:
            if is_within(s.path,other.path) or is_within(other.path,s.path):
                raise ValueError('Ce dossier recouvre une source déjà ajoutée : '+s.path+'\nRetirez l’ancienne entrée avant de l’ajouter en Auto.')
    return choices
