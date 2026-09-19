from __future__ import annotations
import json
import os
import copy
import sys
import threading
import time
import resources_rc
from mascot import VespaRide
from app_info import APP_NAME, VERSION, BUILD_DATE
from diagnostics import logger as diagnostic_log, setup as setup_diagnostics, export_bundle
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QUrl
from PySide6.QtGui import QIcon, QColor, QDesktopServices, QFont, QPainter, QPalette
from PySide6.QtWidgets import (QMenu,QScrollArea,QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QLineEdit,QPushButton,QFileDialog,QComboBox,QCheckBox,QTableWidget,QTableWidgetItem,QTableView,QHeaderView,QSplitter,QTabWidget,QPlainTextEdit,QProgressBar,QMessageBox,QSizePolicy,QDialog,QDialogButtonBox,QDoubleSpinBox,QInputDialog)
from engine import Config,Source,Row,DEVICES,scan,execute,validate,export_csv,report_path,Cancelled
from exiftool_support import find_exiftool, probe
from engine import CAMERAS, DEVICE_DEFAULTS, SOFTWARE_DEFAULTS, SOCIAL_DEFAULTS, enabled, tree_text, safe_name

INPUT_SOURCES=[d for d in DEVICE_DEFAULTS if d!='Pixel 8 Pro']+['Geo-Log']

STYLE="""
QWidget { font-family: "Segoe UI"; font-size: 13px; color: #eeeaf2; }
QMainWindow, QDialog { background: #202020; }
QLabel { background: transparent; }
QLabel#brand { font-size: 16px; font-weight: 600; }
QLabel#heading { font-size: 12px; font-weight: 600; color: #e4dce9; }
QLabel#hint, QLabel#subtitle { color: #b7b0be; }
QLabel#metricValue { font-size: 20px; font-weight: 600; color: #cba5ff; }
QLabel#metricReady { font-size: 20px; font-weight: 600; color: #f4cf4d; }
QWidget#setup { background: #282729; border-radius: 8px; }
QWidget#stats { background: #2d2833; border-radius: 6px; }
QLineEdit, QComboBox, QDoubleSpinBox { background: #222123; border: 1px solid #4b4352; border-radius: 4px; padding: 5px 7px; min-height: 19px; selection-background-color: #543976; }
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border-color: #ba8aff; }
QLineEdit:disabled { color: #a69caa; }
QComboBox QAbstractItemView { background: #282729; selection-background-color: #503565; color: #eeeaf2; }
QPushButton { background: #302d33; border: 1px solid #4b4352; border-radius: 4px; padding: 6px 10px; min-height: 18px; }
QPushButton:hover { background: #3a3244; border-color: #ab7cd6; }
QPushButton:focus { border-color: #ccaaff; }
QPushButton#primary { background: #f4cf4d; color: #2d2510; border-color: #f4cf4d; font-weight: 600; }
QPushButton#primary:hover { background: #ffe080; }
QPushButton:disabled, QPushButton#primary:disabled { color: #a299a8; background: #302d33; border-color: #45404a; }
QTableView, QPlainTextEdit { background: #252426; alternate-background-color: #2a282d; border: 1px solid #403a45; selection-background-color: #4c365f; selection-color: #f8f4fc; gridline-color: #39353d; }
QHeaderView::section { background: #312c37; border: none; border-bottom: 1px solid #4f415b; padding: 5px 6px; color: #ded3e7; font-weight: 600; }
QTableCornerButton::section { background: #312c37; border: none; }
QTabWidget::pane { border: none; }
QTabBar::tab { padding: 8px 12px; background: transparent; border-bottom: 2px solid transparent; color: #bbb1c4; }
QTabBar::tab:selected { border-bottom-color: #ba8aff; color: #e8d5ff; }
QTabBar::tab:hover { background: #302d33; }
QProgressBar { background: #403a45; border: none; min-height: 3px; max-height: 3px; }
QProgressBar::chunk { background: #f4cf4d; }
QSplitter::handle { background: #202020; width: 10px; }
QCheckBox { spacing: 8px; padding: 4px 0; }
QCheckBox::indicator { width: 15px; height: 15px; border: 1px solid #807087; border-radius: 3px; background: #252426; }
QCheckBox::indicator:checked { background: #ba8aff; border-color: #ba8aff; image: url("CHECK_ASSET"); }
QCheckBox::indicator:checked:disabled { background: #8666a6; border-color: #8666a6; }
QCheckBox:disabled { color: #b8a8c8; }
QPushButton#accent { background: #3d2e4d; color: #e0c4ff; border-color: #9164b8; }
QPushButton#accent:hover { background: #4c3661; }
QPlainTextEdit { padding: 9px; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QMenu { background: #282729; border: 1px solid #4b4352; padding: 4px; }
QMenu::item { padding: 7px 20px; }
QMenu::item:selected { background: #4c365f; }
QToolTip { color: #2d2510; background: #f4cf4d; border: 1px solid #d8b63c; border-radius: 7px; padding: 0px 3px; margin: 0px; font-size: 12px; min-height: 0px; }
QScrollBar:vertical { background: #252426; width: 9px; margin: 0; }
QScrollBar:horizontal { background: #252426; height: 9px; margin: 0; }
QScrollBar::handle { background: #65566f; border-radius: 4px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
"""

STYLE=STYLE.replace("CHECK_ASSET",":/vespa/check.svg")

def dark_palette():
    palette=QPalette()
    for role,color in [(QPalette.Window,'#202020'),(QPalette.WindowText,'#eeeaf2'),(QPalette.Base,'#222123'),(QPalette.AlternateBase,'#2a282d'),(QPalette.Text,'#eeeaf2'),(QPalette.Button,'#302d33'),(QPalette.ButtonText,'#eeeaf2'),(QPalette.Highlight,'#4c365f'),(QPalette.HighlightedText,'#f8f4fc'),(QPalette.ToolTipBase,'#f4cf4d'),(QPalette.ToolTipText,'#2d2510'),(QPalette.PlaceholderText,'#a49aa9')]:
        palette.setColor(role,QColor(color))
    return palette

class CompactLabel(QLabel):
    """Keep status messages on one line; full text remains available in a tooltip."""
    def __init__(self,text='',name='hint'):
        super().__init__(text);self.setObjectName(name);self.setMinimumWidth(0);self.setFixedHeight(22);self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed);self.setToolTip(text)
    def setText(self,text):super().setText(text);self.setToolTip(text)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setPen(self.palette().color(QPalette.WindowText));painter.setFont(self.font())
        painter.drawText(self.contentsRect(),Qt.AlignLeft|Qt.AlignVCenter,self.fontMetrics().elidedText(self.text(),Qt.ElideRight,self.contentsRect().width()))


def label(text, name=None, wrap=False):
    x=QLabel(text)
    if name:x.setObjectName(name)
    x.setWordWrap(wrap)
    return x

BUTTON_TIPS = {
    'Paramètres du voyage': 'Choisir les appareils, logiciels, réseaux, dates et profils du voyage.',
    'Charger un profil': 'Restaurer un voyage enregistré : dossiers, appareils, dates et réglages.',
    'Enregistrer': 'Enregistrer le voyage complet dans un fichier de profil JSON.',
    '+ Ajouter': 'Choisir un dossier à importer, sans déplacer ni modifier ses fichiers.',
    'Modifier': 'Modifier le dossier sélectionné, son affectation ou sa date.',
    'Retirer': 'Retirer cette entrée de la liste ; aucun fichier du disque n’est supprimé.',
    'Nommer les journées…': 'Donner un nom facultatif à chaque date dans les dossiers du voyage.',
    '1. Analyser / aperçu': 'Lire les fichiers et afficher leur classement prévu, sans créer de dossiers ni copier.',
    '2. Copier': 'Copier uniquement les fichiers prêts après l’aperçu ; les originaux restent intacts.',
    'Gérer les fichiers…': 'Ajouter la sélection et les médias finaux des réseaux activés.',
    'Exporter CSV': 'Enregistrer le détail des fichiers, dates, destinations, états et erreurs.',
    'Arrêter': 'Arrêter après le fichier en cours ; les copies terminées sont conservées.',
    'Ouvrir le voyage': 'Afficher le dossier du voyage dans l’Explorateur Windows.',
    'ExifTool…': 'Sélectionner exiftool.exe ; le chemin choisi sera mémorisé.',
    'Auto': 'Rechercher automatiquement ExifTool près du programme et dans le PATH.',
    'Retester': 'Vérifier l’exécutable ExifTool et afficher sa version ou son erreur.',
    'Enregistrer comme valeurs par défaut': 'Réutiliser ces réglages au prochain lancement de l’application.',
    'Charger le preset': 'Remplacer les réglages du roadtrip par le preset sélectionné.',
    'Enregistrer le preset…': 'Nommer et conserver cet ensemble de réglages pour un autre voyage.',
    'Appliquer': 'Valider les paramètres et actualiser l’aperçu des fichiers déjà ajoutés.',
    'Détails du fichier…': 'Voir les chemins complets, l’origine de la date et la raison d’un blocage.',
    '+ Ajouter une journée': 'Ajouter le lendemain de la dernière date. Première ligne : début du roadtrip, ou aujourd’hui si non renseigné.'
}

def button(text, callback, primary=False):
    x=QPushButton(text); x.clicked.connect(callback);x.setToolTip(BUTTON_TIPS.get(text,text))
    if primary:x.setObjectName('primary')
    return x

