"""Small, scalable Vespa vignette. No external image or animation dependency."""
import math
import sys
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtWidgets import QWidget, QSizePolicy

class VespaRide(QWidget):
    animationChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(0)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.phase = 0.0
        self.animated = True
        if sys.platform == 'win32':
            import ctypes
            enabled = ctypes.c_int(1)
            if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
                self.animated = bool(enabled.value)
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.tick)
        self.update_tip()

    def update_tip(self):
        self.setToolTip('Petite échappée à Vespa — clic ou Espace pour '+('mettre en pause.' if self.animated else 'animer.'))
        self.setAccessibleName('Animation Vespa : '+('en mouvement' if self.animated else 'en pause'))

    def setAnimated(self, value):
        self.animated = bool(value)
        if self.animated and self.isVisible():self.timer.start()
        else:self.timer.stop()
        self.update_tip()
        self.update()

    def toggle(self):
        self.setAnimated(not self.animated)
        self.animationChanged.emit(self.animated)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:self.toggle()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Space, Qt.Key_Return):self.toggle();event.accept()
        else:super().keyPressEvent(event)

    def showEvent(self, event):
        if self.animated:self.timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def tick(self):
        self.phase = (self.phase + .05) % 120
        self.update()

    def paintEvent(self, event):
        if self.width() < 44:return
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        w=self.width()
        left=max(4,(w-320)/2);right=min(w-4,(w+320)/2)
        p.setPen(QPen(QColor('#514359'),1))
        p.drawLine(QPointF(left,39),QPointF(right,39))
        p.setPen(QPen(QColor('#756282'),1.4,Qt.SolidLine,Qt.RoundCap))
        drift=self.phase*12%28
        for i in range(int((right-left)/28)+1):
            x=left+i*28-drift
            if x>=left and x+8<=right:p.drawLine(QPointF(x,42),QPointF(x+8,42))
        # Delicate sun, visible only when the strip has breathing room.
        if w>200:
            p.setPen(Qt.NoPen);p.setBrush(QColor('#f4cf4d'));p.drawEllipse(QPointF(right-20,11),3,3)
        p.save();p.translate(w/2-34,2+math.sin(self.phase*3)*.55)
        # Wheels and hubs.
        for x in (13,55):
            p.setPen(QPen(QColor('#eeeaf2'),2.6));p.setBrush(QColor('#202020'));p.drawEllipse(QPointF(x,30),6,6)
            p.setPen(QPen(QColor('#ba8aff'),1.3));p.drawEllipse(QPointF(x,30),1.8,1.8)
        # Rounded rear shell, footboard, steering column and front mudguard.
        body=QPainterPath();body.moveTo(3,26);body.cubicTo(3,17,10,17,22,18);body.lineTo(29,29);body.lineTo(43,29);body.lineTo(46,13);body.lineTo(42,7)
        p.setPen(QPen(QColor('#ba8aff'),5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin));p.setBrush(Qt.NoBrush);p.drawPath(body)
        fender=QPainterPath();fender.moveTo(47,24);fender.quadTo(56,18,64,25);p.setPen(QPen(QColor('#ba8aff'),3,Qt.SolidLine,Qt.RoundCap));p.drawPath(fender)
        p.setPen(QPen(QColor('#eeeaf2'),2,Qt.SolidLine,Qt.RoundCap));p.drawLine(QPointF(41,7),QPointF(49,7));p.drawLine(QPointF(44,6),QPointF(42,2))
        p.setPen(Qt.NoPen);p.setBrush(QColor('#f4cf4d'));p.drawRoundedRect(QRectF(7,13,16,3),1.4,1.4);p.drawEllipse(QPointF(50,9),2,2)
        # Tiny strapped travel case.
        p.setPen(QPen(QColor('#f4cf4d'),1));p.setBrush(QColor('#f4cf4d'));p.drawRoundedRect(QRectF(4,4,12,8),2,2)
        p.setPen(QPen(QColor('#705b26'),1));p.drawLine(QPointF(8,5),QPointF(8,11));p.drawLine(QPointF(12,5),QPointF(12,11))
        p.restore()
