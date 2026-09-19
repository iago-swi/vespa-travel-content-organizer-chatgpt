import csv
import json
import struct
import tempfile
import threading
import unittest
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
from engine import *

class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.src=self.base/'source';self.src.mkdir();self.dest=self.base/'archive';self.c=Config(str(self.dest),'Alpes',[Source(str(self.src),'Pixel 11')])
    def tearDown(self):self.tmp.cleanup()
    def file(self,name,data=b'content'):
        p=self.src/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p
    def test_dry_run_no_writes(self):
        self.file('PXL_20260907_120000.jpg');rows=scan(self.c)
        self.assertEqual(rows[0].status,'Prêt');self.assertFalse(self.dest.exists())
        self.assertIn('2026-09-07',rows[0].target)
    def test_execute_and_resume(self):
        p=self.file('PXL_20260907_120000.jpg');rows=scan(self.c);execute(self.c,rows)
        self.assertEqual(rows[0].status,'Copié');self.assertEqual(Path(rows[0].target).read_bytes(),p.read_bytes());self.assertTrue(p.exists())
        self.assertFalse((self.dest/'Alpes/2026-09-07/06_SELECTION').exists())
        self.assertFalse((self.dest/'Alpes/2026-09-07/07_PUBLICATION').exists())
        self.assertEqual(scan(self.c)[0].status,'Doublon')
    def test_conflict_never_overwrites(self):
        self.file('PXL_20260907_120000.jpg');rows=scan(self.c);target=Path(rows[0].target);target.parent.mkdir(parents=True);target.write_bytes(b'different')
        execute(self.c,rows);self.assertEqual(rows[0].status,'Erreur');self.assertEqual(target.read_bytes(),b'different');self.assertEqual(scan(self.c)[0].status,'Conflit')
    def test_source_changed_after_preview(self):
        p=self.file('PXL_20260907_120000.jpg');rows=scan(self.c);p.write_bytes(b'changed');execute(self.c,rows);self.assertEqual(rows[0].status,'Erreur');self.assertFalse(Path(rows[0].target).exists())
    def test_cancel_during_copy_cleans_partial(self):
        self.file('VID_20260907_120000.mp4',b'0'*(10*1024*1024));rows=scan(self.c);stop=threading.Event()
        def emit(k,v):
            if k=='progress' and v[2].startswith('Copie :'):stop.set()
        with self.assertRaises(Cancelled):execute(self.c,rows,emit,stop)
        self.assertFalse(Path(rows[0].target).exists());self.assertEqual(list(self.dest.rglob('*.partial')),[])
    def test_unknown_device_requires_review(self):
        self.c.sources[0].device='Auto';self.file('DJI_20260907_120000.jpg');self.assertEqual(scan(self.c)[0].status,'À vérifier')
    def test_no_date_requires_review(self):
        self.file('photo.jpg');self.assertEqual(scan(self.c)[0].status,'À vérifier')
        self.c.sources[0].date='2026-09-07';self.assertEqual(scan(self.c)[0].status,'Prêt')
    def test_period(self):
        self.file('PXL_20260907_120000.jpg');self.c.start='2026-09-08';self.assertEqual(scan(self.c)[0].status,'Hors période')
    def test_exif(self):
        im=Image.new('RGB',(8,8),'blue');e=Image.Exif();e[272]='Pixel 11';e[306]='2026:09:07 12:30:00';im.save(self.src/'photo.jpg',exif=e)
        self.c.sources[0].device='Auto';r=scan(self.c)[0];self.assertEqual((r.device,r.date,r.date_origin),('Pixel 11','2026-09-07','EXIF'))
    def test_video_utc_timezone(self):
        self.c.exiftool_enabled=False
        sec=int((datetime(2026,9,7,23,30,tzinfo=timezone.utc)-datetime(1904,1,1,tzinfo=timezone.utc)).total_seconds());body=b'\0'*4+struct.pack('>I',sec)+b'\0'*4;atom=struct.pack('>I4s',len(body)+8,b'mvhd')+body
        self.file('video.mp4',struct.pack('>I4s',len(atom)+8,b'moov')+atom);r=scan(self.c)[0];self.assertEqual(r.date,'2026-09-08');self.assertIn('vidéo',r.date_origin)
    def test_gpx_and_offset(self):
        self.c.sources[0].device='Garmin';self.c.sources[0].offset_hours=-3;self.file('trace.gpx',b'<gpx><trk><time>2026-09-07T00:30:00Z</time></trk></gpx>');self.assertEqual(scan(self.c)[0].date,'2026-09-06')
    def test_all_routes(self):
        self.file('20260907_120000.mp4')
        self.c.devices={k:True for k in DEVICE_DEFAULTS};self.c.software={k:True for k in SOFTWARE_DEFAULTS};self.c.social={k:True for k in SOCIAL_DEFAULTS};self.c.mirror_facebook=False
        for d in ROUTES:
            self.c.sources[0]=Source(str(self.src),d,'2026-09-07',exports_confirmed=True);r=scan(self.c)[0];self.assertIn(str(Path(ROUTES[d])),r.target)
    def test_journal_relative_links(self):
        self.c.sources[0]=Source(str(self.src),'Geo-Log','2026-09-07');self.file('export/index.html',b'<img src="MEDIA/photo.jpg">');self.file('export/MEDIA/photo.jpg');rows=scan(self.c);execute(self.c,rows)
        root=self.dest/'Alpes/2026-09-07/01_GPS_JOURNAL/GEOLOG/export';self.assertTrue((root/'index.html').exists());self.assertTrue((root/'MEDIA/photo.jpg').exists())
    def test_sidecar_follows_photo(self):
        im=Image.new('RGB',(8,8));e=Image.Exif();e[306]='2026:09:07 12:30:00';im.save(self.src/'photo.jpg',exif=e);self.file('photo.xmp');r=next(r for r in scan(self.c) if r.kind=='Annexe');self.assertEqual(r.date,'2026-09-07');self.assertIn('PHOTO',r.target)
    def test_profile_roundtrip(self):
        self.c.day_labels={'2026-09-07':'Furka_Grimsel'};p=self.base/'profile.json';self.c.save(p);self.assertEqual(Config.load(p),self.c)
    def test_legacy_profile_rejected(self):
        p=self.base/'profile.json';p.write_text('{}');self.assertRaises(ValueError,Config.load,p)
    def test_names_and_nested_paths(self):
        self.c.trip='../bad';self.assertRaises(ValueError,validate,self.c);self.c.trip='Alpes';self.c.destination=str(self.src);self.assertRaises(ValueError,validate,self.c)
    def test_overlapping_sources(self):
        self.c.sources.append(Source(str(self.src),'Garmin'));self.assertRaises(ValueError,validate,self.c)
    def test_report_bom_and_formula_escape(self):
        p=self.base/'report.csv';export_csv(p,[Row('=CMD()',detail='é')]);self.assertTrue(p.read_bytes().startswith(b'\xef\xbb\xbf'))
        with p.open(encoding='utf-8-sig') as f:r=list(csv.DictReader(f,delimiter=';'))[0]
        self.assertEqual(r['source'],"'=CMD()");self.assertEqual(r['detail'],'é')
    def test_mtime_and_day_label(self):
        self.file('photo.jpg');self.c.allow_mtime=True;r=scan(self.c)[0];self.assertEqual(r.status,'Prêt');self.assertIn('Modification',r.date_origin)
        self.c.sources[0].date='2026-09-07';self.c.day_labels={'2026-09-07':'Furka'};self.assertIn('2026-09-07_Furka',scan(self.c)[0].target)

if __name__=='__main__':unittest.main(verbosity=2)