def size_text(n):
    if n<1024:return f'{n} o'
    if n<1024**2:return f'{n/1024:.1f} Ko'
    return f'{n/1024**3:.2f} Go' if n>=1024**3 else f'{n/1024**2:.1f} Mo'

class FileModel(QAbstractTableModel):
    columns=[('Fichier','source'),('Appareil','device'),('Type','kind'),('Journée','date'),('État','status'),('Taille','size'),('Date issue de','date_origin'),('Destination','target'),('Détail','detail')]
    def __init__(self):super().__init__();self.rows=[]
    def set_rows(self, rows):self.beginResetModel();self.rows=rows;self.endResetModel()
    def rowCount(self,parent=QModelIndex()):return 0 if parent.isValid() else len(self.rows)
    def columnCount(self,parent=QModelIndex()):return len(self.columns)
    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role==Qt.DisplayRole and orientation==Qt.Horizontal:return self.columns[section][0]
    def data(self,index,role=Qt.DisplayRole):
        if not index.isValid():return None
        r=self.rows[index.row()];key=self.columns[index.column()][1];v=getattr(r,key)
        if role==Qt.DisplayRole:
            if key=='source':return Path(v).name
            return size_text(v) if key=='size' else v
        if role==Qt.ToolTipRole:return r.source+'\n'+r.target+'\n'+r.detail
        if role==Qt.ForegroundRole and key=='status':
            return QColor('#f4cf4d' if r.status in {'Erreur','Conflit','À vérifier'} else '#d3b2ff' if r.status in {'Copié','Prêt'} else '#b7b0be')
        if role==Qt.UserRole:return v

class Filter(QSortFilterProxyModel):
    def __init__(self):super().__init__();self.query='';self.state='Tous les états';self.setSortRole(Qt.UserRole)
    def filterAcceptsRow(self,n,parent):
        r=self.sourceModel().rows[n]
        return (self.state=='Tous les états' or r.status==self.state) and self.query.casefold() in ' '.join(str(v) for v in asdict(r).values()).casefold()

class Worker(QThread):
    event=Signal(str,object)
    result=Signal(object,bool,str)
    def __init__(self,c,rows=None):
        super().__init__();self.c=c;self.rows=rows;self.stop=threading.Event();self.last=0;self.logs=[]
    def emit_event(self,k,v):
        if k=='log':
            diagnostic_log.debug('Import: %s',v)
            self.logs.append(v)
            if len(self.logs)>=50:self.event.emit('logs',self.logs);self.logs=[]
        elif k=='exiftool':self.event.emit(k,v)
        elif time.monotonic()-self.last>.08:
            self.event.emit(k,v);self.last=time.monotonic()
    def run(self):
        message='';cancel=False;rows=self.rows or []
        try:
            rows=scan(self.c,self.emit_event,self.stop) if self.rows is None else execute(self.c,self.rows,self.emit_event,self.stop)
        except Cancelled:cancel=True;message='Traitement arrêté. Les copies déjà terminées sont conservées.'
        except Exception as e:diagnostic_log.exception('Worker failure');message=str(e)
        finally:
            if self.logs:self.event.emit('logs',self.logs)
            self.result.emit(rows,cancel,message)

class SourceDialog(QDialog):
    def __init__(self,parent,source=None,workflow=False):
        super().__init__(parent);self.setWindowTitle('Ajouter des fichiers au workflow' if workflow else 'Configurer une source');self.resize(620,260)
        box=QVBoxLayout(self);form=QFormLayout();self.path=QLineEdit();line=QHBoxLayout();line.addWidget(self.path);line.addWidget(button('Parcourir…',self.browse));form.addRow('Dossier source',line)
        self.device=QComboBox();c=parent.config();choices=[d for d in DEVICES if d not in INPUT_SOURCES and d!='Auto'] if workflow else INPUT_SOURCES;self.device.addItems([d for d in choices if enabled(c,d)]);form.addRow('Destination du workflow' if workflow else 'Source',self.device)
        self.date=QLineEdit();self.date.setPlaceholderText('Facultatif : AAAA-MM-JJ');form.addRow('Imposer une journée',self.date)
        self.offset=QDoubleSpinBox();self.offset.setRange(-48,48);self.offset.setDecimals(2);self.offset.setSuffix(' h');form.addRow('Corriger l’horloge',self.offset)
        box.addLayout(form)
        if workflow:box.addWidget(label('Choisissez les fichiers préparés et leur journée. Aucun envoi vers les réseaux.','hint',True))
        self.path.setToolTip('Dossier contenant les fichiers à copier. Les fichiers source restent intacts.')
        self.device.setToolTip('Appareils et journaux activés dans le roadtrip. Geo-Log fournit ses exports ; les logiciels d’édition ne sont pas des sources.')
        self.date.setToolTip('Facultatif pour les appareils : impose une date de capture à tout ce dossier. Obligatoire pour les journaux, sélections et publications.')
        self.offset.setToolTip('Décalage ajouté à la date de capture pour corriger une horloge. Sans effet si une journée est imposée.')
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.accepted.connect(self.confirm);buttons.rejected.connect(self.reject);box.addWidget(buttons)
        if source:self.path.setText(source.path);self.device.setCurrentText(source.device);self.date.setText(source.date);self.offset.setValue(float(source.offset_hours))
    def browse(self):
        p=QFileDialog.getExistingDirectory(self,'Dossier source',self.path.text())
        if p:self.path.setText(p)
    def confirm(self):
        try:
            if not self.device.currentText():raise ValueError('Activez un appareil ou une destination dans les paramètres du roadtrip.')
            if not Path(self.path.text()).is_dir():raise ValueError('Choisissez un dossier existant.')
            if self.date.text():
                from datetime import datetime
                datetime.strptime(self.date.text(),'%Y-%m-%d')
            self.accept()
        except Exception as e:QMessageBox.warning(self,'Vérifier la source',str(e))
    def value(self):return Source(self.path.text(),self.device.currentText(),self.date.text(),self.offset.value())

def preferences_path():
    return Path(os.environ.get('VESPA_SETTINGS_DIR') or str(Path(os.environ.get('APPDATA',str(Path.home())))/'Vespa travel content organizer'))/'preferences.json'

def read_preferences():
    try:
        data=json.loads(preferences_path().read_text(encoding='utf-8'))
        return clean_preferences(data)
    except (OSError,ValueError):return {}

def clean_preferences(data):
    for settings in [data.get('defaults', {})] + list(data.get('presets', {}).values()):
        for group, defaults in [('devices', DEVICE_DEFAULTS), ('software', SOFTWARE_DEFAULTS), ('social', SOCIAL_DEFAULTS)]:
            if group in settings:
                settings[group] = {key: bool(settings[group].get(key, default)) for key, default in defaults.items()}
    return data

def write_preferences(data):
    data=clean_preferences(data)
    p=preferences_path();p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(p)

