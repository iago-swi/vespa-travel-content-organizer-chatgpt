import copy,tempfile,unittest
from pathlib import Path
from engine import Config,Source,scan,preview_rows,tree_text,execute

class TreePreviewTests(unittest.TestCase):
    def test_period_expansion_days_x5_and_no_empty_folder(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'in';src.mkdir()
            for filename in ['20260914.jpg','20260915.mp4']:(src/filename).write_bytes(b'media')
            before=Config(str(root/'out'),'Old',[Source(str(src),'Insta360 X5')],start='2026-09-15',exiftool_enabled=False)
            rows=scan(before);self.assertEqual({r.status for r in rows},{'Prêt','Hors période'})
            after=copy.deepcopy(before);after.trip='New';after.start='2026-09-14';after.day_labels={'2026-09-14':'Col'}
            text=tree_text(after,preview_rows(before,after,rows))
            self.assertIn('2026-09-14_Col',text);self.assertIn('PHOTO',text);self.assertIn('VIDEO',text)
            after.devices['Insta360 X5']=False;self.assertEqual(preview_rows(before,after,rows),[])
            self.assertFalse((root/'out').exists())
    def test_disabled_missing_source_is_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            c=Config(td,'Trip',[Source(str(Path(td)/'unplugged'),'DJI Air 3')],exiftool_enabled=False)
            self.assertEqual(scan(c),[])
