import json
import tempfile
import unittest
from pathlib import Path
from engine import Config, Source, SOFTWARE_DEFAULTS, SOCIAL_DEFAULTS

class ProfileCleanupTests(unittest.TestCase):
    def test_old_categories_and_sources_removed_on_load_and_save(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'profile.json'
            c=Config(sources=[Source('media','Pixel 11')])
            c.save(path)
            data=json.loads(path.read_text('utf-8'))
            data['software']['Retired journal']=True
            data['social']['Retired network']=True
            data['sources'].append({'path':'old-export','device':'Retired journal'})
            path.write_text(json.dumps(data),'utf-8')
            loaded=Config.load(path)
            self.assertEqual([s.device for s in loaded.sources],['Pixel 11'])
            self.assertEqual(set(loaded.software),set(SOFTWARE_DEFAULTS))
            self.assertEqual(set(loaded.social),set(SOCIAL_DEFAULTS))
            loaded.save(path)
            self.assertNotIn('Retired',path.read_text('utf-8'))

    def test_preferences_clean_all_presets_and_defaults(self):
        from app import clean_preferences
        data={'defaults':{'software':{'Geo-Log':False,'Retired journal':True}},
              'presets':{'Weekend':{'social':{'Instagram':False,'Retired network':True}}},
              'exiftool_path':'C:/Tools/exiftool.exe'}
        cleaned=clean_preferences(data)
        self.assertFalse(cleaned['defaults']['software']['Geo-Log'])
        self.assertFalse(cleaned['presets']['Weekend']['social']['Instagram'])
        self.assertNotIn('Retired',json.dumps(cleaned))
        self.assertEqual(cleaned['exiftool_path'],'C:/Tools/exiftool.exe')