class RoadtripDialog(QDialog):
    def __init__(self,parent):
        super().__init__(parent);self.setWindowTitle('Paramètres du voyage');self.setMinimumSize(900,480)
        area=QApplication.primaryScreen().availableGeometry();self.resize(min(1340,area.width()-40),min(700,area.height()-70))
        self.c=copy.deepcopy(parent.config());self.rows=parent.rows;self.prefs=read_preferences()
        box=QVBoxLayout(self);box.setContentsMargins(16,12,16,12);box.setSpacing(12)
        self.splitter=QSplitter(Qt.Horizontal);box.addWidget(self.splitter,1)
        self.pages=QTabWidget();self.splitter.addWidget(self.pages)
        trip_page=QWidget();tripbox=QVBoxLayout(trip_page);tripbox.setContentsMargins(12,18,12,12);tripbox.setSpacing(16)
        tripbox.addWidget(label('Prépare ton prochain départ','brand'))
        tripbox.addWidget(label('Identité du voyage et profils réutilisables.','hint'))
        form=QFormLayout();form.setSpacing(12)
        self.name=QLineEdit(self.c.trip);self.start=QLineEdit(self.c.start);self.end=QLineEdit(self.c.end);self.region=QLineEdit(self.c.region)
        form.addRow('Nom du roadtrip',self.name);dates=QHBoxLayout();self.start.setPlaceholderText('AAAA-MM-JJ');self.end.setPlaceholderText('AAAA-MM-JJ');dates.addWidget(self.start);dates.addWidget(self.end);form.addRow('Début / fin',dates);form.addRow('Pays / région',self.region);tripbox.addLayout(form)
        presets=QHBoxLayout();self.presets=QComboBox();self.presets.addItems(sorted(self.prefs.get('presets',{})));presets.addWidget(self.presets,1);presets.addWidget(button('Charger le preset',self.load_preset));presets.addWidget(button('Enregistrer le preset…',self.save_preset));tripbox.addWidget(label('Profils enregistrés','heading'));tripbox.addLayout(presets);tripbox.addStretch();self.pages.addTab(trip_page,'Voyage et profils')
        equipment=QWidget();eqbox=QVBoxLayout(equipment);eqbox.setContentsMargins(10,16,10,12);eqbox.setSpacing(14)
        columns=QHBoxLayout();self.checks={}
        labels={'Pixel 11':'Pixel 11 Pro','Pixel 8 Pro':'Pixel 8 Pro · navigation','Garmin':'Garmin Instinct 3 Solar','Insta360 X5':'Insta360 X5 · exports photo / vidéo','Insta360 Ace Pro 2':'Ace Pro 2 · vidéo'}
        for title,group,defaults in [('Appareils','devices',DEVICE_DEFAULTS),('Logiciels','software',SOFTWARE_DEFAULTS),('Réseaux sociaux','social',SOCIAL_DEFAULTS)]:
            col=QVBoxLayout();col.addWidget(label(title,'heading'));self.checks[group]={}
            for key in defaults:
                text=labels.get(key,key)
                cb=QCheckBox(text);cb.setToolTip({'Pixel 8 Pro':'Navigation et tracking, aucun dossier PIXEL8.','Insta360 X5':'Photos issues de frames et vidéos recadrées, déjà exportées depuis Insta360 Studio ; jamais .insv.','Insta360 Ace Pro 2':'Vidéo uniquement, aucun dossier PHOTO.'}.get(key,text));cb.setChecked(getattr(self.c,group).get(key,False));self.checks[group][key]=cb;col.addWidget(cb);cb.toggled.connect(self.update_preview)
            if group=='social':
                col.addSpacing(12);col.addWidget(label('Classement des publications','heading'))
                self.mirror=QCheckBox('Dossier commun Instagram / Facebook');self.mirror.setChecked(self.c.mirror_facebook);col.addWidget(self.mirror)
            col.addStretch();columns.addLayout(col)
        eqbox.addLayout(columns)
        eqbox.addWidget(label('Les logiciels d’édition sont informatifs. Aucun dossier sans contenu.','hint',True));eqbox.addStretch();equipment_scroll=QScrollArea();equipment_scroll.setWidgetResizable(True);equipment_scroll.setWidget(equipment);self.pages.addTab(equipment_scroll,'Équipement et réseaux')
        self.mirror.toggled.connect(self.update_preview)
        previewpage=QWidget();previewbox=QVBoxLayout(previewpage);previewbox.setContentsMargins(10,16,10,10)
        previewbox.addWidget(label('Sélection des médias','heading'))
        self.selection=QCheckBox('Conserver une copie des médias sélectionnés');self.selection.setChecked(self.c.selection);previewbox.addWidget(self.selection)
        previewbox.addWidget(label('Option facultative : conserve les photos et vidéos que vous avez choisies dans 06_SELECTION, pour chaque journée. Vous faites la sélection vous-même ; aucun dossier n’est créé sans fichiers.','hint',True))
        previewbox.addWidget(label('Pour l’utiliser : Workflow > Gérer les fichiers… > Sélection, puis ajouter le dossier de vos choix et leur journée. Décochez cette option si vous ne souhaitez pas cette copie supplémentaire.','hint',True))
        self.selection.toggled.connect(self.update_preview)
        previewbox.addStretch();self.pages.addTab(previewpage,'Sélection')
        daypage=QWidget();daybox=QVBoxLayout(daypage)
        daybox.addWidget(label('Dates et noms facultatifs des journées. Les dossiers apparaissent seulement avec du contenu.','hint',True))
        self.day_table=QTableWidget(0,2);self.day_table.setHorizontalHeaderLabels(['Date (AAAA-MM-JJ)','Nom de la journée'])
        self.day_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents);self.day_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for date in sorted(set(self.c.day_labels)|{r.date for r in self.rows if r.date}):
            n=self.day_table.rowCount();self.day_table.insertRow(n);self.day_table.setItem(n,0,QTableWidgetItem(date));self.day_table.setItem(n,1,QTableWidgetItem(self.c.day_labels.get(date,'')))
        daybox.addWidget(self.day_table);daybox.addWidget(button('+ Ajouter une journée',self.add_day));self.pages.addTab(daypage,'Journées')
        panel=QWidget();panelbox=QVBoxLayout(panel);panelbox.setContentsMargins(8,0,0,0)
        heading=QHBoxLayout();heading.addWidget(label('Arborescence du voyage','brand'));heading.addStretch()
        self.copy_tree=button('Copier',self.copy_preview);heading.addWidget(self.copy_tree);panelbox.addLayout(heading)
        self.preview_context=label('','hint',True);panelbox.addWidget(self.preview_context)
        self.tree=QPlainTextEdit();self.tree.setReadOnly(True);self.tree.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.tree.setStyleSheet('QPlainTextEdit { font-family: Consolas; font-size: 13px; }');self.tree.setMinimumWidth(360);panelbox.addWidget(self.tree,1)
        panelbox.addWidget(label('Structure prévue selon les cases cochées, sans analyse ni fichiers individuels. PHOTO/VIDEO indiquent les possibilités ; seuls les dossiers contenant des fichiers seront créés lors de la copie.','hint',True))
        self.splitter.addWidget(panel);self.splitter.setChildrenCollapsible(False);self.splitter.setSizes([720,560])
        for field in [self.name,self.start,self.end,self.region]:field.textChanged.connect(self.update_preview)
        self.day_table.itemChanged.connect(self.update_preview)
        actions=QHBoxLayout();actions.addWidget(button('Enregistrer comme valeurs par défaut',self.save_defaults));actions.addStretch();actions.addWidget(button('Annuler',self.reject));actions.addWidget(button('Appliquer',self.confirm,True));box.addLayout(actions)
        self.update_preview()
        self.selection.setToolTip('Archive vos meilleures photos et vidéos dans 06_SELECTION, séparées par type. Ajoutez vos choix via Workflow > Gérer les fichiers… ; aucun dossier n’est créé sans fichiers.')
        self.mirror.setToolTip('Quand Instagram et Facebook sont activés, leurs médias finaux sont réunis dans INSTAGRAM_FACEBOOK au lieu de deux dossiers.')
        self.checks['software']['Insta360 Studio'].setToolTip('Automatique et en lecture seule : coché exactement lorsque la X5 est activée. Prépare les exports X5 ; aucun dossier de logiciel.')
        self.checks['software']['LosslessCut'].setToolTip('Automatique et en lecture seule : coché si au moins un appareil vidéo est activé (Pixel 11, X5, Ace Pro 2 ou drone). Aucun dossier de logiciel.')
        self.name.setToolTip('Nom du dossier principal du voyage.')
        self.start.setToolTip('Premier jour à importer, au format AAAA-MM-JJ ; laissez vide pour ne pas limiter.')
        self.end.setToolTip('Dernier jour à importer, inclus, au format AAAA-MM-JJ.')
        self.region.setToolTip('Pays ou région du voyage, conservé dans le profil.')
        self.presets.setToolTip('Réutilisez un ensemble de paramètres enregistré pour un court ou un long roadtrip.')
    def value(self):
        c=copy.deepcopy(self.c);c.trip=self.name.text().strip();c.start=self.start.text().strip();c.end=self.end.text().strip();c.region=self.region.text().strip()
        for group,checks in self.checks.items():setattr(c,group,{k:cb.isChecked() for k,cb in checks.items()})
        c.mirror_facebook=self.mirror.isChecked();c.selection=self.selection.isChecked()
        c.day_labels={self.day_table.item(n,0).text().strip():self.day_table.item(n,1).text().strip() if self.day_table.item(n,1) else '' for n in range(self.day_table.rowCount()) if self.day_table.item(n,0) and self.day_table.item(n,0).text().strip()}
        c.normalize();return c
    def update_preview(self,*args):
        if not hasattr(self,'tree'):return
        from datetime import datetime
        video=any(self.checks['devices'][d].isChecked() for d in CAMERAS)
        x5=self.checks['devices']['Insta360 X5'].isChecked()
        for key,forced in [('LosslessCut',video),('Insta360 Studio',x5)]:
            cb=self.checks['software'][key];cb.blockSignals(True)
            cb.setChecked(forced);cb.setEnabled(False);cb.blockSignals(False)
        self.mirror.setEnabled(self.checks['social']['Instagram'].isChecked() and self.checks['social']['Facebook'].isChecked())
        from engine import structure_text
        c=self.value()
        diagnostic_log.debug('Structure settings: trip=%s period=%s..%s devices=%s software=%s social=%s',c.trip,c.start,c.end,c.devices,c.software,c.social)
        self.preview_context.setText(' · '.join(x for x in [c.region, (c.start or 'Début libre')+' → '+(c.end or 'Fin libre')] if x))
        try:
            safe_name(c.trip)
            for date,name in c.day_labels.items():
                datetime.strptime(date,'%Y-%m-%d')
                if name:safe_name(name)
            for date in [c.start,c.end]:
                if date:datetime.strptime(date,'%Y-%m-%d')
            if c.start and c.end and c.start>c.end:raise ValueError('La fin précède le début du voyage.')
            text=structure_text(c)
            self.copy_tree.setEnabled(True)
        except ValueError as e:
            text='Complétez les paramètres : '+str(e);self.copy_tree.setEnabled(False)
        scroll=self.tree.verticalScrollBar().value();horizontal=self.tree.horizontalScrollBar().value()
        self.tree.setPlainText(text);self.tree.verticalScrollBar().setValue(scroll);self.tree.horizontalScrollBar().setValue(horizontal)
    def copy_preview(self):
        QApplication.clipboard().setText(self.tree.toPlainText())
    def add_day(self):
        from datetime import date,timedelta
        dates=[self.day_table.item(n,0).text() for n in range(self.day_table.rowCount()) if self.day_table.item(n,0)]
        try:proposed=date.fromisoformat(max(dates))+timedelta(days=1) if dates else date.fromisoformat(self.start.text()) if self.start.text() else date.today()
        except ValueError:proposed=date.today()
        n=self.day_table.rowCount();self.day_table.insertRow(n);self.day_table.setItem(n,0,QTableWidgetItem(proposed.isoformat()));self.day_table.setItem(n,1,QTableWidgetItem(''));self.day_table.setCurrentCell(n,1)
    def validate_fields(self):
        from datetime import datetime
        c=self.value();safe_name(c.trip)
        for d in [c.start,c.end]:
            if d:datetime.strptime(d,'%Y-%m-%d')
        if c.start and c.end and c.start>c.end:raise ValueError('La fin précède le début du roadtrip.')
        seen=set()
        for n in range(self.day_table.rowCount()):
            date=self.day_table.item(n,0).text().strip() if self.day_table.item(n,0) else ''
            datetime.strptime(date,'%Y-%m-%d')
            if date in seen:raise ValueError('Journée en double : '+date)
            seen.add(date)
        for name in c.day_labels.values():
            if name:safe_name(name)
        return c
    def settings(self):
        c=self.validate_fields();return {k:asdict(c)[k] for k in ['trip','start','end','region','devices','software','social','mirror_facebook','selection']}
    def apply_settings(self,data):
        for key,widget in [('trip',self.name),('start',self.start),('end',self.end),('region',self.region)]:widget.setText(data.get(key,''))
        for group,checks in self.checks.items():
            for key,cb in checks.items():cb.blockSignals(True);cb.setChecked(data.get(group,{}).get(key,False));cb.blockSignals(False)
        self.mirror.setChecked(data.get('mirror_facebook',True));self.selection.setChecked(data.get('selection',True));self.update_preview()
    def load_preset(self):
        data=self.prefs.get('presets',{}).get(self.presets.currentText())
        if data:self.apply_settings(data)
    def save_preset(self):
        name,ok=QInputDialog.getText(self,'Enregistrer le preset','Nom du profil (ex. Court roadtrip (quelques jours))')
        if not ok or not name.strip():return
        try:
            self.prefs.setdefault('presets',{})[name.strip()]=self.settings();write_preferences(self.prefs);self.presets.clear();self.presets.addItems(sorted(self.prefs['presets']));self.presets.setCurrentText(name.strip())
        except Exception as e:QMessageBox.warning(self,'Preset',str(e))
    def save_defaults(self):
        try:self.prefs['defaults']=self.settings();write_preferences(self.prefs);QMessageBox.information(self,'Valeurs par défaut','Réglages enregistrés pour le prochain démarrage.')
        except Exception as e:QMessageBox.warning(self,'Valeurs par défaut',str(e))
    def confirm(self):
        try:self.validate_fields();self.accept()
        except Exception as e:QMessageBox.warning(self,'Paramètres',str(e))

class AboutDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('À propos')
        self.setWindowIcon(application_icon())
        self.setMinimumWidth(440)
        box=QVBoxLayout(self);box.setContentsMargins(24,24,24,24);box.setSpacing(14)
        heading=QHBoxLayout()
        icon=QLabel();icon.setPixmap(application_icon().pixmap(48,48));heading.addWidget(icon)
        heading.addWidget(label(APP_NAME,'brand',True),1);box.addLayout(heading)
        date_text='.'.join(reversed(BUILD_DATE.split('-')))
        self.details=label(f'Version {VERSION}\nBuild du {date_text}',wrap=True)
        self.details.setTextInteractionFlags(Qt.TextSelectableByMouse)
        box.addWidget(self.details)
        box.addWidget(label('Technologies utilisées','heading'))
        box.addWidget(label('Python · PySide6 / Qt (interface graphique)\n'
                            'Pillow (images et métadonnées EXIF)\n'
                            'tzdata / zoneinfo (fuseaux horaires)\n'
                            'ExifTool (métadonnées, outil externe optionnel)\n'
                            'PyInstaller (packaging Windows)',wrap=True))
        box.addWidget(label('Vibe-codé avec ChatGPT','subtitle'))
        buttons=QDialogButtonBox(QDialogButtonBox.Close)
        buttons.button(QDialogButtonBox.Close).setText('Fermer')
        buttons.rejected.connect(self.reject);box.addWidget(buttons)


