"""Regression: checked indicators must survive parentheses in installation paths."""
from pathlib import Path
import shutil
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest


def verify_checkboxes(application, window, folder, dialog_class, style, asset):
    root = Path(folder) / 'Téléchargements (1)'
    root.mkdir(parents=True, exist_ok=True)
    # Internal Qt resources are independent of installation folder names.
    from PySide6.QtCore import QFile
    assert QFile.exists(asset)
    application.setStyleSheet(style)
    dialog = dialog_class(window)
    dialog.setAttribute(Qt.WA_DontShowOnScreen)
    dialog.show()
    dialog.pages.setCurrentIndex(1)
    application.processEvents()

    def purple_pixels(box):
        im = box.grab().toImage()
        count = 0
        for y in range(im.height()):
            for x in range(min(im.width(), int(20 * im.devicePixelRatio()))):
                c = im.pixelColor(x, y)
                count += abs(c.red()-186)<5 and abs(c.green()-138)<5 and abs(c.blue()-255)<5
        return count

    try:
        tested = 0
        for checks in dialog.checks.values():
            for name, box in checks.items():
                if not box.isEnabled():
                    continue
                before = box.isChecked()
                for x in (7, 40):
                    QTest.mouseClick(box, Qt.LeftButton, pos=QPoint(x, box.height()//2))
                    application.processEvents()
                    assert box.isChecked() != before if x == 7 else box.isChecked() == before, name
                box.setFocus()
                QTest.keyClick(box, Qt.Key_Space)
                assert box.isChecked() != before, name
                QTest.keyClick(box, Qt.Key_Space)
                tested += 1
        box = dialog.checks['devices']['DJI Air 3']
        box.setChecked(False)
        application.processEvents()
        off = purple_pixels(box)
        QTest.mouseClick(box, Qt.LeftButton, pos=QPoint(7, box.height()//2))
        application.processEvents()
        on = purple_pixels(box)
        assert on > off + 30, (on, off)
        return {'controls': tested, 'mouse': True, 'keyboard': True, 'checked_pixels': on, 'unchecked_pixels': off, 'path': 'accents, spaces, parentheses'}
    finally:
        dialog.close()
        application.setStyleSheet(style)
