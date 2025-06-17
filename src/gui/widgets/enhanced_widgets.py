"""
Enhanced widgets with integrated information support using the new InfoManager system.
These widgets replace the previous InfoItem and InfoGroupBox implementations.
"""
from PyQt6.QtWidgets import QGroupBox, QWidget, QSlider, QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal
from typing import Optional

from .info_manager import InfoManager


class InfoGroupBox(QGroupBox):
    """
    Enhanced QGroupBox with integrated information support.
    Much more stable than the previous implementation using eventFilter.
    """
    
    def __init__(self, title: str = "", info_text: str = "", 
                 info_manager: Optional[InfoManager] = None, parent=None):
        super().__init__(title, parent)
        
        # Info system integration
        self._info_manager = info_manager
        self._info_text = info_text
        self._is_registered = False
        
        # Setup mouse tracking for hover detection
        self.setMouseTracking(True)
        
        # Register with info manager if provided
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """Set or change the InfoManager for this widget."""
        # Unregister from old manager
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
        self._info_manager = info_manager
        
        # Register with new manager
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_text(self, info_text: str):
        """Set or update the information text."""
        self._info_text = info_text
        
        if self._is_registered and self._info_manager:
            self._info_manager.update_widget_info(self, info_text)
        elif self._info_manager and info_text:
            self._register_with_manager()
            
    def _register_with_manager(self):
        """Register this widget with the InfoManager."""
        if self._info_manager and self._info_text and not self._is_registered:
            self._info_manager.register_widget(self, self._info_text)
            self._is_registered = True
            
    def _unregister_from_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
    def get_info_text(self) -> str:
        """Get the current information text."""
        return self._info_text
        
    def closeEvent(self, event):
        """Clean up when widget is closed."""
        self._unregister_from_manager()
        super().closeEvent(event)


class InfoWidget(QWidget):
    """
    Enhanced QWidget with integrated information support.
    Can be used as a base class or standalone widget with info capabilities.
    """
    
    def __init__(self, info_text: str = "", info_manager: Optional[InfoManager] = None, 
                 parent=None):
        super().__init__(parent)
        
        # Info system integration
        self._info_manager = info_manager
        self._info_text = info_text
        self._is_registered = False
        
        # Setup mouse tracking
        self.setMouseTracking(True)
        
        # Register with info manager if provided
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """Set or change the InfoManager for this widget."""
        # Unregister from old manager
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
        self._info_manager = info_manager
        
        # Register with new manager
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_text(self, info_text: str):
        """Set or update the information text."""
        self._info_text = info_text
        
        if self._is_registered and self._info_manager:
            self._info_manager.update_widget_info(self, info_text)
        elif self._info_manager and info_text:
            self._register_with_manager()
            
    def _register_with_manager(self):
        """Register this widget with the InfoManager."""
        if self._info_manager and self._info_text and not self._is_registered:
            self._info_manager.register_widget(self, self._info_text)
            self._is_registered = True
            
    def _unregister_from_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
    def get_info_text(self) -> str:
        """Get the current information text."""
        return self._info_text
        
    def closeEvent(self, event):
        """Clean up when widget is closed."""
        self._unregister_from_manager()
        super().closeEvent(event)


class InfoSlider(QSlider):
    """
    Enhanced QSlider with integrated information support.
    Provides hover information without the complexity of multiple inheritance.
    """
    
    def __init__(self, orientation, info_text: str = "", 
                 info_manager: Optional[InfoManager] = None, parent=None):
        super().__init__(orientation, parent)
        
        # Info system integration
        self._info_manager = info_manager
        self._info_text = info_text
        self._is_registered = False
        
        # Setup mouse tracking
        self.setMouseTracking(True)
        
        # Register with info manager if provided
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """Set or change the InfoManager for this widget."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
        self._info_manager = info_manager
        
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_text(self, info_text: str):
        """Set or update the information text."""
        self._info_text = info_text
        
        if self._is_registered and self._info_manager:
            self._info_manager.update_widget_info(self, info_text)
        elif self._info_manager and info_text:
            self._register_with_manager()
            
    def _register_with_manager(self):
        """Register this widget with the InfoManager."""
        if self._info_manager and self._info_text and not self._is_registered:
            self._info_manager.register_widget(self, self._info_text)
            self._is_registered = True
            
    def _unregister_from_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
    def get_info_text(self) -> str:
        """Get the current information text."""
        return self._info_text


class InfoComboBox(QComboBox):
    """
    Enhanced QComboBox with integrated information support.
    """
    
    def __init__(self, info_text: str = "", info_manager: Optional[InfoManager] = None, 
                 parent=None):
        super().__init__(parent)
        
        # Info system integration
        self._info_manager = info_manager
        self._info_text = info_text
        self._is_registered = False
        
        # Setup mouse tracking
        self.setMouseTracking(True)
        
        # Register with info manager if provided
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """Set or change the InfoManager for this widget."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
        self._info_manager = info_manager
        
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_text(self, info_text: str):
        """Set or update the information text."""
        self._info_text = info_text
        
        if self._is_registered and self._info_manager:
            self._info_manager.update_widget_info(self, info_text)
        elif self._info_manager and info_text:
            self._register_with_manager()
            
    def _register_with_manager(self):
        """Register this widget with the InfoManager."""
        if self._info_manager and self._info_text and not self._is_registered:
            self._info_manager.register_widget(self, self._info_text)
            self._is_registered = True
            
    def _unregister_from_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
    def get_info_text(self) -> str:
        """Get the current information text."""
        return self._info_text


class InfoLabel(QLabel):
    """
    Enhanced QLabel with integrated information support.
    Useful for creating informational labels that show additional details on hover.
    """
    
    def __init__(self, text: str = "", info_text: str = "", 
                 info_manager: Optional[InfoManager] = None, parent=None):
        super().__init__(text, parent)
        
        # Info system integration
        self._info_manager = info_manager
        self._info_text = info_text
        self._is_registered = False
        
        # Setup mouse tracking
        self.setMouseTracking(True)
        
        # Register with info manager if provided
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """Set or change the InfoManager for this widget."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
        self._info_manager = info_manager
        
        if self._info_manager and self._info_text:
            self._register_with_manager()
            
    def set_info_text(self, info_text: str):
        """Set or update the information text."""
        self._info_text = info_text
        
        if self._is_registered and self._info_manager:
            self._info_manager.update_widget_info(self, info_text)
        elif self._info_manager and info_text:
            self._register_with_manager()
            
    def _register_with_manager(self):
        """Register this widget with the InfoManager."""
        if self._info_manager and self._info_text and not self._is_registered:
            self._info_manager.register_widget(self, self._info_text)
            self._is_registered = True
            
    def _unregister_from_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._is_registered and self._info_manager:
            self._info_manager.unregister_widget(self)
            self._is_registered = False
            
    def get_info_text(self) -> str:
        """Get the current information text."""
        return self._info_text 