class Window(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle(f'{APP_NAME} — {VERSION}');self.setMinimumSize(960,560)
        available=QApplication.primaryScreen().availableGeometry()
        self.resize(min(1180,available.width()-32),min(720,available.height()-64))
        self.roadtrip=Config();self.sources=[];self.day_labels={};self.rows=[];self.preview_config=None;self.worker=None;self.running=False;self.mode='';self.last_report=''
        self.setPalette(dark_palette())
        main=QWidget();self.setCentralWidget(main);outer=QVBoxLayout(main);outer.setContentsMargins(14,10,14,10);outer.setSpacing(8)
        header=QHBoxLayout();header.addWidget(label(APP_NAME,'brand'));self.mascot=VespaRide();header.addWidget(self.mascot,1)
        self.profile_bar=QWidget();profile=QHBoxLayout(self.profile_bar);profile.setContentsMargins(0,0,0,0);profile.setSpacing(6)
        settings_button=button('Paramètres du voyage',self.roadtrip_settings);settings_button.setObjectName('accent');profile.addWidget(settings_button)
        load=button('Charger un profil',self.load);load.setShortcut('Ctrl+O');profile.addWidget(load)
        save=button('Enregistrer',self.save);save.setShortcut('Ctrl+S');profile.addWidget(save);header.addWidget(self.profile_bar);self.help_button=QPushButton('Aide');self.help_menu=QMenu(self.help_button);self.help_menu.addAction('Mode d’emploi',self.help);self.help_menu.addSeparator();self.help_menu.addAction('Exporter le diagnostic…',self.export_diagnostic);self.help_menu.addAction('À propos',self.about);self.help_button.setMenu(self.help_menu);header.addWidget(self.help_button);outer.addLayout(header)
        splitter=QSplitter(Qt.Horizontal);splitter.setChildrenCollapsible(False);outer.addWidget(splitter,1)
        self.setup=QWidget();self.setup.setObjectName('setup');self.setup.setMinimumWidth(290);self.setup.setMaximumWidth(360)
        side=QVBoxLayout(self.setup);side.setContentsMargins(8,4,8,8);side.setSpacing(5)
        self.setup_tabs=QTabWidget();side.addWidget(self.setup_tabs)
        imports=QWidget();left=QVBoxLayout(imports);left.setContentsMargins(4,10,4,0);left.setSpacing(7)
        left.addWidget(label('Destination','heading'));destline=QHBoxLayout();destline.setSpacing(5);self.dest=QLineEdit();self.dest.setPlaceholderText('Dossier des voyages');destline.addWidget(self.dest)
        browse=button('…',self.destination);browse.setFixedWidth(30);browse.setToolTip('Choisir le dossier destination');browse.setAccessibleName('Choisir le dossier destination');destline.addWidget(browse);left.addLayout(destline)
        left.addWidget(label('Nom du voyage','heading'));self.trip=QLineEdit('Voyage_Vespa');left.addWidget(self.trip)
        left.addSpacing(4);left.addWidget(label('Sources à importer','heading'))
        self.source_table=QTableWidget(0,2);self.source_table.setHorizontalHeaderLabels(['Source','Dossier']);self.source_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.source_table.setSelectionBehavior(QTableView.SelectRows);self.source_table.setSelectionMode(QTableView.SingleSelection);self.source_table.setEditTriggers(QTableView.NoEditTriggers);self.source_table.verticalHeader().hide();self.source_table.verticalHeader().setDefaultSectionSize(30);self.source_table.setMinimumHeight(80);self.source_table.setWordWrap(False);self.source_table.setShowGrid(False);self.source_table.doubleClicked.connect(self.edit_source);left.addWidget(self.source_table,1)
        actions=QHBoxLayout();actions.setSpacing(5);actions.addWidget(button('+ Ajouter',self.add_source));actions.addWidget(button('Auto…',self.add_auto_sources));actions.addWidget(button('Modifier',self.edit_source));actions.addWidget(button('Retirer',self.remove_source));left.addLayout(actions)
        left.addWidget(label('Double-clic : appareil, journée et horloge.','hint',True))
        self.days_button=button('Nommer les journées…',self.days);left.addWidget(self.days_button);self.setup_tabs.addTab(imports,'Import')
        settings=QWidget();opts=QVBoxLayout(settings);opts.setContentsMargins(4,10,4,0);opts.setSpacing(8)
        opts.addWidget(label('Période à importer','heading'));dates=QHBoxLayout();dates.setSpacing(5);self.start=QLineEdit();self.start.setPlaceholderText('Du AAAA-MM-JJ');self.end=QLineEdit();self.end.setPlaceholderText('Au AAAA-MM-JJ');dates.addWidget(self.start);dates.addWidget(self.end);opts.addLayout(dates)
        opts.addWidget(label('Fuseau horaire','heading'));self.zone=QComboBox();self.zone.setEditable(True);self.zone.addItems(['Europe/Zurich','Europe/Rome','Europe/Paris','UTC']);opts.addWidget(self.zone)
        self.mtime=QCheckBox('Date du fichier en dernier recours');self.mtime.setToolTip('Utiliser la date de modification si aucune date de capture n’est disponible.');opts.addWidget(self.mtime)
        self.exclude_raw=QCheckBox('Exclure les RAW/DNG de la copie');self.exclude_raw.setToolTip('Ignore les photos RAW (DNG, RAW, CR2/CR3, NEF, ARW et autres formats bruts). Les JPG, PNG et vidéos restent inclus. Les originaux ne sont jamais supprimés. Réglage enregistré dans le profil.');self.exclude_raw.setChecked(self.roadtrip.exclude_raw);opts.addWidget(self.exclude_raw)
        self.exclude_srt_lrv=QCheckBox("Exclure les SRT/LRV de la copie");self.exclude_srt_lrv.setToolTip("Ignore les sous-titres SRT et les aperçus LRV. Les fichiers source restent intacts. Réglage enregistré dans le profil.");self.exclude_srt_lrv.setChecked(self.roadtrip.exclude_srt_lrv);opts.addWidget(self.exclude_srt_lrv)
        self.verify=QCheckBox('Vérifier les copies avec SHA-256');self.verify.setChecked(True);opts.addWidget(self.verify)
        opts.addSpacing(8);opts.addWidget(label('Lecture des métadonnées','heading'))
        self.exiftool_path='';self.use_exiftool=QCheckBox('Utiliser ExifTool si disponible');self.use_exiftool.setChecked(True);opts.addWidget(self.use_exiftool)
        toolrow=QHBoxLayout();toolrow.addWidget(button('ExifTool…',self.choose_exiftool));toolrow.addWidget(button('Auto',self.auto_exiftool));toolrow.addWidget(button('Retester',self.test_exiftool));opts.addLayout(toolrow)
        self.exiftool_location=QLineEdit();self.exiftool_location.setReadOnly(True);self.exiftool_location.setPlaceholderText('Aucun exécutable trouvé');opts.addWidget(self.exiftool_location)
        self.exiftool_status=CompactLabel();opts.addWidget(self.exiftool_status);self.refresh_exiftool();opts.addStretch()
        opts.addWidget(label('Les réglages sont enregistrés dans le profil.','hint',True));scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(settings);self.setup_tabs.addTab(scroll,'Réglages')
        splitter.addWidget(self.setup)
        right=QWidget();content=QVBoxLayout(right);content.setContentsMargins(0,0,0,0);content.setSpacing(6)
        statsbox=QWidget();statsbox.setObjectName('stats');stats=QHBoxLayout(statsbox);stats.setContentsMargins(12,6,12,6);stats.setSpacing(10);self.metrics={}
        for key,title in [('read','lus'),('ready','à copier'),('copied','copiés'),('review','à examiner')]:
            pair=QHBoxLayout();pair.setSpacing(6);num=label('0','metricReady' if key=='ready' else 'metricValue');pair.addWidget(num);pair.addWidget(label(title,'hint'));pair.addStretch();stats.addLayout(pair,1);self.metrics[key]=num
        content.addWidget(statsbox)
        self.info=CompactLabel('Ajoutez vos sources, puis lancez un aperçu.');content.addWidget(self.info)
        self.tabs=QTabWidget();content.addWidget(self.tabs,1)
        workflowpage=QWidget();workflowbox=QVBoxLayout(workflowpage);workflowbox.setContentsMargins(0,6,0,0);self.workflow=QPlainTextEdit();self.workflow.setReadOnly(True);workflowbox.addWidget(self.workflow);self.workflow_button=button('Gérer les fichiers…',self.manage_workflow);workflowbox.addWidget(self.workflow_button);self.tabs.addTab(workflowpage,'Workflow')
        files=QWidget();fl=QVBoxLayout(files);fl.setContentsMargins(0,6,0,0);fl.setSpacing(6);filters=QHBoxLayout();filters.setSpacing(6);self.search=QLineEdit();self.search.setPlaceholderText('Rechercher un fichier, un appareil, une date…');filters.addWidget(self.search);self.state=QComboBox();self.state.addItems(['Tous les états','Prêt','Copié','Doublon','À vérifier','Conflit','Erreur','Hors période','Exclu']);filters.addWidget(self.state);fl.addLayout(filters)
        self.model=FileModel();self.proxy=Filter();self.proxy.setSourceModel(self.model);self.table=QTableView();self.table.setModel(self.proxy);self.table.setSortingEnabled(True);self.table.setAlternatingRowColors(True);self.table.setSelectionBehavior(QTableView.SelectRows);self.table.setSelectionMode(QTableView.SingleSelection);self.table.verticalHeader().hide();self.table.verticalHeader().setDefaultSectionSize(30);self.table.setWordWrap(False);self.table.setShowGrid(False)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        for col,width in [(1,112),(2,62),(3,86),(4,80),(5,68)]:self.table.setColumnWidth(col,width)
        for col in [6,7,8]:self.table.setColumnHidden(col,True)
        self.table.doubleClicked.connect(self.open_row);fl.addWidget(self.table)
        fileactions=QHBoxLayout();fileactions.addWidget(button('Détails du fichier…',self.file_details));fileactions.addStretch();fileactions.addWidget(label('Double-clic : ouvrir le dossier','hint'));fl.addLayout(fileactions);self.tabs.addTab(files,'Fichiers')
        self.summary=QTableWidget(0,8);self.summary.setHorizontalHeaderLabels(['Appareil / type','Lus','Prêts','Copiés','Doublons','À examiner','Exclus','Volume']);self.summary.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch);self.summary.setEditTriggers(QTableView.NoEditTriggers);self.summary.verticalHeader().hide();self.summary.verticalHeader().setDefaultSectionSize(30);self.summary.setAlternatingRowColors(True);self.summary.setWordWrap(False);self.summary.setShowGrid(False);self.tabs.addTab(self.summary,'Synthèse')
        for col,width in [(1,40),(2,44),(3,48),(4,68),(5,84),(6,48),(7,70)]:self.summary.setColumnWidth(col,width)
        logpage=QWidget();ll=QVBoxLayout(logpage);ll.setContentsMargins(0,6,0,0);ll.setSpacing(6);self.log=QPlainTextEdit();self.log.setReadOnly(True);ll.addWidget(self.log);logactions=QHBoxLayout();logactions.addWidget(button('Enregistrer le journal…',self.save_log));logactions.addStretch();ll.addLayout(logactions);self.tabs.addTab(logpage,'Journal')
        splitter.addWidget(right);splitter.setSizes([300,850])
        self.progress=QProgressBar();self.progress.setRange(0,1000);self.progress.setValue(0);self.progress.setTextVisible(False);outer.addWidget(self.progress)
        footer=QHBoxLayout();footer.setSpacing(6);self.export_button=button('Exporter CSV',self.export);self.export_button.setEnabled(False);footer.addWidget(self.export_button);footer.addWidget(button('Ouvrir le voyage',self.open_trip))
        self.progress_text=CompactLabel('Prêt à préparer votre import');footer.addWidget(self.progress_text,1)
        self.cancel=button('Arrêter',self.stop);self.cancel.setEnabled(False);footer.addWidget(self.cancel);self.preview=button('1. Analyser / aperçu',self.analyze);self.preview.setShortcut('Ctrl+Return');self.preview.setObjectName('accent');self.copy=button('2. Copier',self.copy_files,True);self.copy.setEnabled(False);footer.addWidget(self.preview);footer.addWidget(self.copy);outer.addLayout(footer)
        self.search.textChanged.connect(self.filter);self.state.currentTextChanged.connect(self.filter)
        for x in [self.dest,self.trip,self.start,self.end]:x.textChanged.connect(self.invalidate)
        self.zone.currentTextChanged.connect(self.invalidate);self.mtime.toggled.connect(self.invalidate);self.verify.toggled.connect(self.invalidate);self.exclude_raw.toggled.connect(self.invalidate);self.exclude_srt_lrv.toggled.connect(self.invalidate);self.use_exiftool.toggled.connect(self.exiftool_changed)
        prefs=read_preferences()
        self.mascot.setAnimated(self.mascot.animated and prefs.get('animation',True))
        self.mascot.animationChanged.connect(self.save_animation)
        if prefs.get('defaults'):
            for key,value in prefs['defaults'].items():
                if hasattr(self.roadtrip,key):setattr(self.roadtrip,key,value)
            self.trip.setText(self.roadtrip.trip);self.start.setText(self.roadtrip.start);self.end.setText(self.roadtrip.end)
        self.roadtrip.normalize()
        self.exiftool_path=prefs.get('exiftool_path','');self.refresh_exiftool();self.refresh()
        for widget,tip in [(self.dest,'Dossier parent dans lequel sera créé le voyage.'),(self.trip,'Nom du dossier du roadtrip.'),(self.zone,'Fuseau utilisé pour convertir les dates de capture.'),(self.verify,'Comparer les empreintes des fichiers source et copiés pour vérifier leur intégrité.'),(self.use_exiftool,'Lire davantage de métadonnées si ExifTool est disponible.'),(self.search,'Filtrer la liste par nom, appareil, date ou destination.'),(self.state,'Afficher uniquement les fichiers ayant cet état.'),(self.start,'Premier jour inclus, AAAA-MM-JJ ; facultatif.'),(self.end,'Dernier jour inclus, AAAA-MM-JJ ; facultatif.')]:widget.setToolTip(tip)
    def about(self):
        AboutDialog(self).exec()

    def save_animation(self,value):
        prefs=read_preferences();prefs['animation']=value;write_preferences(prefs)
    def roadtrip_settings(self):
        dlg=RoadtripDialog(self)
        if dlg.exec():
            self.roadtrip=dlg.value();self.day_labels=self.roadtrip.day_labels.copy();self.trip.setText(self.roadtrip.trip);self.start.setText(self.roadtrip.start);self.end.setText(self.roadtrip.end);self.refresh_sources();self.refresh()
            if self.sources and self.dest.text():self.analyze()
    def test_exiftool(self):
        try:
            path=find_exiftool(self.exiftool_path)
            if not path:raise ValueError('ExifTool introuvable. Cliquez sur ExifTool… pour choisir exiftool.exe.')
            self.exiftool_location.setText(path);self.exiftool_status.setText('ExifTool '+probe(path)+' - disponible')
        except Exception as e:self.exiftool_status.setText(str(e))
    def file_details(self):
        index=self.table.currentIndex()
        if not index.isValid():self.info.setText('Sélectionnez un fichier pour afficher ses détails.');return
        r=self.rows[self.proxy.mapToSource(index).row()];dlg=QDialog(self);dlg.setWindowTitle(Path(r.source).name);dlg.resize(640,370);box=QVBoxLayout(dlg);form=QFormLayout()
        for title,value in [('Source',r.source),('Destination',r.target),('Appareil / type',r.device+' / '+r.kind),('Journée',r.date),('Date issue de',r.date_origin),('État',r.status),('Taille',size_text(r.size))]:
            field=QLineEdit(value);field.setReadOnly(True);field.setToolTip(value);form.addRow(title,field)
        box.addLayout(form);detail=label(r.detail or 'Aucune remarque.','hint',True);detail.setTextInteractionFlags(Qt.TextSelectableByMouse);box.addWidget(detail);box.addStretch();box.addWidget(button('Fermer',dlg.accept));dlg.exec()
    def refresh_exiftool(self):
        path=find_exiftool(self.exiftool_path)
        self.exiftool_location.setText(self.exiftool_path or path)
        self.exiftool_location.setToolTip(self.exiftool_path or path or 'Recherché près de l’application, dans tools et dans le PATH.')
        text='Désactivé — lecture interne.' if not self.use_exiftool.isChecked() else ('Sélection manuelle — vérification à l’aperçu.' if self.exiftool_path and path else 'Détecté automatiquement — vérification à l’aperçu.' if path else 'Introuvable — lecture interne disponible.')
        self.exiftool_status.setText(text);self.exiftool_status.setToolTip(text)
    def exiftool_changed(self,*args):
        self.refresh_exiftool();self.invalidate()
        try:
            prefs=read_preferences();prefs['exiftool_path']=self.exiftool_path;write_preferences(prefs)
        except OSError as e:self.error(e)
    def choose_exiftool(self):
        path,_=QFileDialog.getOpenFileName(self,'Sélectionner exiftool.exe',self.exiftool_path or self.exiftool_location.text(),'Exécutable ExifTool (*.exe);;Tous les fichiers (*)')
        if path:
            self.exiftool_path=str(Path(path).resolve());self.use_exiftool.setChecked(True);self.exiftool_changed()
    def auto_exiftool(self):self.exiftool_path='';self.use_exiftool.setChecked(True);self.exiftool_changed()
    def config(self):return Config(destination=self.dest.text().strip(),trip=self.trip.text().strip(),sources=self.sources.copy(),start=self.start.text().strip(),end=self.end.text().strip(),timezone=self.zone.currentText(),allow_mtime=self.mtime.isChecked(),verify=self.verify.isChecked(),exclude_raw=self.exclude_raw.isChecked(),exclude_srt_lrv=self.exclude_srt_lrv.isChecked(),day_labels=self.day_labels.copy(),exiftool_path=self.exiftool_path,exiftool_enabled=self.use_exiftool.isChecked(),region=self.roadtrip.region,devices=self.roadtrip.devices.copy(),software=self.roadtrip.software.copy(),social=self.roadtrip.social.copy(),mirror_facebook=self.roadtrip.mirror_facebook,selection=self.roadtrip.selection)
    def invalidate(self,*args):
        self.preview_config=None;self.copy.setEnabled(False)
        if self.rows:self.info.setText('Configuration modifiée : relancez un aperçu avant de copier.')
    def refresh_sources(self):
        self.visible_sources=[i for i,s in enumerate(self.sources) if s.device in INPUT_SOURCES and enabled(self.config(),s.device)]
        self.source_table.setRowCount(len(self.visible_sources))
        for n,i in enumerate(self.visible_sources):
            s=self.sources[i]
            for col,value in enumerate([s.device,s.path]):
                item=QTableWidgetItem(value);item.setToolTip(s.path+'\nDate : '+(s.date or 'automatique')+'\nCorrection : '+str(s.offset_hours)+' h');self.source_table.setItem(n,col,item)
        self.invalidate()
    def add_source(self):
        dlg=SourceDialog(self)
        if dlg.exec():self.sources.append(dlg.value());diagnostic_log.info('Source added: %s',dlg.value());self.refresh_sources()
    def add_auto_sources(self):
        root=QFileDialog.getExistingDirectory(self,'Auto — dossier contenant les sous-dossiers des appareils')
        if not root:return
        try:
            from auto_dialog import AutoSourceDialog
            dlg=AutoSourceDialog(self,root)
            if dlg.exec():self.sources.extend(dlg.result_sources);diagnostic_log.info('Auto sources added: %s',dlg.result_sources);self.refresh_sources();self.info.setText('Sources reconnues ajoutées. Lancez Analyser / aperçu pour contrôler les fichiers.')
        except OSError as e:self.error(e)
    def edit_source(self,*args):
        n=self.source_table.currentRow()
        if n<0:return
        n=self.visible_sources[n]
        dlg=SourceDialog(self,self.sources[n])
        if dlg.exec():self.sources[n]=dlg.value();self.refresh_sources()
    def remove_source(self):
        n=self.source_table.currentRow()
        if n>=0:self.sources.pop(self.visible_sources[n]);self.refresh_sources()
    def manage_workflow(self):
        dlg=QDialog(self);dlg.setWindowTitle('Sélection et publication');dlg.resize(650,360)
        layout=QVBoxLayout(dlg);table=QTableWidget(0,2);table.setHorizontalHeaderLabels(['Destination','Dossier']);table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);table.setSelectionBehavior(QTableView.SelectRows);table.setSelectionMode(QTableView.SingleSelection);table.setEditTriggers(QTableView.NoEditTriggers);layout.addWidget(table)
        indices=[]
        def refresh():
            indices[:]=[i for i,s in enumerate(self.sources) if s.device not in INPUT_SOURCES]
            table.setRowCount(len(indices))
            for row,i in enumerate(indices):
                s=self.sources[i]
                for col,value in enumerate([s.device+(' (désactivé)' if not enabled(self.config(),s.device) else ''),s.path]):table.setItem(row,col,QTableWidgetItem(value))
            self.refresh_sources()
        def add():
            edit=SourceDialog(self,workflow=True)
            if edit.exec():self.sources.append(edit.value());refresh()
        def change():
            row=table.currentRow()
            if row<0:return
            i=indices[row];edit=SourceDialog(self,self.sources[i],workflow=True)
            if edit.exec():self.sources[i]=edit.value();refresh()
        def remove():
            row=table.currentRow()
            if row>=0:self.sources.pop(indices[row]);refresh()
        bar=QHBoxLayout()
        for text,callback in [('+ Ajouter',add),('Modifier',change),('Retirer',remove),('Fermer',dlg.accept)]:bar.addWidget(button(text,callback))
        layout.addLayout(bar);refresh();dlg.exec()
    def destination(self):
        p=QFileDialog.getExistingDirectory(self,'Destination des voyages',self.dest.text())
        if p:self.dest.setText(p)
    def save(self):
        p,_=QFileDialog.getSaveFileName(self,'Enregistrer le profil','profil-vespa.json','Profil JSON (*.json)')
        if p:
            try:self.config().save(p);self.info.setText('Profil enregistré : '+Path(p).name)
            except Exception as e:self.error(e)
    def load(self):
        p,_=QFileDialog.getOpenFileName(self,'Charger un profil','','Profil JSON (*.json)')
        if p:
            try:
                c=Config.load(p);self.roadtrip=c;self.dest.setText(c.destination);self.trip.setText(c.trip);self.sources=c.sources;self.day_labels=c.day_labels;self.start.setText(c.start);self.end.setText(c.end);self.zone.setCurrentText(c.timezone);self.mtime.setChecked(c.allow_mtime);self.verify.setChecked(c.verify);self.exclude_raw.setChecked(c.exclude_raw);self.exclude_srt_lrv.setChecked(c.exclude_srt_lrv);self.exiftool_path=c.exiftool_path;self.use_exiftool.setChecked(c.exiftool_enabled);self.refresh_exiftool();self.refresh_sources();self.refresh();self.info.setText('Profil chargé. Vérifiez les sources puis lancez un aperçu.')
            except Exception as e:self.error(e)
    def days(self):
        dlg=QDialog(self);dlg.setWindowTitle('Nommer les journées');dlg.resize(600,400);box=QVBoxLayout(dlg);box.addWidget(label('Ajoutez un nom facultatif : 2026-09-07 → Jour_de_depart.','hint'))
        table=QTableWidget(0,2);table.setHorizontalHeaderLabels(['Date (AAAA-MM-JJ)','Nom de la journée']);table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents);table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch);table.setToolTip('Première colonne : date AAAA-MM-JJ. Deuxième colonne : nom facultatif ajouté au dossier de cette journée.')
        dates=sorted(set(self.day_labels)|{r.date for r in self.rows if r.date})
        for d in dates:
            n=table.rowCount();table.insertRow(n);table.setItem(n,0,QTableWidgetItem(d));table.setItem(n,1,QTableWidgetItem(self.day_labels.get(d,'')))
        box.addWidget(table)
        def add_day():
            from datetime import datetime, date, timedelta
            try:
                if table.rowCount():
                    item=table.item(table.rowCount()-1,0);text=item.text().strip() if item else ''
                    try:proposed=datetime.strptime(text,'%Y-%m-%d').date()+timedelta(days=1)
                    except ValueError:raise ValueError('Complétez la date de la dernière ligne au format AAAA-MM-JJ avant d’ajouter le lendemain.')
                else:
                    start=self.start.text().strip()
                    proposed=datetime.strptime(start,'%Y-%m-%d').date() if start else date.today()
                existing={table.item(i,0).text().strip() for i in range(table.rowCount()) if table.item(i,0)}
                while proposed.isoformat() in existing:proposed+=timedelta(days=1)
                n=table.rowCount();table.insertRow(n);table.setItem(n,0,QTableWidgetItem(proposed.isoformat()));table.setItem(n,1,QTableWidgetItem(''))
                table.setCurrentCell(n,1);table.scrollToItem(table.item(n,1));table.editItem(table.item(n,1))
            except (ValueError,OverflowError) as e:self.error(e)
        box.addWidget(button('+ Ajouter une journée',add_day))
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.addWidget(buttons);buttons.rejected.connect(dlg.reject)
        def accept():
            try:
                from datetime import datetime
                from engine import safe_name
                result={}
                for n in range(table.rowCount()):
                    d=table.item(n,0).text().strip() if table.item(n,0) else '';v=table.item(n,1).text().strip() if table.item(n,1) else ''
                    if not d and not v:continue
                    datetime.strptime(d,'%Y-%m-%d')
                    if d in result:raise ValueError('Cette date apparaît plusieurs fois : '+d)
                    result[d]=safe_name(v) if v else ''
                self.day_labels=result;self.invalidate();dlg.accept()
            except Exception as e:self.error(e)
        buttons.accepted.connect(accept);dlg.exec()
    def analyze(self):
        try:c=self.config();validate(c)
        except Exception as e:self.error(e);return
        self.rows=[];self.model.set_rows([]);self.refresh();self.preview_config=None;self.log.clear();self.launch(c,None)
    def copy_files(self):
        if not self.preview_config or self.config()!=self.preview_config:self.invalidate();return
        self.launch(self.preview_config,self.rows)
    def launch(self,c,rows):
        diagnostic_log.info('Operation %s: trip=%s destination=%s sources=%s devices=%s software=%s social=%s period=%s..%s', 'scan' if rows is None else 'copy',c.trip,c.destination,c.sources,c.devices,c.software,c.social,c.start,c.end)
        self.mode='scan' if rows is None else 'copy';self.running=True;self.workflow_button.setEnabled(False);self.profile_bar.setEnabled(False);self.setup.setEnabled(False);self.preview.setEnabled(False);self.copy.setEnabled(False);self.export_button.setEnabled(False);self.cancel.setEnabled(True);self.progress.setRange(0,0);self.table.setEnabled(False)
        self.info.setText('Lecture en cours : aucun fichier n’est copié.' if rows is None else 'Copie en cours. Les fichiers déjà terminés restent disponibles.');self.log.appendPlainText('APERÇU' if rows is None else '\nEXÉCUTION RÉELLE')
        self.worker=Worker(c,rows);self.worker.event.connect(self.on_event);self.worker.result.connect(self.done);self.worker.finished.connect(self.thread_finished);self.worker.start()
    def on_event(self,k,v):
        if k=='exiftool':diagnostic_log.debug('%s: %s',k,v)
        if k=='logs':self.log.appendPlainText('\n'.join(v))
        elif k=='exiftool':
            self.exiftool_status.setText(v.split(' : ')[0]+' — actif.' if v.startswith('ExifTool ') and v[9:10].isdigit() else 'Lecture interne / informations dans le journal.')
            self.exiftool_status.setToolTip(v)
        elif k=='progress':
            done,total,text=v;self.progress_text.setText(f'{text}  {int(done)} / {total}')
            if text.startswith('Lecture des dates'):self.metrics['read'].setText(str(int(done)))
            if total and done:self.progress.setRange(0,1000);self.progress.setValue(int(done/total*1000))
    def done(self,rows,cancel,message):
        diagnostic_log.info('Operation finished: cancelled=%s message=%s counts=%s',cancel,message,dict(Counter(r.status for r in rows)))
        self.rows=rows;self.model.set_rows(rows);self.progress.setRange(0,1000);self.progress.setValue(0 if cancel or message else 1000)
        self.preview_config=self.worker.c if self.mode=='scan' and not cancel and not message else None
        self.refresh()
        count=Counter(r.status for r in rows)
        if self.mode=='copy':
            try:
                p=report_path(self.worker.c);export_csv(p,rows);self.last_report=str(p);self.log.appendPlainText('Rapport enregistré : '+str(p))
            except Exception as e:message+=' Rapport automatique non enregistré : '+str(e)
        if message:self.log.appendPlainText(message)
        self.info.setText(message if message else (f'Aperçu terminé : {count["Prêt"]} à copier, {count["Doublon"]} doublons, {count["À vérifier"]+count["Conflit"]+count["Erreur"]} à examiner.' if self.mode=='scan' else f'Import terminé : {count["Copié"]} copiés, {count["Doublon"]} doublons, {count["Erreur"]} erreurs. Rapport CSV enregistré.'))
        self.progress_text.setText('Arrêté' if cancel else 'Terminé avec un problème' if message else 'Aperçu terminé — aucune copie effectuée' if self.mode=='scan' else 'Copie terminée')
        if message and not cancel:QMessageBox.warning(self,'Traitement',message)
    def thread_finished(self):
        self.running=False;self.workflow_button.setEnabled(True);self.profile_bar.setEnabled(True);self.setup.setEnabled(True);self.preview.setEnabled(True);self.cancel.setEnabled(False);self.table.setEnabled(True);self.export_button.setEnabled(bool(self.rows));self.copy.setEnabled(self.preview_config is not None and any(r.status=='Prêt' for r in self.rows))
    def refresh(self):
        c=self.config()
        text=['PIXEL 11 : Google Photos → album du roadtrip → téléchargement → décompression → contrôle des dates, avant tout export Insta360/DJI. USB : plan B.', 'GARMIN / GEO-LOG : exporter le tracking et le journal. Pixel 8 : navigation, aucun dossier propre.']
        if c.software.get('Insta360 Studio'):text.append('INSTA360 STUDIO : recadrer et exporter les vidéos ou les photos issues de frames X5 avant ingestion. Aucun original 360 accepté.')
        if c.software.get('LosslessCut'):text.append('LOSSLESSCUT : raccourcir toute vidéo avant ingestion si nécessaire : Ace Pro 2, Pixel 11, drone ou export plat X5.')
        if c.selection:text.append('SÉLECTION : ajoutez une source « Sélection » contenant uniquement vos choix, avec une journée imposée.')
        channels=[k for k,v in c.social.items() if v]
        if channels:text.append('PUBLICATION : ajoutez vos fichiers finaux comme source '+', '.join(channels)+'. Une journée imposée par source. WhatsApp : une photo + une vidéo au maximum. Aucun envoi automatique.')
        self.workflow.setPlainText('\n\n'.join(text))
        active_rows=[r for r in self.rows if enabled(c,r.device)];counts=Counter(r.status for r in active_rows);self.metrics['read'].setText(str(len(active_rows)));self.metrics['ready'].setText(str(counts['Prêt']));self.metrics['copied'].setText(str(counts['Copié']));self.metrics['review'].setText(str(sum(counts[k] for k in ['À vérifier','Erreur','Conflit'])))
        groups=defaultdict(list)
        for r in active_rows:groups[(r.device,r.kind)].append(r)
        self.summary.setRowCount(len(groups)+bool(groups))
        entries=[(f'{d} / {k}',rs) for (d,k),rs in sorted(groups.items())]
        if entries:entries.append(('Total',active_rows))
        for n,(name,rs) in enumerate(entries):
            c=Counter(r.status for r in rs);vals=[name,len(rs),c['Prêt'],c['Copié'],c['Doublon'],c['À vérifier']+c['Erreur']+c['Conflit'],c['Hors période']+c['Exclu'],size_text(sum(r.size for r in rs))]
            for col,v in enumerate(vals):self.summary.setItem(n,col,QTableWidgetItem(str(v)))
    def filter(self,*args):self.proxy.query=self.search.text();self.proxy.state=self.state.currentText();self.proxy.invalidateFilter()
    def stop(self):
        if self.worker:self.worker.stop.set();self.cancel.setEnabled(False);self.progress_text.setText('Arrêt après nettoyage de la copie en cours…')
    def export(self):
        p,_=QFileDialog.getSaveFileName(self,'Exporter le rapport','ingestion_report.csv','Rapport CSV (*.csv)')
        if p:
            try:export_csv(p,self.rows);self.info.setText('Rapport exporté : '+p)
            except Exception as e:self.error(e)
    def save_log(self):
        p,_=QFileDialog.getSaveFileName(self,'Enregistrer le journal','journal-vespa.txt','Texte (*.txt)')
        if p:
            try:Path(p).write_text(self.log.toPlainText(),encoding='utf-8')
            except Exception as e:self.error(e)
    def open_trip(self):
        p=Path(self.dest.text())/self.trip.text()
        if not self.dest.text() or not p.is_dir():self.error('Le dossier voyage sera créé lors de la copie.');return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.resolve())))
    def open_row(self,index):
        r=self.rows[self.proxy.mapToSource(index).row()];p=Path(r.target).parent if r.target and Path(r.target).parent.is_dir() else Path(r.source).parent
        if p.is_dir():QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.resolve())))
    def error(self,e):
        diagnostic_log.error('UI error: %s',e,exc_info=(type(e),e,e.__traceback__))
        QMessageBox.warning(self,'Vérifier les informations',str(e))
    def export_diagnostic(self):
        path,_=QFileDialog.getSaveFileName(self,'Exporter le diagnostic','Vespa-diagnostic.zip','Diagnostic ZIP (*.zip)')
        if not path:return
        try:
            export_bundle(path);self.info.setText('Diagnostic exporté : '+path)
        except (OSError,ValueError) as e:self.error(e)
    def help(self):
        dlg=QDialog(self);dlg.setWindowTitle('Mode d’emploi');dlg.resize(640,450);box=QVBoxLayout(dlg)
        sections=[]
        for block in HELP.split('\n\n'):
            if '\n' in block:
                title,body=block.split('\n',1);sections.append((title,body))
            elif sections:sections[-1]=(sections[-1][0],sections[-1][1]+'\n\n'+block)
        topics=QComboBox();topics.addItems([title for title,body in sections]);box.addWidget(topics)
        text=label(sections[0][1],wrap=True);text.setTextInteractionFlags(Qt.TextSelectableByMouse);text.setAlignment(Qt.AlignTop);box.addWidget(text,1)
        topics.currentIndexChanged.connect(lambda n:text.setText(sections[n][1]));box.addWidget(button('Fermer',dlg.accept));dlg.exec()
    def closeEvent(self,event):
        if self.running:
            event.ignore();self.stop();self.info.setText('Arrêt demandé. Fermez la fenêtre une fois le traitement arrêté.')
        else:event.accept()

