import json,tempfile,unittest
from pathlib import Path
from engine import Config,Source,scan,execute
class MediaOptionsTests(unittest.TestCase):
    def test_x5_photo_video_and_originals(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'in';src.mkdir()
            for ext in ['JPG','PNG','mp4','insv','insp']:(src/('20260907.'+ext)).write_bytes(ext.encode())
            c=Config(str(root/'out'),'Trip',[Source(str(src),'Insta360 X5','2026-09-07')],exiftool_enabled=False,exclude_raw=False,exclude_srt_lrv=False)
            rows=scan(c);execute(c,rows)
            for r in rows:
                ext=Path(r.source).suffix.lower()
                self.assertEqual(r.status,'Exclu' if ext in {'.insv','.insp'} else 'Copié')
                if r.status=='Copié':self.assertIn('/PHOTO/' if ext!='.mp4' else '/VIDEO/',Path(r.target).as_posix())
            self.assertEqual(len(list(src.iterdir())),5)
    def test_extras_toggle_and_copy_guard(self):
        for device in ['Insta360 X5','DJI Mini 4 Pro']:
            with tempfile.TemporaryDirectory() as td:
                root=Path(td);src=root/'in';src.mkdir()
                for ext in ['MP4','SrT','LRV']:(src/('clip.'+ext)).write_bytes(ext.encode())
                c=Config(str(root/'out'),'Trip',[Source(str(src),device,'2026-09-07')],exiftool_enabled=False,exclude_raw=False,exclude_srt_lrv=False)
                rows=scan(c);self.assertTrue(all(r.status=='Prêt' for r in rows))
                execute(c,rows);self.assertTrue(all(r.status=='Copié' for r in rows))
                c.trip='Filtered';rows=scan(c);c.exclude_srt_lrv=True;execute(c,rows)
                self.assertEqual([p.suffix for p in (root/'out/Filtered').rglob('*') if p.is_file()],['.MP4'])
                rows=scan(c)
                for r in rows:
                    if Path(r.source).suffix.lower() in {'.srt','.lrv'}:self.assertEqual(r.status,'Exclu')
                self.assertEqual(len(list(src.iterdir())),3)
    def test_profile_compatibility(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'p.json';c=Config(exclude_srt_lrv=True);c.save(p);self.assertTrue(Config.load(p).exclude_srt_lrv)
            c.exclude_srt_lrv=False;c.save(p);self.assertFalse(Config.load(p).exclude_srt_lrv)
            old=json.loads(p.read_text());old.pop('exclude_srt_lrv');p.write_text(json.dumps(old));self.assertTrue(Config.load(p).exclude_srt_lrv)
