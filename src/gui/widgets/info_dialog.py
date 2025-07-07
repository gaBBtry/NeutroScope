"""
Dialog for displaying detailed information text.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, 
    QSizePolicy, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class InfoDialog(QDialog):
    """
    A dialog window to display detailed, scrollable information text.
    It takes HTML formatted text for rich presentation.
    """
    
    def __init__(self, title: str, content_html: str, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.setModal(False)  # Allow interaction with main window
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setHtml(content_html)
        self.text_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        
        # Add widgets to layout
        layout.addWidget(self.text_display)
        layout.addWidget(button_box)
        
        # Apply some styling
        self._setup_styles()
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Close dialog on 'i' key or Escape
        if event.key() == Qt.Key.Key_I or event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
        
    def _setup_styles(self):
        """Setup the visual styling for the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
        """)
        
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        
    @staticmethod
    def show_info(title: str, content_html: str, parent=None):
        """
        Static method to create and show the dialog.
        
        Args:
            title: The title for the dialog window.
            content_html: The HTML content to display.
            parent: The parent widget.
        """
        if not content_html.strip():
            return
            
        dialog = InfoDialog(title, content_html, parent)
        dialog.exec() 