HELP="""1. Configurer le roadtrip
Ouvrez Paramètres du voyage. Choisissez les appareils et réseaux utiles au voyage. Enregistrez des presets ou des valeurs par défaut. Tout appareil vidéo active LosslessCut ; la X5 active Insta360 Studio. Ces deux logiciels sont en lecture seule et se décochent quand les appareils correspondants sont désactivés. Ils ne créent aucun dossier.

2. Préparer les sources
Pixel 11 : créez un album Google Photos avec les médias réellement pris au Pixel 11, puis téléchargez et décompressez l’album avant les exports Insta360/DJI. Vérifiez les dates. USB est uniquement un plan B sans Internet ou sans synchronisation. Une source par appareil. Les noms génériques DJI ou Insta360 ne suffisent pas à déterminer le modèle.

Cochez « Exclure les SRT/LRV de la copie » dans Réglages pour ignorer ces annexes. Décochez pour conserver les annexes associées à un média accepté.

3. X5 et Ace Pro 2
X5 : uniquement des exports plats déjà traités dans Insta360 Studio. Les originaux 360 sont refusés. Les photos exportées depuis une frame vont dans PHOTO, les vidéos recadrées dans VIDEO, uniquement selon le contenu présent. Aucun dossier ORIGINAL. Ace Pro 2 : VIDEO uniquement. Un MP4 sans métadonnées fiables nécessite votre contrôle ; l’application ne recadre pas les vidéos.

4. Analyser puis copier
L’aperçu ne crée aucun dossier. Consultez l’arborescence intégrée aux Paramètres du voyage, puis Fichiers et Synthèse. Corrigez les fichiers À vérifier. Copier traite uniquement les fichiers Prêt, sans effacer les sources ni écraser les conflits. Les empreintes SHA-256 sont vérifiées par défaut. Les doublons sont recherchés à la destination prévue ; un fichier renommé peut être copié à nouveau.

5. Dates et journaux
Priorité : journée imposée, métadonnées, nom du fichier, puis modification si activée. Les dates avec fuseau sont converties ; QuickTime entier est considéré UTC. Choisissez la journée réelle de capture pour les exports dont la date a changé. Les traces ne sont pas découpées. Pour Geo-Log, imposez une journée afin de conserver ensemble les liens HTML et les médias associés. Les ZIP doivent être décompressés avant ingestion.

6. Sélection et publication
Dans Workflow > Gérer les fichiers…, ajoutez une sélection ou un réseau activé, contenant uniquement les fichiers choisis/finalisés, avec une date imposée. WhatsApp accepte une photo et une vidéo par jour au maximum. Pour modifier le choix déjà copié, archivez ou retirez manuellement l’ancien fichier puis réanalysez. Instagram et Facebook partagent leur dossier lorsque le mode miroir et les deux canaux sont activés. Aucun envoi vers les réseaux n’est effectué.

7. ExifTool
ExifTool… sélectionne exiftool.exe ; Auto relance la recherche près de l’application, dans tools et dans le PATH ; Retester affiche la version et le statut. Le chemin est mémorisé. ExifTool est optionnel et installé séparément ; gardez son dossier exiftool_files à côté de l’exécutable. En son absence, la lecture interne est utilisée et les dates manquantes doivent être corrigées.

8. Rapports et sauvegarde
Le CSV détaille chaque résultat. Le journal peut être enregistré. Après copie, un CSV est placé dans 00_TRIP/NOTES, dossier utile au rapport. Arrêter conserve les copies terminées et nettoie le fichier partiel. Refaites un aperçu pour reprendre. Sauvegardez le voyage sur un deuxième support indépendant.
"""

