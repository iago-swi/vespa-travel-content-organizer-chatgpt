from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QComboBox,QDialogButtonBox,QMessageBox,QHeaderView
from auto_sources import discover,validate_choices
from engine import Source,DEVICE_DEFAULTS,enabled

class AutoSourceDialog(QDialog):
    def __init__(self,parent,root):
        super().__init__(parent);self.setWindowTitle('Auto — reconnaître les sous-dossiers');self.resize(900,480)
        self.config=parent.config();self.existing=parent.sources;self.result_sources=[]
        layout=QVBoxLayout(self)
        hint=QLabel('Reconnaissance par nom de sous-dossier. Vérifiez les affectations avant ajout.\nLes dates des médias restent automatiques ; Geo-Log nécessite une journée de classement.');hint.setWordWrap(True);layout.addWidget(hint)
        self.folders,loose=discover(root)
        note=QLabel(f'{root}\n{len(self.folders)} sous-dossier(s). {loose} fichier(s) directement à la racine non inclus.');note.setWordWrap(True);layout.addWidget(note)
        self.table=QTableWidget(len(self.folders),4);self.table.setHorizontalHeaderLabels(['Importer / dossier','Source','Journée (facultatif)','Reconnaissance'])
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        for col in [1,2,3]:self.table.horizontalHeader().setSectionResizeMode(col,QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        choices=[d for d in DEVICE_DEFAULTS if d!='Pixel 8 Pro' and enabled(self.config,d)]+(['Geo-Log'] if enabled(self.config,'Geo-Log') else [])
        for n,(path,device) in enumerate(self.folders):
            active=bool(device and enabled(self.config,device))
            item=QTableWidgetItem(Path(path).name);item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if active else Qt.Unchecked);item.setToolTip(path);self.table.setItem(n,0,item)
            combo=QComboBox();combo.addItem('Choisir…','');[combo.addItem(d,d) for d in choices]
            if active:combo.setCurrentIndex(combo.findData(device))
            self.table.setCellWidget(n,1,combo);self.table.setItem(n,2,QTableWidgetItem(''))
            status=QTableWidgetItem('Reconnu' if active else 'Désactivé : '+device if device else 'À identifier ou ignorer');status.setFlags(Qt.ItemIsEnabled);self.table.setItem(n,3,status)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.button(QDialogButtonBox.Ok).setText('Ajouter les sources');buttons.accepted.connect(self.confirm);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def values(self):
        return validate_choices([Source(path,self.table.cellWidget(n,1).currentData(),self.table.item(n,2).text().strip()) for n,(path,_) in enumerate(self.folders) if self.table.item(n,0).checkState()==Qt.Checked],self.config,self.existing)
    def confirm(self):
        try:self.result_sources=self.values();self.accept()
        except ValueError as e:QMessageBox.warning(self,'Vérifier les sources',str(e))
