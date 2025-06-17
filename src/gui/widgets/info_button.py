"""
InfoButton widget
"""
from PyQt6.QtWidgets import QToolButton
from PyQt6.QtGui import QFont


class InfoButton(QToolButton):
    """Button to show the detailed info dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("i")
        
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 15px; /* Perfect circle */
                background-color: #f0f0f0;
                color: #555;
            }
            QToolButton:hover {
                background-color: #e9e9e9;
            }
            QToolButton:pressed {
                background-color: #cce5ff;
                border: 1px solid #007bff;
            }
        """)
        self.setToolTip("Afficher les informations détaillées (i)") 