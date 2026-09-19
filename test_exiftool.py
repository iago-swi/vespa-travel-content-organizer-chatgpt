import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import Config,Source,scan,metadata,exiftool_metadata,Cancelled
import exiftool_support as et

class ExifToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name).resolve();self.src=self.base/'été photos';self.src.mkdir();self.p=self.src/'PXL_20260908_120000.heic';self.p.write_bytes(b'fixture');self.c=Config(str(self.base/'dest'),'Test',[Source(str(self.src))])
    def tearDown(self):self.tmp.cleanup()
    def test_missing_manual_path_does_not_silently_use_other_tool(self):
        with patch.object(et.shutil,'which',return_value=sys.executable):self.assertEqual(et.find_exiftool(str(self.base/'missing.exe')),'')
    def test_manual_path_with_spaces(self):
        exe=self.base/'outils été/exiftool.exe';exe.parent.mkdir();exe.touch();self.assertEqual(et.find_exiftool(str(exe)),str(exe.resolve()))
    def test_auto_near_application_and_path(self):
        with patch.object(et.sys,'frozen',True,create=True),patch.object(et.sys,'executable',str(self.base/'app.exe')):
            exe=self.base/'tools/exiftool.exe';exe.parent.mkdir();exe.touch();self.assertEqual(et.find_exiftool(),str(exe))
            exe.unlink()
            with patch.object(et.shutil,'which',return_value='C:/Tools/exiftool.exe'):self.assertEqual(et.find_exiftool(),'C:/Tools/exiftool.exe')
    def test_profiles_old_and_new(self):
        p=self.base/'profil.json';self.c.exiftool_path='C:/Outils été/exiftool.exe';self.c.exiftool_enabled=False;self.c.save(p);self.assertEqual(Config.load(p),self.c)
        data=json.loads(p.read_text());data.pop('exiftool_path');data.pop('exiftool_enabled');p.write_text(json.dumps(data));old=Config.load(p);self.assertEqual(old.exiftool_path,'');self.assertTrue(old.exiftool_enabled)
    def test_probe_rejects_keep_open_and_invalid(self):
        self.assertRaises(ValueError,et.probe,'exiftool(-k).exe')
        with patch.object(et,'run',return_value=(0,'hello','')):self.assertRaises(ValueError,et.probe,'exiftool.exe')
        with patch.object(et,'run',return_value=(0,'13.59\n','')):self.assertEqual(et.probe('exiftool.exe'),'13.59')
    def test_readonly_utf8_batch(self):
        data=[{'SourceFile':str(self.p),'ExifIFD:Model':'Pixel 11'}]
        with patch.object(et,'run',return_value=(0,json.dumps(data),'')) as call:
            result=et.read_batch('ExifTool.exe',[self.p]);args=call.call_args.args;self.assertEqual(args[1][:2],['-config','']);self.assertIn(str(self.p),args[2].decode('utf-8'));self.assertIn(str(self.p.resolve()).casefold(),result);self.assertNotIn('-overwrite_original',args[1]);self.assertEqual(args[1][-2:],['-@','-'])
    def test_metadata_priority_model_offset(self):
        data={'ExifIFD:DateTimeOriginal':'2026:09:07 23:30:00','ExifIFD:OffsetTimeOriginal':'+02:00','IFD0:Model':'Pixel 11'}
        dt,origin,model,issues=metadata(self.p,data);self.assertEqual(dt.isoformat(),'2026-09-07T23:30:00+02:00');self.assertIn('ExifTool',origin);self.assertIn('Pixel 11',model)
    def test_quicktime_utc(self):
        dt,*_=exiftool_metadata({'QuickTime:CreateDate':'2026:09:07 23:30:00'});self.assertEqual(dt.utcoffset().total_seconds(),0)
    def test_no_filesystem_date_used(self):
        dt,*_=exiftool_metadata({'System:FileModifyDate':'2026:09:07 23:30:00'});self.assertIsNone(dt)
    def test_scan_external_classifies_and_converts(self):
        data={str(self.p.resolve()).casefold():{'SourceFile':str(self.p),'QuickTime:CreateDate':'2026:09:07 23:30:00','IFD0:Model':'DJI Mini 4 Pro'}}
        with patch('engine.find_exiftool',return_value='tool'),patch('engine.probe',return_value='13.59'),patch('engine.read_batch',return_value=data):
            r=scan(self.c)[0];self.assertEqual((r.date,r.device,r.status),('2026-09-08','DJI Mini 4 Pro','Prêt'));self.assertIn('ExifTool',r.date_origin)
    def test_failure_falls_back_with_log(self):
        self.c.sources[0].device='Pixel 11';events=[]
        with patch('engine.find_exiftool',return_value='tool'),patch('engine.probe',return_value='13.59'),patch('engine.read_batch',side_effect=ValueError('bad output')):
            r=scan(self.c,lambda k,v:events.append(str(v)))[0];self.assertEqual(r.status,'Prêt');self.assertEqual(r.date_origin,'Nom du fichier');self.assertTrue(any('bad output' in v for v in events))
    def test_disabled_never_launches(self):
        self.c.exiftool_enabled=False
        with patch('engine.probe') as probe:scan(self.c);probe.assert_not_called()
    def test_subprocess_timeout_and_cancellation(self):
        with self.assertRaises(TimeoutError):et.run(sys.executable,['-c','import time;time.sleep(20)'],timeout=.2)
        start=time.monotonic()
        def check():
            if time.monotonic()-start>.2:raise Cancelled()
        with self.assertRaises(Cancelled):et.run(sys.executable,['-c','import time;time.sleep(20)'],check=check)
        self.assertLess(time.monotonic()-start,5)

if __name__=='__main__':unittest.main(verbosity=2)
