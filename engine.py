"""Local, copy-only ingestion engine. No GUI dependencies."""
from __future__ import annotations
import csv
import hashlib
import json
import os
import re
import shutil
import struct
import tempfile
import threading
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from exiftool_support import find_exiftool, probe, read_batch

CAMERAS = ['DJI Mini 4 Pro','DJI Air 3','DJI Neo 2','Insta360 X5','Insta360 Ace Pro 2','Pixel 11']
DEVICE_DEFAULTS = {d: d not in {'DJI Air 3','Insta360 Ace Pro 2'} for d in CAMERAS + ['Pixel 8 Pro','Garmin']}
SOFTWARE_DEFAULTS = {'Geo-Log':True,'Insta360 Studio':True,'LosslessCut':True}
SOCIAL_DEFAULTS = {'WhatsApp':True,'Instagram':True,'Facebook':True}
DEVICES = ['Auto'] + CAMERAS + ['Garmin','Geo-Log','Sélection','WhatsApp','Instagram','Facebook']
RAW_PHOTOS = {'.raw','.dng','.cr2','.cr3','.nef','.nrw','.arw','.sr2','.srf','.orf','.rw2','.raf','.pef','.srw','.rwl','.3fr','.fff','.iiq','.dcr','.kdc','.erf','.mef','.mos','.mrw','.x3f'}
PHOTOS = RAW_PHOTOS | {'.jpg','.jpeg','.png','.heic','.heif','.dng','.raw','.webp','.tif','.tiff'}
VIDEOS = {'.mp4','.mov','.m4v','.avi'}
FORBIDDEN = {'.insv','.insp','.360'}
COPY_EXTRAS = {'.srt','.lrv'}
GPS = {'.gpx','.kml','.kmz','.fit','.tcx'}
SIDECARS = {'.lrv','.srt','.lrf','.thm','.xmp','.json','.xml','.bin','.idx'}
ROUTES = {'Garmin':'01_GPS_JOURNAL/GARMIN','Geo-Log':'01_GPS_JOURNAL/GEOLOG','Pixel 11':'02_PIXEL11','Insta360 X5':'03_INSTA360_X5','Insta360 Ace Pro 2':'INSTA360_ACEPRO2','DJI Neo 2':'04_DJI_NEO2','DJI Air 3':'05_DJI_AIR3','DJI Mini 4 Pro':'05_DJI_MINI4PRO','Sélection':'06_SELECTION','WhatsApp':'07_PUBLICATION/WHATSAPP','Instagram':'07_PUBLICATION/INSTAGRAM','Facebook':'07_PUBLICATION/FACEBOOK'}

def enabled(c, device):
    if device in DEVICE_DEFAULTS:return c.devices.get(device,False)
    if device in {'Geo-Log'}:return c.software.get(device,False)
    if device == 'Sélection':return c.selection
    return c.social.get(device,False)

def policy(c, device, media_kind, suffix, confirmed=False):
    if c.exclude_srt_lrv and suffix in COPY_EXTRAS:return 'SRT/LRV exclu par le réglage d’import.'
    if suffix in FORBIDDEN:return 'Originaux 360 et proxies refusés. Fournissez uniquement des exports plats traités.'
    if c.exclude_raw and suffix in RAW_PHOTOS:return 'RAW/DNG exclu par le réglage d’import.'
    if device not in ROUTES:return 'Appareil ambigu : affectez explicitement la source.'
    if not enabled(c,device):return 'Désactivé dans les paramètres du roadtrip.'
    if device == 'Insta360 Ace Pro 2' and media_kind != 'Vidéo':return 'Cette caméra accepte uniquement des vidéos.'
    if device in CAMERAS + ['Sélection','WhatsApp'] and media_kind not in {'Photo','Vidéo'}:return 'Type non admis pour cette source (annexe sans média associé ?).'
    if device in {'Instagram','Facebook'} and media_kind not in {'Photo','Vidéo'} and suffix != '.txt':return 'Seuls les médias finaux et les légendes TXT sont admis.'
    return ''

@dataclass
class Source:
    path: str
    device: str = 'Auto'
    date: str = ''
    offset_hours: float = 0
    exports_confirmed: bool = False

