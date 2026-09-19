"""Bounded local diagnostics; no media contents or preferences are exported."""
import logging
from logging.handlers import RotatingFileHandler
import os,platform,sys,threading,zipfile
from pathlib import Path
from app_info import APP_NAME,VERSION,BUILD_DATE

logger=logging.getLogger('vespa')
logger.addHandler(logging.NullHandler())
_directory=None

def setup():
    global _directory
    if _directory is not None:return _directory
    root=Path(os.environ.get('VESPA_SETTINGS_DIR') or str(Path(os.environ.get('APPDATA',str(Path.home())))/APP_NAME))
    directory=root/'logs'
    try:
        directory.mkdir(parents=True,exist_ok=True)
        handler=RotatingFileHandler(directory/'diagnostic.log',maxBytes=2*1024*1024,backupCount=3,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(threadName)s] %(message)s'))
        logger.addHandler(handler);logger.setLevel(logging.DEBUG);logger.propagate=False
        _directory=directory
    except OSError:
        return None
    old_hook=sys.excepthook
    def exception_hook(kind,value,tb):
        logger.critical('Unhandled exception',exc_info=(kind,value,tb));old_hook(kind,value,tb)
    sys.excepthook=exception_hook
    old_thread_hook=threading.excepthook
    def thread_hook(args):
        logger.critical('Unhandled thread exception',exc_info=(args.exc_type,args.exc_value,args.exc_traceback));old_thread_hook(args)
    threading.excepthook=thread_hook
    logger.info('START %s version=%s build=%s Python=%s platform=%s',APP_NAME,VERSION,BUILD_DATE,platform.python_version(),platform.platform())
    return directory

def export_bundle(destination):
    directory=setup()
    if directory is None:raise OSError('Le dossier de diagnostic est inaccessible.')
    logger.info('Diagnostic export requested')
    for handler in logger.handlers:handler.flush()
    target=Path(destination).resolve()
    if target.parent==directory.resolve():raise ValueError('Enregistrez le diagnostic en dehors du dossier des journaux.')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr('version.txt',f'{APP_NAME}\nVersion: {VERSION}\nBuild: {BUILD_DATE}\nPython: {platform.python_version()}\nOS: {platform.platform()}\n')
        for path in sorted(directory.glob('diagnostic.log*')):
            if path.is_file():bundle.write(path,path.name)
    return target