def application_icon():
    # __file__ resolves within the bundle under PyInstaller and beside source otherwise.
    return QIcon(':/vespa/vespa.ico')

def main():
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Vespa.TravelContentOrganizer')
    if '--self-test' in sys.argv:
        os.environ['VESPA_SETTINGS_DIR']=str(Path(sys.argv[sys.argv.index('--self-test')+1]).resolve().parent/'test-settings')
    setup_diagnostics()
    app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(STYLE);app.setApplicationName(APP_NAME);app.setApplicationVersion(VERSION);app.setFont(QFont('Segoe UI',9));app.setPalette(dark_palette());app.setWindowIcon(application_icon());window=Window();window.setWindowIcon(app.windowIcon())
    if '--self-test' in sys.argv:
        assert not app.windowIcon().isNull() and not window.windowIcon().isNull()
        assert not app.windowIcon().pixmap(32,32).isNull()
        # Reproducible startup/engine check for the packaged Windows executable.
        import tempfile
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);source=base/'source';source.mkdir();im=Image.new('RGB',(8,8));im.save(source/'PXL_20260907_120000.jpg')
            c=Config(str(base/'archive'),'Test',[Source(str(source),'Pixel 11')]);rows=scan(c);assert rows[0].status=='Prêt';execute(c,rows);assert rows[0].status=='Copié';assert scan(c)[0].status=='Doublon'
            window.rows=rows;window.model.set_rows(rows);window.refresh();app.processEvents()
            dlg=RoadtripDialog(window)
            assert dlg.checks['devices']['DJI Mini 4 Pro'].isChecked()
            assert not dlg.checks['devices']['DJI Air 3'].isChecked()
            from test_day_dates import verify_day_dates
            day_proof=verify_day_dates(window)
            from test_ui_behavior import verify_ui
            ui_proof=verify_ui(app,window,RoadtripDialog,SourceDialog)
            from test_checkboxes import verify_checkboxes
            checkbox_proof=verify_checkboxes(app,window,base,RoadtripDialog,STYLE,':/vespa/check.svg')
            x5=base/'X5';x5.mkdir();(x5/'20260907.insv').write_bytes(b'raw');(x5/'20260907.mp4').write_bytes(b'export')
            xc=Config(str(base/'archive'),'X5',[Source(str(x5),'Insta360 X5',exports_confirmed=True)],exiftool_enabled=False)
            xr=scan(xc);assert sum(r.status=='Prêt' for r in xr)==1 and sum(r.status=='Exclu' for r in xr)==1
            execute(xc,xr);assert not any(p.name in {'ORIGINAL','PHOTO'} for p in (base/'archive/X5').rglob('*'))
            index=sys.argv.index('--self-test');out=Path(sys.argv[index+1]);out.write_text(json.dumps({'ok':True,'checkboxes':checkbox_proof,'interface':ui_proof,'day_dates':day_proof,'checks':['Qt window','Application and window icons','Pillow','timezone','preview','copy','SHA-256','duplicate','Roadtrip settings dialog','Device defaults','X5 exports only','No empty folders']},indent=2),encoding='utf-8')
        return
    window.show();sys.exit(app.exec())

if __name__=='__main__':main()
