import unittest
from unittest.mock import patch
from engine import Config,structure_text

class StructureTests(unittest.TestCase):
    def test_without_sources_or_disk(self):
        c=Config();c.devices['Insta360 Ace Pro 2']=True
        with patch('pathlib.Path.resolve',side_effect=AssertionError('disk access')):
            text=structure_text(c)
        for name in ['<journée>/','02_PIXEL11/','03_INSTA360_X5/','INSTA360_ACEPRO2/','WHATSAPP/','INSTAGRAM_FACEBOOK/','GEOLOG/']:self.assertIn(name,text)
        self.assertNotIn('PIXEL8',text)
        self.assertNotIn('Studio',text);self.assertNotIn('LosslessCut',text)
        self.assertRegex(text,r'INSTA360_ACEPRO2/\n[^\n]*VIDEO/')
    def test_disabled_sources_and_channels(self):
        c=Config(devices={},software={},social={})
        for group in [c.devices,c.software,c.social]:
            for key in group:group[key]=False
        c.selection=False
        self.assertEqual(structure_text(c),'Voyage_Vespa/')
        c.social['Instagram']=True;self.assertIn('INSTAGRAM/',structure_text(c));self.assertNotIn('FACEBOOK',structure_text(c))
        c.social['Facebook']=True;self.assertIn('INSTAGRAM_FACEBOOK/',structure_text(c))
        c.mirror_facebook=False;self.assertNotIn('INSTAGRAM_FACEBOOK',structure_text(c))
    def test_named_days(self):
        c=Config(trip='Trip',day_labels={'2026-09-11':'Col','2026-09-12':'Retour'},start='2026-09-12')
        text=structure_text(c);self.assertIn('2026-09-12_Retour/',text);self.assertNotIn('2026-09-11',text)
