"""
Panel for displaying information about visualizations
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy, 
    QScrollArea, QDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class InfoPanel(QFrame):
    """Panel for displaying information about visualizations"""
    
    # Signal emitted when panel is closed
    closed = pyqtSignal()
    # Signal to request detailed info display
    show_details = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        # Main layout for the panel
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with title and close button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Informations")
        font = self.title_label.font()
        font.setBold(True)
        self.title_label.setFont(font)
        
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("font-size: 14px; border-radius: 10px; background-color: #e0e0e0;")
        close_button.clicked.connect(self.close_panel)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        # Content label
        self.info_label = QLabel("Survolez un élément pour afficher des informations.")
        self.info_label.setWordWrap(True)
        self.info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.info_label)
        
        # Initially hidden
        self.setVisible(False)

    def update_info(self, text):
        """Update the information text"""
        self.info_label.setText(text)
        if text:
            self.setVisible(True)
        else:
            self.setVisible(False)
            
    def close_panel(self):
        """Close the panel"""
        self.setVisible(False)
        self.closed.emit() 