"""Optional ExifTool reader: fixed read-only arguments, no shell, UTF-8 stdin."""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TAGS = ['SubSecDateTimeOriginal','DateTimeOriginal','SubSecCreateDate','CreationDate',
        'CreateDate','MediaCreateDate','TrackCreateDate','GPSDateTime',
        'OffsetTimeOriginal','OffsetTimeDigitized','Model','CameraModelName','Make']

def find_exiftool(configured=''):
    if configured:
        path=Path(configured).expanduser()
        return str(path.resolve()) if path.is_file() else ''
    appdir=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
    for folder in [appdir,appdir/'tools',appdir.parent,appdir.parent/'tools']:
        path=folder/'exiftool.exe'
        if path.is_file():return str(path.resolve())
    return shutil.which('exiftool.exe') or shutil.which('exiftool') or ''

def run(executable,args,input_data=None,timeout=30,check=lambda:None):
    check()
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    proc=subprocess.Popen([executable,*args],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,shell=False,creationflags=flags)
    deadline=time.monotonic()+timeout
    try:
        while True:
            check()
            try:
                out,err=proc.communicate(input=input_data,timeout=.15)
                return proc.returncode,out.decode('utf-8-sig',errors='replace'),err.decode('utf-8',errors='replace')
            except subprocess.TimeoutExpired:
                input_data=None
                if time.monotonic()>=deadline:raise TimeoutError('ExifTool ne répond pas dans le délai prévu.')
    finally:
        if proc.poll() is None:proc.kill()
        proc.communicate()

def probe(executable,check=lambda:None):
    if '(-k)' in Path(executable).name.lower():
        raise ValueError('Renommez exiftool(-k).exe en exiftool.exe et gardez exiftool_files à côté.')
    code,out,err=run(executable,['-config','','-ver'],timeout=8,check=check)
    version=out.strip()
    if code or not re.fullmatch(r'\d+\.\d+(?:_\d+)?',version):
        raise ValueError('ExifTool invalide ou incomplet. '+(err.strip()[:200] or 'Vérifiez le fichier et son dossier exiftool_files.'))
    return version

def read_batch(executable,paths,check=lambda:None):
    absolute=[str(Path(p).resolve()) for p in paths]
    if any('\n' in p or '\r' in p for p in absolute):raise ValueError('Nom contenant un saut de ligne : lecture interne utilisée.')
    args=['-config','','-j','-G1','-a','-s','-charset','filename=UTF8']+['-'+t for t in TAGS]+['-@','-']
    code,out,err=run(executable,args,('\n'.join(absolute)+'\n').encode('utf-8'),check=check)
    try:data=json.loads(out)
    except ValueError:raise ValueError('Réponse ExifTool illisible. '+err.strip()[:200])
    if not isinstance(data,list):raise ValueError('Réponse ExifTool inattendue.')
    result={}
    for item in data:
        if isinstance(item,dict) and isinstance(item.get('SourceFile'),str):
            result[str(Path(item['SourceFile']).resolve()).casefold()]=item
    if code and not result:raise ValueError('Lecture ExifTool impossible. '+err.strip()[:200])
    return result
