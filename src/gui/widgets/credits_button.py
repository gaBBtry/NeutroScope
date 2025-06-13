"""
CreditsButton widget
"""
from PyQt6.QtWidgets import (
    QToolButton, QDialog, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CreditsButton(QToolButton):
    """Button to show the credits dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("©")  # Unicode copyright symbol
        self.setToolTip("Afficher les crédits")
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("""
            QToolButton { 
                border: 1px solid #ddd; 
                border-radius: 4px;
                padding: 5px; 
                background-color: #f8f8f8;
                color: #888;
            }
            QToolButton:hover { 
                background-color: #e6e6e6; 
                color: #444;
            }
        """)
        self.setFixedSize(30, 30)
        self.clicked.connect(self.show_credits)
        
    def show_credits(self):
        """Show the credits dialog"""
        dialog = QDialog(self.parent())
        dialog.setWindowTitle("Crédits")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Simulation Neutronique des REP")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        credits = QLabel(
            "© 2023-2024 EDF UFPI\n\n"
            "Développé pour la formation et l'apprentissage\n"
            "des principes de la neutronique des réacteurs.\n\n"
            "Version: alpha 0.1"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setWordWrap(True)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        
        layout.addWidget(title)
        layout.addWidget(credits)
        layout.addWidget(close_button)
        
        dialog.exec() 