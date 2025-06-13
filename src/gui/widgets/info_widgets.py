"""
Info-enabled widgets
"""
from PyQt6.QtWidgets import QWidget, QGroupBox
from PyQt6.QtCore import pyqtSignal, QEvent


class InfoItem(QWidget):
    """
    Mixin class to add hover information capability to any widget
    """
    # Signal to send info to the info panel
    info_signal = pyqtSignal(str)
    
    def __init__(self, parent=None, info_text=""):
        super().__init__(parent)
        self.info_text = info_text
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to detect mouse hover"""
        if event.type() == QEvent.Type.Enter:
            # Mouse entered widget
            self.send_info()
        elif event.type() == QEvent.Type.Leave:
            # Mouse left widget
            self.clear_info()
        return super().eventFilter(obj, event)
    
    def send_info(self):
        """Send info text to the panel"""
        self.info_signal.emit(self.info_text)
    
    def clear_info(self):
        """Clear info panel"""
        self.info_signal.emit("")
    
    def set_info_text(self, text):
        """Set the information text for this widget"""
        self.info_text = text


class InfoGroupBox(QGroupBox):
    """GroupBox with hover information capability"""
    
    info_signal = pyqtSignal(str)
    
    def __init__(self, title, info_text="", parent=None):
        super().__init__(title, parent)
        self.info_text = info_text
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to detect mouse hover"""
        if event.type() == QEvent.Type.Enter:
            # Mouse entered widget
            self.send_info()
        elif event.type() == QEvent.Type.Leave:
            # Mouse left widget
            self.clear_info()
        return super().eventFilter(obj, event)
    
    def send_info(self):
        """Send info text to the panel"""
        self.info_signal.emit(self.info_text)
    
    def clear_info(self):
        """Clear info panel"""
        self.info_signal.emit("")
    
    def set_info_text(self, text):
        """Set the information text for this widget"""
        self.info_text = text 