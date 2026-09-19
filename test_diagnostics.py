import os,sys,threading,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import diagnostics as d

class DiagnosticsTests(unittest.TestCase):
    def test_rotation_errors_and_export(self):
        old=sys.excepthook;old_thread=threading.excepthook
        handlers=d.logger.handlers[:]
        with tempfile.TemporaryDirectory() as td,patch.dict(os.environ,{'VESPA_SETTINGS_DIR':td}):
            try:
                directory=d.setup();self.assertEqual(directory,Path(td)/'logs')
                handler=next(h for h in d.logger.handlers if hasattr(h,'maxBytes'));handler.maxBytes=350
                for n in range(50):d.logger.debug('event %d %s',n,'x'*50)
                try:raise ValueError('sample bug')
                except ValueError:d.logger.exception('Test failure')
                target=d.export_bundle(Path(td)/'diagnostic.zip')
                self.assertLessEqual(len(list(directory.glob('diagnostic.log*'))),4)
                with zipfile.ZipFile(target) as z:
                    self.assertIn('version.txt',z.namelist())
                    text=''.join(z.read(name).decode('utf-8') for name in z.namelist())
                    self.assertIn('sample bug',text);self.assertIn('Traceback',text)
                    self.assertTrue(all(name=='version.txt' or name.startswith('diagnostic.log') for name in z.namelist()))
            finally:
                for handler in d.logger.handlers[:]:
                    if handler not in handlers:handler.close();d.logger.removeHandler(handler)
                d._directory=None;sys.excepthook=old;threading.excepthook=old_thread
