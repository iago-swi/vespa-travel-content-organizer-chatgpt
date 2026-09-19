from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QTableWidget

def verify_ui(application, window, dialog_class, source_class):
    import copy
    saved=copy.deepcopy(window.roadtrip)
    sources=window.sources[:];raw_setting=window.exclude_raw.isChecked()
    window.exclude_raw.setChecked(True);assert window.config().exclude_raw
    window.exclude_raw.setChecked(False);assert not window.config().exclude_raw
    try:
        dialog=dialog_class(window)
        for key in ['DJI Mini 4 Pro','DJI Air 3','DJI Neo 2','Insta360 X5','Insta360 Ace Pro 2','Pixel 11']:
            dialog.checks['devices'][key].setChecked(False)
        for key in ['LosslessCut','Insta360 Studio']:
            box=dialog.checks['software'][key]
            assert not box.isChecked() and not box.isEnabled()
        for key in ['DJI Mini 4 Pro','DJI Air 3','DJI Neo 2','Insta360 X5','Insta360 Ace Pro 2','Pixel 11']:
            dialog.checks['devices'][key].setChecked(True)
            assert dialog.checks['software']['LosslessCut'].isChecked()
            dialog.checks['devices'][key].setChecked(False)
            assert not dialog.checks['software']['LosslessCut'].isChecked()
        dialog.checks['devices']['Pixel 11'].setChecked(True)
        dialog.checks['devices']['Insta360 X5'].setChecked(True)
        assert dialog.checks['software']['Insta360 Studio'].isChecked()
        assert '06_SELECTION' in dialog.selection.toolTip()
        window.roadtrip=dialog.value();dialog.close()
        source=source_class(window)
        choices=[source.device.itemText(i) for i in range(source.device.count())]
        assert choices==['Insta360 X5','Pixel 11','Garmin','Geo-Log'],choices
        assert not source.findChildren(QCheckBox)
        source.close()
        window.roadtrip.software['Geo-Log']=False
        source=source_class(window);choices=[source.device.itemText(i) for i in range(source.device.count())]
        assert 'Geo-Log' not in choices
        source.close();window.roadtrip.software['Geo-Log']=True
        workflow=source_class(window,workflow=True)
        choices=[workflow.device.itemText(i) for i in range(workflow.device.count())]
        assert 'WhatsApp' in choices and 'Geo-Log' not in choices
        assert 'Insta360 X5' not in choices
        workflow.close()
        from engine import Source
        window.sources=[Source('inactive','DJI Air 3'),Source('active','Pixel 11'),Source('final','WhatsApp')]
        window.refresh_sources()
        assert window.source_table.rowCount()==1
        assert window.source_table.item(0,0).text()=='Pixel 11'
        window.roadtrip.devices['DJI Air 3']=True;window.refresh_sources()
        assert window.source_table.rowCount()==2
        assert len(window.sources)==3 # retained settings, no deletion of files or entries
        checked=[]
        def inspect_days():
            d=QApplication.activeModalWidget()
            table=d.findChild(QTableWidget)
            text=table.horizontalHeaderItem(0).text()
            checked.append(table.columnWidth(0)>=table.fontMetrics().horizontalAdvance(text)+10)
            d.reject()
        QTimer.singleShot(100,inspect_days)
        window.days()
        assert checked==[True],checked
        previous=window.mascot.animated
        QTest.keyClick(window.mascot,Qt.Key_Space)
        assert window.mascot.animated!=previous
        QTest.keyClick(window.mascot,Qt.Key_Space)
        assert window.mascot.animated==previous
        return {'dependent_editors':True,'device_filter':True,'workflow_separate':True,'no_x5_checkbox':True,'day_header':True,'animation_pause':True}
    finally:
        window.exclude_raw.setChecked(raw_setting);window.roadtrip=saved;window.sources=sources;window.refresh_sources()
