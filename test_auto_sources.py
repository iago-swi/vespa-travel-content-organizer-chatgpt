import unittest,tempfile
from pathlib import Path
from auto_sources import identify_folder,discover,validate_choices
from engine import Config,Source,scan

class AutoSourcesTests(unittest.TestCase):
    def test_broad_names_for_all_sources(self):
        names={
            'Insta360 X5':['Insta X5','Insta360_X5','X5'],
            'Insta360 Ace Pro 2':['AcePro2','Insta_Ace_Pro_2','Insta360 Ace 2','Ace 2'],
            'DJI Mini 4 Pro':['DJI Mini4Pro','Mini4','M4P','DJI_M4_Pro'],
            'DJI Neo 2':['DJI_Neo2','Neo_2'],
            'DJI Air 3':['DJI_Air3','Air_3'],
            'Pixel 11':['pixel','Google Pixel','Pixel_11','Pixel11Pro','P11','Google_P11_Pro'],
            'Garmin':['Garmin','Instinct_3','Garmin Instinct 3 Solar','Instinct3Solar'],
            'Geo-Log':['GeoLog','Géo_Log','Geo Log'],
        }
        for expected,variants in names.items():
            for variant in variants:
                for name in [variant,variant.upper(),variant.lower(),'03_'+variant,'20260911 - '+variant,'Photos - '+variant+' - exports',variant+' (vidéos recadrées)']:
                    with self.subTest(name=name):self.assertEqual(identify_folder(name),expected)
    def test_no_fuzzy_model_confusion(self):
        for name in ['Pixel8','Google Pixel 8 Pro','Pixel 10','Pixel 11 Pro XL','Air 3S','Air 30','Mini 3 Pro','Mini 4K','Neo','Neo 20','Ace Pro','Ace Pro 3','X50','Insta360','DJI','Garmin X5','Mini4Pro X5','WhatsApp','LosslessCut','Insta360 Studio','GPS','20260911']:
            with self.subTest(name=name):self.assertEqual(identify_folder(name),'')
    def test_folder_names(self):
        for name,device in [('X5','Insta360 X5'),('Ace Pro 2','Insta360 Ace Pro 2'),('Mini 4 Pro','DJI Mini 4 Pro'),('Neo 2','DJI Neo 2'),('Pixel','Pixel 11'),('Garmin','Garmin'),('Geo-Log','Geo-Log'),('03_INSTA360_X5','Insta360 X5'),('DJI AIR 3','DJI Air 3')]:self.assertEqual(identify_folder(name),device)
        for name in ['Pixel 8 Pro','WhatsApp','Sélection','Instagram','Facebook','Unknown','Mini 4 Pro X5']:self.assertEqual(identify_folder(name),'')
    def test_import_separates_devices_and_preserves_dates(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);incoming=root/'input';incoming.mkdir()
            for name in ['X5','Neo 2','Pixel']:
                p=incoming/name;p.mkdir();(p/'20260911.jpg').write_bytes(b'photo');(p/'20260912.mp4').write_bytes(b'video')
            (incoming/'loose.txt').write_text('root')
            folders,loose=discover(incoming);self.assertEqual(loose,1)
            c=Config(str(root/'out'),'Trip',exiftool_enabled=False)
            c.sources=validate_choices([Source(path,device) for path,device in folders],c,[])
            rows=scan(c);self.assertEqual(len(rows),6);self.assertTrue(all(r.status=='Prêt' for r in rows))
            self.assertEqual({r.device for r in rows},{'Insta360 X5','DJI Neo 2','Pixel 11'})
            self.assertEqual({r.date for r in rows},{'2026-09-11','2026-09-12'})
            self.assertTrue(all('/PHOTO/'+Path(r.source).name in Path(r.target).as_posix() or '/VIDEO/'+Path(r.source).name in Path(r.target).as_posix() for r in rows))
            self.assertFalse((root/'out').exists())
    def test_dates_disabled_and_overlap(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/'Geo-Log';p.mkdir();c=Config()
            with self.assertRaises(ValueError):validate_choices([Source(str(p),'Geo-Log')],c,[])
            s=Source(str(p),'Geo-Log','2026-09-11');self.assertEqual(validate_choices([s],c,[]),[s])
            with self.assertRaises(ValueError):validate_choices([s],c,[Source(str(root),'Pixel 11')])
            c.software['Geo-Log']=False
            with self.assertRaises(ValueError):validate_choices([s],c,[])
