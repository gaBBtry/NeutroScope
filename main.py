"""
Programme pédagogique interactif sur la neutronique des REP
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from src.gui.main_window import MainWindow

def check_openmc_cross_sections():
    """
    Check if the OPENMC_CROSS_SECTIONS environment variable is set.
    If not, ask the user to locate the cross_sections.xml file.
    """
    if not os.environ.get('OPENMC_CROSS_SECTIONS'):
        # A QApplication instance is needed to show dialogs
        app_for_dialog = QApplication.instance() or QApplication(sys.argv)
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("Configuration d'OpenMC requise")
        msg_box.setInformativeText(
            "Le simulateur de réacteur utilise OpenMC pour des calculs précis. "
            "Pour continuer, veuillez localiser votre fichier `cross_sections.xml`."
            "\n\nCe fichier est essentiel pour qu'OpenMC puisse accéder aux données nucléaires."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ret = msg_box.exec()

        if ret == QMessageBox.StandardButton.Ok:
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Sélectionner cross_sections.xml",
                "",
                "XML Files (*.xml);;All Files (*)"
            )
            if file_path:
                os.environ['OPENMC_CROSS_SECTIONS'] = file_path
                QMessageBox.information(None, "Succès", f"Variable d'environnement OPENMC_CROSS_SECTIONS définie à:\n{file_path}")
            else:
                # User cancelled the file dialog
                QMessageBox.warning(
                    None, 
                    "Avertissement", 
                    "Aucun fichier sélectionné. Le programme utilisera un modèle analytique simplifié. "
                    "Les calculs de criticité pourraient être moins précis."
                )
        else:
            # User cancelled the info message
            QMessageBox.warning(
                None, 
                "Avertissement", 
                "Configuration annulée. Le programme utilisera un modèle analytique simplifié. "
                "Les calculs de criticité pourraient être moins précis."
            )
        # We might not need to keep this QApplication running
        # app_for_dialog.quit()


def main():
    """Main entry point for the application"""
    # Check for OpenMC cross sections before starting the main app
    check_openmc_cross_sections()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 