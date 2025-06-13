"""
InfoButton widget
"""
from PyQt6.QtWidgets import QToolButton
from PyQt6.QtGui import QFont


class InfoButton(QToolButton):
    """Button to toggle the info panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("i")
        self.setCheckable(True)
        
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
            QToolButton:checked {
                background-color: #cce5ff;
                border: 1px solid #007bff;
            }
            QToolButton:hover {
                background-color: #e9e9e9;
            }
        """)
        self.update_tooltip(False)

    def update_tooltip(self, is_panel_visible):
        """Update tooltip based on panel visibility"""
        if is_panel_visible:
            self.setToolTip("Cacher le panneau d'information (i)")
        else:
            self.setToolTip("Afficher le panneau d'information (i)") 