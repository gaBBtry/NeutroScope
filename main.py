"""
Programme pédagogique interactif sur la neutronique des REP
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 