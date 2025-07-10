"""
Centralized information management system for the application
"""
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
from typing import Optional, Dict, Any


class InfoManager(QObject):
    """
    Centralized manager for handling information display throughout the application.
    Provides a clean, robust interface for widget information management.
    """
    
    # Signal emitted when info should be displayed
    info_requested = pyqtSignal(str)
    # Signal emitted when info should be cleared
    info_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._registered_widgets: Dict[QWidget, str] = {}
        self._current_info_widget: Optional[QWidget] = None
        
    def register_widget(self, widget: QWidget, info_text: str):
        """
        Register a widget with its associated information text.
        
        Args:
            widget: The widget to register
            info_text: The information text to display when hovering over the widget
        """
        if widget in self._registered_widgets:
            self.unregister_widget(widget)
            
        self._registered_widgets[widget] = info_text
        
        # Install event handling for hover detection
        widget.installEventFilter(self)
        widget.setMouseTracking(True)
        
    def unregister_widget(self, widget: QWidget):
        """
        Unregister a widget from the info system.
        
        Args:
            widget: The widget to unregister
        """
        if widget in self._registered_widgets:
            widget.removeEventFilter(self)
            del self._registered_widgets[widget]
            
            # Clear info if this widget was currently showing info
            if self._current_info_widget == widget:
                self._current_info_widget = None
                self.info_cleared.emit()
                
    def update_widget_info(self, widget: QWidget, new_info_text: str):
        """
        Update the information text for a registered widget.
        
        Args:
            widget: The widget to update
            new_info_text: The new information text
        """
        if widget in self._registered_widgets:
            self._registered_widgets[widget] = new_info_text
            
            # If this widget is currently showing info, update it
            if self._current_info_widget == widget:
                self.info_requested.emit(new_info_text)
                
    def show_info(self, widget: QWidget):
        """
        Manually show information for a specific widget.
        
        Args:
            widget: The widget whose info should be shown
        """
        if widget in self._registered_widgets:
            self._current_info_widget = widget
            self.info_requested.emit(self._registered_widgets[widget])
            
    def clear_info(self):
        """Manually clear the currently displayed information."""
        self._current_info_widget = None
        self.info_cleared.emit()
        
    def eventFilter(self, obj: QObject, event) -> bool:
        """
        Event filter to handle mouse enter/leave events for registered widgets.
        
        Args:
            obj: The object that received the event
            event: The event to process
            
        Returns:
            bool: False to allow normal event processing
        """
        # Defensive check - ensure _registered_widgets exists
        if not hasattr(self, '_registered_widgets'):
            self._registered_widgets = {}
            self._current_info_widget = None
            
        if not isinstance(obj, QWidget) or obj not in self._registered_widgets:
            return False
            
        from PyQt6.QtCore import QEvent
        
        if event.type() == QEvent.Type.Enter:
            # Mouse entered widget - show its info
            self._current_info_widget = obj
            self.info_requested.emit(self._registered_widgets[obj])
            
        elif event.type() == QEvent.Type.Leave:
            # Mouse left widget - clear info if this widget was showing it
            if self._current_info_widget == obj:
                self._current_info_widget = None
                self.info_cleared.emit()
                
        return False  # Always allow normal event processing
        
    def get_registered_widgets(self) -> Dict[QWidget, str]:
        """
        Get a copy of all registered widgets and their info texts.
        
        Returns:
            Dict mapping widgets to their info texts
        """
        return self._registered_widgets.copy()
        
    def is_widget_registered(self, widget: QWidget) -> bool:
        """
        Check if a widget is registered with the info manager.
        
        Args:
            widget: The widget to check
            
        Returns:
            bool: True if the widget is registered
        """
        return widget in self._registered_widgets


class InfoMixin:
    """
    Mixin class that can be added to any widget to easily integrate with InfoManager.
    This provides a clean interface without the complexity of multiple inheritance.
    """
    
    def __init__(self, *args, info_manager: Optional[InfoManager] = None, 
                 info_text: str = "", **kwargs):
        """
        Initialize the mixin.
        
        Args:
            info_manager: The InfoManager instance to use (optional)
            info_text: The initial information text
        """
        super().__init__(*args, **kwargs)
        self._info_manager = info_manager
        self._info_text = info_text
        
        if self._info_manager and self._info_text:
            self.register_with_info_manager()
            
    def set_info_manager(self, info_manager: InfoManager):
        """
        Set or change the InfoManager for this widget.
        
        Args:
            info_manager: The InfoManager instance to use
        """
        # Unregister from old manager if needed
        if self._info_manager and hasattr(self, '_registered'):
            self._info_manager.unregister_widget(self)
            
        self._info_manager = info_manager
        
        if self._info_manager and self._info_text:
            self.register_with_info_manager()
            
    def set_info_text(self, info_text: str):
        """
        Set or update the information text for this widget.
        
        Args:
            info_text: The new information text
        """
        self._info_text = info_text
        
        if self._info_manager:
            if hasattr(self, '_registered'):
                self._info_manager.update_widget_info(self, info_text)
            else:
                self.register_with_info_manager()
                
    def register_with_info_manager(self):
        """Register this widget with the current InfoManager."""
        if self._info_manager and self._info_text:
            self._info_manager.register_widget(self, self._info_text)
            self._registered = True
            
    def unregister_from_info_manager(self):
        """Unregister this widget from the InfoManager."""
        if self._info_manager and hasattr(self, '_registered'):
            self._info_manager.unregister_widget(self)
            delattr(self, '_registered')
            
    def get_info_text(self) -> str:
        """Get the current information text for this widget."""
        return self._info_text 