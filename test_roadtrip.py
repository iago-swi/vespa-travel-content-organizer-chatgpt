import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import *

class RoadtripTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.src=self.root/'input';self.src.mkdir();self.c=Config(str(self.root/'output'),'Trip',[Source(str(self.src),'Pixel 11')],exiftool_enabled=False,exclude_raw=False,exclude_srt_lrv=False)
    def tearDown(self):self.tmp.cleanup()
    def put(self,name):p=self.src/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(name.encode());return p
    def test_defaults_and_forced_software(self):
        c=self.c;self.assertFalse(c.devices['DJI Air 3']);self.assertFalse(c.devices['Insta360 Ace Pro 2'])
        c.software['LosslessCut']=False;c.software['Insta360 Studio']=False;c.normalize();self.assertTrue(c.software['LosslessCut']);self.assertTrue(c.software['Insta360 Studio'])
    def test_editors_follow_devices_both_directions(self):
        c=self.c
        for d in ['DJI Mini 4 Pro','DJI Air 3','DJI Neo 2','Insta360 X5','Insta360 Ace Pro 2','Pixel 11']:c.devices[d]=False
        c.normalize();self.assertFalse(c.software['LosslessCut']);self.assertFalse(c.software['Insta360 Studio'])
        for d in ['DJI Mini 4 Pro','DJI Air 3','DJI Neo 2','Insta360 X5','Insta360 Ace Pro 2','Pixel 11']:
            c.devices[d]=True;c.normalize();self.assertTrue(c.software['LosslessCut'])
            c.devices[d]=False;c.normalize();self.assertFalse(c.software['LosslessCut'])
        c.devices['Insta360 X5']=True;c.normalize();self.assertTrue(c.software['Insta360 Studio'])
    def test_unnamed_day_persists_without_folder_suffix(self):
        self.put('20260907.jpg');self.c.day_labels={'2026-09-07':''}
        validate(self.c)
        profile=self.root/'profile.json';self.c.save(profile);c=Config.load(profile)
        self.assertEqual(c.day_labels,{'2026-09-07':''})
        rows=scan(c);self.assertEqual(rows[0].status,'Prêt')
        self.assertIn('/2026-09-07/',Path(rows[0].target).as_posix())
    def test_exclude_raw_keeps_jpg_png_video_and_sources(self):
        for ext in ['DNG','RAW','NEF','ARW','jpg','png','mp4']:self.put('20260907.'+ext)
        self.c.exclude_raw=True;rows=scan(self.c)
        for r in rows:self.assertEqual(r.status,'Exclu' if Path(r.source).suffix.lower() in RAW_PHOTOS else 'Prêt')
        execute(self.c,rows)
        self.assertEqual(len(list(self.src.iterdir())),7)
        self.assertEqual({p.suffix for p in (self.root/'output').rglob('*') if p.is_file()},{'.jpg','.png','.mp4'})
    def test_raw_filter_profile_and_stale_preview(self):
        self.put('20260907.DNG');rows=scan(self.c);self.assertEqual(rows[0].status,'Prêt')
        self.c.exclude_raw=True;execute(self.c,rows);self.assertEqual(rows[0].status,'Exclu');self.assertFalse((self.root/'output/Trip').exists())
        p=self.root/'profile.json';self.c.save(p);self.assertTrue(Config.load(p).exclude_raw)
        import json
        old=json.loads(p.read_text());old.pop('exclude_raw');p.write_text(json.dumps(old));self.assertTrue(Config.load(p).exclude_raw)
    def test_raw_only_sidecar_excluded_but_jpg_pair_kept(self):
        self.put('20260907.dng');self.put('20260907.xmp');self.c.exclude_raw=True
        self.assertTrue(all(r.status=='Exclu' for r in scan(self.c)))
        self.put('20260907.jpg');rows=scan(self.c)
        self.assertEqual(next(r.status for r in rows if r.source.endswith('.xmp')),'Prêt')
    def test_only_populated_folders_and_both_drones(self):
        self.put('Mini4Pro/20260907.jpg');self.put('Air3/20260907.mp4');self.c.sources[0].device='Auto';self.c.devices['DJI Air 3']=True
        rows=scan(self.c);self.assertEqual(len([r for r in rows if r.status=='Prêt']),2);execute(self.c,rows)
        names={p.name for p in (self.root/'output').rglob('*') if p.is_dir()};self.assertNotIn('06_SELECTION',names);self.assertNotIn('07_PUBLICATION',names);self.assertNotIn('PIXEL8',names)
        self.assertTrue((self.root/'output/Trip/2026-09-07/05_DJI_MINI4PRO/PHOTO').exists());self.assertFalse((self.root/'output/Trip/2026-09-07/05_DJI_MINI4PRO/VIDEO').exists())
    def test_disabled_device(self):
        self.put('20260907.mp4');self.c.sources[0].device='DJI Air 3';rows=scan(self.c);self.assertEqual(rows,[]);execute(self.c,rows);self.assertFalse((self.root/'output').exists())
    def test_x5_raw_never_read(self):
        self.put('20260907.insv');self.put('20260907.insp');self.c.sources[0].device='Insta360 X5'
        with patch('engine.metadata') as reader:
            rows=scan(self.c);reader.assert_not_called()
        self.assertTrue(all(r.status=='Exclu' for r in rows))
    def test_x5_export_without_confirmation(self):
        self.put('20260907.mp4');self.c.sources[0].device='Insta360 X5';self.assertFalse(self.c.sources[0].exports_confirmed)
        rows=scan(self.c);self.assertEqual(rows[0].status,'Prêt');self.assertIn('03_INSTA360_X5/VIDEO',Path(rows[0].target).as_posix())
    def test_video_only_cameras(self):
        self.put('20260907.jpg');self.put('20260907.mp4')
        for camera in ['Insta360 Ace Pro 2']:
            self.c.devices[camera]=True;self.c.sources[0]=Source(str(self.src),camera,exports_confirmed=True)
            rows=scan(self.c);self.assertEqual([r.status for r in rows],['Exclu','Prêt']);self.assertNotIn('PHOTO',tree_text(self.c,rows))
    def test_pixel8_does_not_become_pixel11(self):
        self.put('Pixel8/20260907.jpg');self.c.sources[0].device='Auto';self.assertEqual(scan(self.c)[0].status,'À vérifier')
    def test_video_only_camera_rejects_sidecars(self):
        self.put('20260907.mp4');self.put('20260907.srt');self.c.devices['Insta360 Ace Pro 2']=True;self.c.sources[0]=Source(str(self.src),'Insta360 Ace Pro 2',exports_confirmed=True)
        rows=scan(self.c);self.assertEqual([r.status for r in rows],['Prêt','Exclu'])
    def test_whatsapp_limits(self):
        for name in ['a.jpg','b.png','c.mp4','d.mov','caption.txt']:self.put(name)
        self.c.sources[0]=Source(str(self.src),'WhatsApp','2026-09-07');rows=scan(self.c);self.assertEqual(sum(r.status=='Prêt' for r in rows),2);self.assertEqual(sum(r.status=='Conflit' for r in rows),2);execute(self.c,rows)
        folder=self.root/'output/Trip/2026-09-07/07_PUBLICATION/WHATSAPP';self.assertEqual({p.name for p in folder.iterdir()},{'photo.jpg','video.mp4'})
        self.assertEqual(sum(r.status=='Doublon' for r in scan(self.c)),2)
    def test_facebook_mirror(self):
        self.put('final.jpg');self.c.sources[0]=Source(str(self.src),'Facebook','2026-09-07');self.assertIn('INSTAGRAM_FACEBOOK',scan(self.c)[0].target)
        self.c.mirror_facebook=False;self.assertIn('PUBLICATION/FACEBOOK',Path(scan(self.c)[0].target).as_posix())
        self.c.mirror_facebook=True;self.c.social['Instagram']=False;self.assertNotIn('INSTAGRAM_FACEBOOK',scan(self.c)[0].target)
    def test_selection_only_if_enabled(self):
        self.put('final.jpg');self.c.sources[0]=Source(str(self.src),'Sélection','2026-09-07');self.assertIn('06_SELECTION',scan(self.c)[0].target);self.c.selection=False;self.assertEqual(scan(self.c),[])
    def test_orphan_sidecar_excluded(self):
        self.put('20260907.srt');self.assertEqual(scan(self.c)[0].status,'Exclu')
    def test_journal_requires_common_date(self):
        self.c.sources[0].device='Geo-Log';self.assertRaises(ValueError,scan,self.c)

if __name__=='__main__':unittest.main(verbosity=2)
