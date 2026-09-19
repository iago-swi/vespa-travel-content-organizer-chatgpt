"""Exercise the real day-entry dialog, including date boundaries and persistence."""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QTableWidget,QTableWidgetItem,QPushButton,QDialogButtonBox

def verify_day_dates(window):
    saved=(window.start.text(),window.day_labels.copy(),window.rows,window.error)
    failures=[];messages=[];result=[]
    window.start.setText('2026-09-07');window.day_labels={};window.rows=[];window.error=lambda e:messages.append(str(e))
    def exercise():
        dialog=QApplication.activeModalWidget()
        try:
            table=dialog.findChild(QTableWidget)
            add=next(b for b in dialog.findChildren(QPushButton) if b.text()=='+ Ajouter une journée')
            add.click();assert table.item(0,0).text()=='2026-09-07'
            add.click();assert table.item(1,0).text()=='2026-09-08';assert table.currentColumn()==1
            for first,expected in [('2024-02-28','2024-02-29'),('2024-02-29','2024-03-01'),('2026-12-31','2027-01-01')]:
                table.setRowCount(1);table.setItem(0,0,QTableWidgetItem(first));add.click();assert table.item(1,0).text()==expected
            table.setRowCount(1);table.setItem(0,0,QTableWidgetItem('2026-09'));add.click();assert table.rowCount()==1 and messages
            table.setRowCount(0);add.click();add.click()
            table.setItem(0,1,QTableWidgetItem('Départ'))
            table.setCurrentCell(0,0)
            dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click()
            assert window.day_labels=={'2026-09-07':'Départ','2026-09-08':''},window.day_labels
            result.append(True)
        except Exception as e:failures.append(e);dialog.reject()
    try:
        QTimer.singleShot(100,exercise);window.days()
        if failures:raise failures[0]
        assert result==[True]
        return {'next_date':True,'trip_start':True,'leap_year':True,'year_change':True,'incomplete_date':True,'unnamed_dates_saved':True}
    finally:
        start,labels,rows,error=saved;window.start.setText(start);window.day_labels=labels;window.rows=rows;window.error=error
