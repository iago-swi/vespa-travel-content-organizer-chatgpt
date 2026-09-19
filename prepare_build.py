"""Generate Windows metadata and stamp the build date before packaging."""
from pathlib import Path
from datetime import datetime
import os
import runpy

root = Path(__file__).resolve().parent
metadata = root / 'app_info.py'
info = runpy.run_path(str(metadata))
epoch = os.environ.get('SOURCE_DATE_EPOCH')
from datetime import timezone
build_date = (datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now().astimezone()).date().isoformat()
name, version = info['APP_NAME'], info['VERSION']
metadata.write_text(f'"""Central release metadata. Build date is stamped by Vespa.spec."""\nAPP_NAME = {name!r}\nVERSION = {version!r}\nBUILD_DATE = {build_date!r}\n', encoding='utf-8')
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct
parts = tuple(map(int, version.split('.'))) + (0,)
strings = dict(CompanyName=name, FileDescription=name, FileVersion=version, InternalName=name, OriginalFilename=name+'.exe', ProductName=name, ProductVersion=version, Comments='Build '+build_date)
resource = VSVersionInfo(ffi=FixedFileInfo(filevers=parts,prodvers=parts), kids=[StringFileInfo([StringTable('040C04B0',[StringStruct(k,v) for k,v in strings.items()])]),VarFileInfo([VarStruct('Translation',[1036,1200])])])
(root/'version_info.txt').write_text(str(resource),encoding='utf-8')
