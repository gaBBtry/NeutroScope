"""
Refactored information panel with improved stability and integration
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class InfoPanel(QFrame):
    """
    An always-visible panel to display context-sensitive information.
    Integrates with the InfoManager system.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup UI
        self._setup_ui()
        self._setup_styles()
        
        # State management
        self._current_text = ""
        
        # Always visible
        self.setVisible(True)
        
    def _setup_ui(self):
        """Setup the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header with title and subtitle
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title and subtitle container
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(0)
        
        # Title
        self.title_label = QLabel("Informations")
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 1)
        self.title_label.setFont(title_font)
        
        # Subtitle
        self.subtitle_label = QLabel("Appuyez sur 'i' pour ouvrir la fenêtre d'informations")
        subtitle_font = self.subtitle_label.font()
        subtitle_font.setPointSize(subtitle_font.pointSize() - 1)
        self.subtitle_label.setStyleSheet("color: #666; margin-top: 1px;")
        self.subtitle_label.setFont(subtitle_font)
        
        title_vbox.addWidget(self.title_label)
        title_vbox.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        
        # Content area with scroll support
        self.content_widget = QTextEdit()
        self.content_widget.setReadOnly(True)
        self.content_widget.setMinimumHeight(60)
        
        # Set default content
        self._set_default_content()
        
        # Add to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.content_widget)
        
        # Size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
    def _setup_styles(self):
        """Setup the visual styling for the panel."""
        self.setStyleSheet("""
            InfoPanel {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        self.content_widget.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
    def _set_default_content(self):
        """Set the default content when no information is available."""
        default_text = (
            "<p style='color: #888; font-style: italic;'>"
            "Survolez un élément pour afficher des informations."
            "</p>"
        )
        self.content_widget.setHtml(default_text)
        
    def update_info(self, text: str):
        """
        Update the information text immediately for fluid real-time updates.
        
        Args:
            text: The new information text to display
        """
        self._current_text = text.strip()
        
        # Update immediately for fluid experience
        self._update_content()
        
    def _update_content(self):
        """Perform the actual content update."""
        if self._current_text:
            # Format the text with basic HTML for better presentation
            formatted_text = self._format_info_text(self._current_text)
            self.content_widget.setHtml(formatted_text)
        else:
            # Clear content
            self._set_default_content()
        
    def _format_info_text(self, text: str) -> str:
        """
        Format plain text into basic HTML for better presentation.
        
        Args:
            text: The plain text to format
            
        Returns:
            str: HTML formatted text
        """
        # Split into lines and process
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if i > 0 and lines[i-1].strip():
                    formatted_lines.append('<br>')
            elif line.endswith(':'):
                # Treat as a header
                formatted_lines.append(f'<p style="font-weight: bold; color: #333; margin-top: 8px; margin-bottom: 4px;">{line}</p>')
            elif line.startswith('- '):
                # Treat as a list item
                item = line[2:]
                formatted_lines.append(f'<p style="margin-left: 16px; margin-top: 2px; margin-bottom: 2px;">• {item}</p>')
            else:
                # Regular paragraph
                formatted_lines.append(f'<p style="margin-top: 4px; margin-bottom: 4px; line-height: 1.5;">{line}</p>')
                
        return ''.join(formatted_lines)
        
    def clear_info(self):
        """Clear the current information."""
        self.update_info("")
        
    def get_current_info_text(self) -> str:
        """Get the current raw information text."""
        return self._current_text
        
    def get_current_info_html(self) -> str:
        """Get the current HTML-formatted information text."""
        if not self._current_text:
            return ""
        return self._format_info_text(self._current_text) 