@dataclass
class Config:
    destination: str = ''
    trip: str = 'Voyage_Vespa'
    sources: list[Source] = field(default_factory=list)
    start: str = ''
    end: str = ''
    timezone: str = 'Europe/Zurich'
    allow_mtime: bool = False
    verify: bool = True
    day_labels: dict = field(default_factory=dict)
    version: int = 2
    exiftool_path: str = ''
    exiftool_enabled: bool = True

    exclude_raw: bool = True
    exclude_srt_lrv: bool = True
    region: str = ''
    devices: dict = field(default_factory=lambda: DEVICE_DEFAULTS.copy())
    software: dict = field(default_factory=lambda: SOFTWARE_DEFAULTS.copy())
    social: dict = field(default_factory=lambda: SOCIAL_DEFAULTS.copy())
    mirror_facebook: bool = True
    selection: bool = True

    def __post_init__(self):
        self.normalize()

    def normalize(self):
        for group, defaults in [('devices', DEVICE_DEFAULTS), ('software', SOFTWARE_DEFAULTS), ('social', SOCIAL_DEFAULTS)]:
            values = getattr(self, group)
            setattr(self, group, {key: bool(values.get(key, default)) for key, default in defaults.items()})
        self.sources = [source for source in self.sources if source.device in DEVICES]
        self.software['LosslessCut']=any(self.devices.get(d,False) for d in CAMERAS)
        self.software['Insta360 Studio']=bool(self.devices.get('Insta360 X5',False))

    def save(self, path):
        self.normalize()
        Path(path).write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding='utf-8')

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict) or data.get('version') != 2:
            raise ValueError('Profil non reconnu : format version 2 requis ; recréez les anciens profils pour confirmer les appareils et les exports X5.')
        data['sources'] = [Source(**s) for s in data.get('sources', [])]
        result = cls(**data)
        if not isinstance(result.day_labels, dict):
            raise ValueError('Les noms des journées doivent être un objet JSON.')
        return result

@dataclass
class Row:
    source: str
    device: str = 'Inconnu'
    kind: str = ''
    date: str = ''
    date_origin: str = ''
    target: str = ''
    size: int = 0
    status: str = 'À vérifier'
    detail: str = ''
    digest: str = ''
    mtime_ns: int = 0

class Cancelled(Exception): pass

def check(stop):
    if stop and stop.is_set(): raise Cancelled()

