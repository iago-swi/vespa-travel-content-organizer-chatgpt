import os
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['VESPA_SETTINGS_DIR']=str(Path('work/test-settings').resolve())
Path('work').mkdir(exist_ok=True)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from app import *
from PySide6.QtGui import QFontDatabase

app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE);app.setPalette(dark_palette())
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
QFontDatabase.addApplicationFont('C:/Windows/Fonts/seguisb.ttf')
app.setFont(QFont('Segoe UI',9))
w=Window()
actions=w.help_menu.actions()
assert [a.text() for a in actions]==['Mode d’emploi','','Exporter le diagnostic…','À propos']
seen=[]
def check():
    dlg=app.activeModalWidget()
    assert isinstance(dlg,AboutDialog)
    text='\n'.join(x.text() for x in dlg.findChildren(QLabel))
    for expected in [APP_NAME,VERSION,'Build du','PySide6','Pillow','ExifTool','tzdata','PyInstaller','Vibe-codé avec ChatGPT']:
        assert expected in text,expected
    dlg.grab().save('work/about-preview.png')
    seen.append(True)
    QTest.keyClick(dlg,Qt.Key_Escape)
QTimer.singleShot(50,check)
actions[-1].trigger()
assert seen
w.close()
print('About menu, modal content and Escape verified')