def sha(path, stop=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            check(stop)
            block = f.read(4 * 1024 * 1024)
            if not block: break
            h.update(block)
    return h.hexdigest()

def safe_name(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or value in {'.','..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]', value) or value.endswith('.') or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', value, re.I):
        raise ValueError(f'Nom de dossier invalide : {value!r}')
    return value

def is_within(child, parent):
    return Path(child).resolve().is_relative_to(Path(parent).resolve())

def validate(c):
    c.normalize()
    sources=[s for s in c.sources if s.device=='Auto' or enabled(c,s.device)]
    safe_name(c.trip)
    if not c.destination.strip(): raise ValueError('Choisissez un dossier destination.')
    ZoneInfo(c.timezone)
    for d in [c.start,c.end] + [s.date for s in sources]:
        if d: datetime.strptime(d, '%Y-%m-%d')
    if c.start and c.end and c.start > c.end: raise ValueError('La date de début doit précéder la date de fin.')
    if not c.sources: raise ValueError('Ajoutez au moins une source.')
    dest = Path(c.destination).resolve() / c.trip
    for day, label in c.day_labels.items():
        datetime.strptime(day,'%Y-%m-%d')
        if label:safe_name(label)
    for s in sources:
        if not Path(s.path).is_dir(): raise ValueError(f'Source introuvable : {s.path}')
        if s.device in {'Geo-Log','WhatsApp','Instagram','Facebook','Sélection'} and not s.date:raise ValueError('Imposez la journée de cet export / de cette sélection : '+s.device)
        if s.device not in DEVICES: raise ValueError(f'Appareil inconnu : {s.device}')
        if not -48 <= float(s.offset_hours) <= 48: raise ValueError('Le décalage doit être compris entre −48 et +48 heures.')
        if is_within(dest, s.path) or is_within(s.path, dest): raise ValueError('La destination du voyage et les sources ne doivent pas être imbriquées.')
    for i,s in enumerate(sources):
        for other in sources[i+1:]:
            if is_within(s.path,other.path) or is_within(other.path,s.path):
                raise ValueError('Deux sources se recouvrent. Choisissez des dossiers distincts pour éviter une affectation ambiguë.')
    return dest

def kind(path):
    e=path.suffix.lower()
    return 'Photo' if e in PHOTOS else 'Vidéo' if e in VIDEOS else 'GPS' if e in GPS else 'Annexe' if e in SIDECARS else 'Document'

def parse_date(text):
    text = str(text).strip().replace('\x00','')
    text = re.sub(r'^(\d{4}):(\d{2}):(\d{2})', r'\1-\2-\3', text)
    try: return datetime.fromisoformat(text.replace('Z','+00:00'))
    except ValueError: return None

def mp4_date(path):
    # ISO base media mvhd creation time, versions 0 and 1. Read only atom headers.
    with path.open('rb') as f:
        def walk(start,end):
            pos=start
            while pos+8<=end:
                f.seek(pos); size,typ=struct.unpack('>I4s',f.read(8)); header=8
                if size==1:
                    raw=f.read(8)
                    if len(raw)!=8: return None
                    size=struct.unpack('>Q',raw)[0]; header=16
                if size==0: size=end-pos
                if size<header or pos+size>end: return None
                if typ==b'moov':
                    found=walk(pos+header,pos+size)
                    if found: return found
                if typ==b'mvhd' and size>=header+12:
                    f.seek(pos+header); version=f.read(4)[0]
                    raw=f.read(8 if version==1 else 4)
                    sec=int.from_bytes(raw,'big')
                    if sec:
                        d=datetime(1904,1,1,tzinfo=timezone.utc)+timedelta(seconds=sec)
                        if 1990<=d.year<=2100: return d
                pos+=size
        return walk(0,path.stat().st_size)

def exiftool_metadata(data):
    def values(tag):
        return [(k,v) for k,v in data.items() if k.split(':')[-1]==tag and isinstance(v,str)]
    model=' '.join(str(v) for tag in ['Make','Model','CameraModelName'] for k,v in values(tag))
    warnings=[str(v) for k,v in data.items() if k.split(':')[-1] in {'Error','Warning'}]
    for tag in ['SubSecDateTimeOriginal','DateTimeOriginal','SubSecCreateDate','CreationDate','CreateDate','MediaCreateDate','TrackCreateDate','GPSDateTime']:
        for key,value in values(tag):
            dt=parse_date(value)
            if not dt or not 1990<=dt.year<=2100:continue
            if not dt.tzinfo:
                offsets=values('OffsetTimeOriginal' if 'Original' in tag else 'OffsetTimeDigitized')
                if tag in {'SubSecDateTimeOriginal','DateTimeOriginal','SubSecCreateDate'} or (tag=='CreateDate' and key.startswith('ExifIFD:')):
                    if offsets:dt=parse_date(dt.isoformat()+offsets[0][1]) or dt
                # Integer QuickTime times are UTC by specification; string dates remain local.
                if not dt.tzinfo and (tag=='GPSDateTime' or (key.split(':')[0] in {'QuickTime','Track1','Track2','Media1','Media2'} and tag in {'CreateDate','MediaCreateDate','TrackCreateDate'})):
                    dt=dt.replace(tzinfo=timezone.utc)
            return dt,'ExifTool / '+key,model,warnings
    return None,'',model,warnings

def metadata(path, external=None):
    model=''; dt=None; origin=''; warnings=[]
    if external:dt,origin,model,warnings=exiftool_metadata(external)
    if path.suffix.lower() in PHOTOS and not dt:
        try:
            from PIL import Image
            with Image.open(path) as im:
                exif=im.getexif(); model=model or str(exif.get(272,''))
                sub=exif.get_ifd(34665)
                for key in [36867,36868,306]:
                    dt=parse_date(sub.get(key) or exif.get(key) or '')
                    if dt:
                        offset=sub.get(36881) or sub.get(36880)
                        if offset and not dt.tzinfo:
                            dt=parse_date(dt.isoformat()+str(offset)) or dt
                        origin='EXIF'; break
        except Exception as e: warnings.append('EXIF indisponible : '+str(e)[:100])
    if not dt and path.suffix.lower() in {'.mp4','.mov','.m4v','.insv'}:
        try:
            dt=mp4_date(path)
            if dt: origin='Métadonnées vidéo (UTC)'
        except Exception as e: warnings.append('Date vidéo illisible : '+str(e)[:100])
    if not dt and path.suffix.lower() in {'.gpx','.kml','.tcx'}:
        try:
            for event, el in ET.iterparse(path,events=('end',)):
                if el.tag.split('}')[-1].lower() in {'time','when'} and el.text:
                    dt=parse_date(el.text)
                    if dt: origin='Trace GPS'; break
                el.clear()
        except Exception as e: warnings.append('Trace illisible : '+str(e)[:100])
    if not dt:
        match=re.search(r'(?<!\d)(20\d{2})[-_]?(\d{2})[-_]?(\d{2})(?:[T_ -]?(\d{2})[.:_-]?(\d{2})[.:_-]?(\d{2}))?',path.stem)
        if match:
            try:
                dt=datetime(*[int(v or 0) for v in match.groups()]); origin='Nom du fichier'
            except ValueError: pass
    return dt,origin,model,warnings

def detect(path,model):
    def match(text):
        t=re.sub(r'[-_ ]','',text.lower())
        for word,dev in [('pixel8','Inconnu'),('acepro2','Insta360 Ace Pro 2'),('x5','Insta360 X5'),('neo2','DJI Neo 2'),('mini4pro','DJI Mini 4 Pro'),('air3','DJI Air 3'),('pixel11','Pixel 11'),('geolog','Geo-Log'),('garmin','Garmin')]:
            if word in t:return dev
        return ''
    return match(model) or match(str(path)) or ('Garmin' if path.suffix.lower()=='.fit' else 'Inconnu')

def folder(device,k,c=None):
    base=ROUTES[device]
    if c and device in {'Instagram','Facebook'} and c.mirror_facebook and c.social.get('Instagram') and c.social.get('Facebook'):
        base='07_PUBLICATION/INSTAGRAM_FACEBOOK'
    if device in CAMERAS + ['Sélection']:
        return base+'/'+('PHOTO' if k=='Photo' else 'VIDEO')
    return base

def structure_text(c):
    """Configuration-only folder template: no inventory and no filesystem access."""
    branch={}
    for device in ROUTES:
        if not enabled(c,device):continue
        kinds=['Photo','Vidéo'] if device in CAMERAS+['Sélection'] else ['']
        if device=='Insta360 Ace Pro 2':kinds=['Vidéo']
        for media_kind in kinds:
            node=branch
            for part in folder(device,media_kind,c).split('/'):
                node=node.setdefault(part,{})
    lines=[(c.trip or 'Voyage_Vespa')+'/']
    if not branch:return '\n'.join(lines)
    # One template applies to every day; named days remain visible when supplied.
    days=[d+('_'+name if name else '') for d,name in sorted(c.day_labels.items())
          if (not c.start or d>=c.start) and (not c.end or d<=c.end)] or ['<journée>']
    def walk(node,prefix):
        items=sorted(node.items())
        for i,(name,children) in enumerate(items):
            last=i==len(items)-1
            lines.append(prefix+('└── ' if last else '├── ')+name+'/')
            walk(children,prefix+('    ' if last else '│   '))
    for i,day in enumerate(days):
        last=i==len(days)-1
        lines.append(('└── ' if last else '├── ')+day+'/')
        walk(branch,'    ' if last else '│   ')
    return '\n'.join(lines)

def preview_rows(previous,c,rows):
    """Reproject cached, analyzed targets without reading or creating files."""
    import copy
    result=[]
    oldroot=(Path(previous.destination)/previous.trip).resolve()
    root=(Path(c.destination)/c.trip).resolve()
    for original in rows:
        if not enabled(c,original.device):continue
        if original.device == 'Insta360 Ace Pro 2' and original.kind!='Vidéo':continue
        if (c.start and original.date<c.start) or (c.end and original.date>c.end):continue
        if original.status not in {'Prêt','Copié','Doublon','Hors période'}:continue
        try:
            if original.target:
                relative=Path(original.target).resolve().relative_to(oldroot)
                oldfolder=Path(folder(original.device,original.kind,previous))
                tail=Path(*relative.parts[1:]).relative_to(oldfolder)
            else:
                spec=next((s for s in previous.sources if is_within(original.source,s.path)),None)
                if spec is None or original.kind=='Annexe':continue
                tail=Path(original.source).relative_to(Path(spec.path))
                if original.device=='WhatsApp':tail=Path(('photo' if original.kind=='Photo' else 'video')+tail.suffix.lower())
        except ValueError:continue
        day=original.date+('_'+c.day_labels[original.date] if c.day_labels.get(original.date) else '')
        row=copy.copy(original)
        if row.status=='Hors période':row.status='Prêt'
        row.target=str(root/day/folder(row.device,row.kind,c)/tail)
        result.append(row)
    return result

def tree_text(c,rows):
    root=(Path(c.destination)/c.trip).resolve()
    paths=sorted({str(Path(r.target).resolve().relative_to(root)) for r in rows if r.target and is_within(r.target,root) and r.status in {'Prêt','Copié','Doublon'} and enabled(c,r.device)})
    tree={}
    for p in paths:
        branch=tree
        for part in Path(p).parts:branch=branch.setdefault(part,{})
    lines=[c.trip+'/']
    def walk(branch,indent=''):
        for key,val in branch.items():
            lines.append(indent+'  '+key+('/' if val else ''))
            walk(val,indent+'  ')
    walk(tree)
    return '\n'.join(lines) if paths else 'Aucun dossier prévu. Ajoutez des sources puis analysez leur contenu.'

def scan(c, emit=lambda *a:None, stop=None):
    root=validate(c); rows=[]; files=[]; seen=set(); planned={}
    executable=find_exiftool(c.exiftool_path) if c.exiftool_enabled else ''
    tool_message='ExifTool désactivé — lecture interne.' if not c.exiftool_enabled else 'ExifTool introuvable — lecture interne. Utilisez le bouton ExifTool…'
    if executable:
        try:tool_message=f'ExifTool {probe(executable,lambda:check(stop))} : {executable}'
        except Cancelled:raise
        except Exception as e:tool_message=f'ExifTool indisponible : {e} Lecture interne utilisée.';executable=''
    emit('log',tool_message);emit('exiftool',tool_message)
    for spec in c.sources:
        if spec.device!='Auto' and not enabled(c,spec.device):continue
        def walk_error(e):
            rows.append(Row(str(e.filename),status='Erreur',detail=str(e)))
            emit('log',str(e))
        for directory,dirs,names in os.walk(spec.path,followlinks=False,onerror=walk_error):
            check(stop)
            dirs[:]=sorted(d for d in dirs if not Path(directory,d).is_symlink() and not Path(directory,d).is_junction())
            for name in sorted(names):
                p=Path(directory,name)
                if p.is_symlink(): continue
                key=str(p.resolve()).casefold()
                if key not in seen:
                    seen.add(key)
                    if c.exclude_srt_lrv and p.suffix.lower() in COPY_EXTRAS:
                        rows.append(Row(str(p),device=spec.device,kind='Annexe',status='Exclu',detail='SRT/LRV exclu par le réglage d’import.'))
                        emit('log','Exclu | '+str(p)+' | SRT/LRV exclu par le réglage d’import.')
                    elif p.suffix.lower() in FORBIDDEN:
                        rows.append(Row(str(p),device=spec.device,kind='360 / proxy',status='Exclu',detail='Original 360 / proxy refusé.'))
                        emit('log','Exclu | '+str(p)+' | Original 360 / proxy refusé.')
                    else:files.append((p,spec))
            emit('progress',(0,len(files),'Recherche des fichiers…'))
    # Metadata first, so sidecars can inherit the media date, including across midnight.
    cache={}
    external={}
    for i,(p,s) in enumerate(files):
        check(stop)
        if executable and i%64==0:
            emit('progress',(i,len(files),'Lecture ExifTool…'))
            try:external=read_batch(executable,[f for f,spec in files[i:i+64]],lambda:check(stop))
            except Cancelled:raise
            except Exception as e:
                external={};emit('log',f'ExifTool : {e} Lecture interne pour ce lot.')
                emit('exiftool','ExifTool : problème de lecture ; détails dans le journal.')
        try: cache[str(p)]=metadata(p,external.get(str(p.resolve()).casefold()))
        except Exception as e: cache[str(p)]=(None,'','',[str(e)])
        emit('progress',(i+1,len(files),'Lecture des dates et appareils…'))
    cache_lower={k.casefold():v for k,v in cache.items()}
    for i,(p,s) in enumerate(files):
        check(stop); r=Row(str(p),kind=kind(p)); rows.append(r)
        try:
            stat=p.stat(); r.size=stat.st_size; r.mtime_ns=stat.st_mtime_ns
            dt,origin,model,warnings=cache[str(p)]
            r.device=s.device if s.device!='Auto' else detect(p,model)
            route_kind=r.kind
            associated=False
            if p.suffix.lower() in SIDECARS:
                for e in sorted((PHOTOS|VIDEOS)-(RAW_PHOTOS if c.exclude_raw else set())):
                    sibling=cache_lower.get(str(p.with_suffix(e)).casefold())
                    if sibling:
                        associated=True
                        route_kind=kind(p.with_suffix(e))
                        if not dt and sibling[0]:dt,origin=sibling[:2];origin='Fichier associé : '+origin
                        if r.device=='Inconnu':r.device=detect(p.with_suffix(e),sibling[2])
                        break
            reason=policy(c,r.device,route_kind,p.suffix.lower(),s.exports_confirmed)
            if r.device == 'Insta360 Ace Pro 2' and r.kind!='Vidéo':reason='Cette caméra accepte uniquement les fichiers vidéo.'
            if r.device=='WhatsApp' and r.kind not in {'Photo','Vidéo'}:reason='WhatsApp : seulement la photo et la vidéo finales.'
            if r.device in CAMERAS and r.kind=='Annexe' and not associated:reason='Annexe sans média associé : exclue.'
            if reason:
                r.status='À vérifier' if 'ambigu' in reason or 'Confirmez' in reason else 'Exclu'
                r.detail=reason;continue
            if s.date: dt=datetime.strptime(s.date,'%Y-%m-%d'); origin='Date imposée à la source'
            elif dt:
                if dt.tzinfo: dt=dt.astimezone(ZoneInfo(c.timezone)).replace(tzinfo=None)
                dt+=timedelta(hours=float(s.offset_hours))
            elif c.allow_mtime:
                dt=datetime.fromtimestamp(stat.st_mtime,ZoneInfo(c.timezone)).replace(tzinfo=None)+timedelta(hours=float(s.offset_hours)); origin='Modification du fichier (à contrôler)'
            r.date_origin=origin
            if not dt: r.detail='Date introuvable. Choisissez une date pour cette source.'; continue
            r.date=dt.strftime('%Y-%m-%d')
            if (c.start and r.date<c.start) or (c.end and r.date>c.end):
                r.status='Hors période'; r.detail='Exclu par le filtre de dates.'; continue
            if r.device not in ROUTES: r.detail='Appareil ambigu. Affectez cette source à un appareil.'; continue
            day=r.date+('_'+c.day_labels[r.date] if c.day_labels.get(r.date) else '')
            relative=p.relative_to(Path(s.path))
            target=root/day/folder(r.device,route_kind,c)/relative
            if r.device=='WhatsApp':
                target=root/day/folder(r.device,route_kind,c)/(('photo' if route_kind=='Photo' else 'video')+p.suffix.lower())
                slot=str(target.with_suffix('')).casefold()
                others=[f for f in target.parent.glob('*') if f.is_file() and kind(f)==route_kind and f.name.casefold()!=target.name.casefold()] if target.parent.exists() else []
                if others or slot in planned and planned[slot]!=str(target).casefold():
                    r.status='Conflit';r.detail='WhatsApp : un seul fichier final par type et par jour. Retirez ou archivez manuellement l’ancien choix.';continue
                planned[slot]=str(target).casefold()
            if not is_within(target,root): raise ValueError('Destination hors du voyage (lien de dossier).')
            r.target=str(target); r.digest=sha(p,stop)
            if p.stat().st_size!=r.size or p.stat().st_mtime_ns!=r.mtime_ns: raise ValueError('Fichier modifié pendant la lecture. Relancez un aperçu.')
            key=str(target).casefold()
            if target.exists():
                if target.is_file() and target.stat().st_size==r.size and sha(target,stop)==r.digest:
                    r.status='Doublon'; r.detail='Copie identique déjà présente (SHA-256).'
                else: r.status='Conflit'; r.detail='Ce nom existe avec un contenu différent. Aucun écrasement ; utilisez une autre source/destination.'
            elif key in planned:
                r.status='Doublon' if planned[key]==r.digest else 'Conflit'
                r.detail='Même destination dans cet import.'
            else:
                r.status='Prêt'; planned[key]=r.digest
            if warnings: r.detail+=' '+' ; '.join(warnings)
            if 'Modification' in origin: r.detail+=' Date de secours : vérifiez la journée.'
        except Cancelled: raise
        except Exception as e: r.status='Erreur'; r.detail=str(e)
        finally:
            emit('log',f'{r.status} | {p.name} | {r.device} | {r.date} | {r.detail}')
            emit('progress',(i+1,len(files),'Préparation du classement…'))
    return rows

def execute(c,rows,emit=lambda *a:None,stop=None):
    root=validate(c)
    for r in rows:
        if r.status=='Prêt' and (not enabled(c,r.device) or r.device == 'Insta360 Ace Pro 2' and r.kind!='Vidéo'):
            r.status='Exclu';r.detail='Source ou type de média désactivé.'
        if c.exclude_srt_lrv and Path(r.source).suffix.lower() in COPY_EXTRAS and r.status=='Prêt':
            r.status='Exclu';r.detail='SRT/LRV exclu par le réglage d’import.'
        if c.exclude_raw and Path(r.source).suffix.lower() in RAW_PHOTOS and r.status=='Prêt':
            r.status='Exclu';r.detail='RAW/DNG exclu par le réglage d’import.'
    ready=[r for r in rows if r.status=='Prêt']
    ancestor=root
    while not ancestor.exists():ancestor=ancestor.parent
    required=sum(r.size for r in ready)
    if shutil.disk_usage(ancestor).free < required+16*1024*1024:raise ValueError('Espace disque insuffisant pour cet import.')
    for i,r in enumerate(ready):
        check(stop); temp=None
        try:
            src=Path(r.source); dest=Path(r.target)
            if not is_within(dest,root):raise ValueError('Destination hors du voyage.')
            st=src.stat()
            if st.st_size!=r.size or st.st_mtime_ns!=r.mtime_ns or sha(src,stop)!=r.digest:
                raise ValueError('Source modifiée depuis l’aperçu. Relancez l’analyse.')
            if dest.exists():
                if dest.is_file() and sha(dest,stop)==r.digest:
                    r.status='Doublon'; r.detail='Copie identique apparue depuis l’aperçu.'; continue
                raise FileExistsError('Destination apparue depuis l’aperçu : aucun écrasement.')
            if not enabled(c,r.device):raise ValueError('Source désactivée depuis l’aperçu.')
            if r.device=='WhatsApp' and dest.parent.exists():
                if any(f.is_file() and kind(f)==r.kind and f.name.casefold()!=dest.name.casefold() for f in dest.parent.iterdir()):
                    raise ValueError('WhatsApp : un autre fichier final de ce type est apparu depuis l’aperçu.')
            dest.parent.mkdir(parents=True,exist_ok=True)
            fd,temp=tempfile.mkstemp(prefix='.vespa-',suffix='.partial',dir=dest.parent)
            with os.fdopen(fd,'wb') as out,src.open('rb') as inp:
                copied=0
                while True:
                    check(stop); block=inp.read(4*1024*1024)
                    if not block:break
                    out.write(block);copied+=len(block)
                    emit('progress',(i+copied/max(r.size,1),len(ready),'Copie : '+src.name))
                out.flush();os.fsync(out.fileno())
            if c.verify and sha(temp,stop)!=r.digest:raise IOError('La vérification SHA-256 de la copie a échoué.')
            shutil.copystat(src,temp)
            check(stop)
            # Windows rename never overwrites. POSIX link is atomic and exclusive.
            if os.name=='nt':os.rename(temp,dest)
            else:os.link(temp,dest);os.unlink(temp)
            temp=None; r.status='Copié';r.detail='Copie vérifiée (SHA-256).' if c.verify else 'Copie terminée.'
        except Cancelled:raise
        except Exception as e:r.status='Erreur';r.detail=str(e)
        finally:
            if temp:
                try:Path(temp).unlink(missing_ok=True)
                except OSError:pass
            if r.status!='Copié' and r.target:
                parent=Path(r.target).parent
                while parent!=root.parent and is_within(parent,root):
                    try:parent.rmdir()
                    except OSError:break
                    parent=parent.parent
            emit('log',f'{r.status} | {r.source} | {r.detail}')
            emit('progress',(i+1,len(ready),'Copie des fichiers…'))
    return rows

def export_csv(path,rows):
    fields=list(Row.__dataclass_fields__)
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader()
        for row in rows:
            values=asdict(row)
            # Prevent spreadsheet formulas when opening a report from untrusted filenames.
            values={k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in values.items()}
            w.writerow(values)

def report_path(c):
    root=Path(c.destination)/c.trip/'00_TRIP'/'NOTES'
    if not is_within(root,Path(c.destination)/c.trip):raise ValueError('Dossier de rapport hors du voyage.')
    root.mkdir(parents=True,exist_ok=True)
    return root/('ingestion_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]+'.csv')
