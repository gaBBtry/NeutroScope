"""
Programme pédagogique interactif sur la neutronique des REP
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from src.gui.main_window import MainWindow
from src.model.config import setup_openmc_data, get_project_root, OPENMC_DATA_PATH

def check_openmc_cross_sections():
    """
    Check if the OPENMC_CROSS_SECTIONS environment variable is set.
    If not, first look for cross_sections.xml in the data directory.
    If not found, ask the user to locate the cross_sections.xml file.
    """
    # Try to setup OpenMC data automatically using config
    if setup_openmc_data():
        return
    
    # If automatic setup failed, ask the user
    # A QApplication instance is needed to show dialogs
    app_for_dialog = QApplication.instance() or QApplication(sys.argv)
    
    project_root = get_project_root()
    expected_path = project_root / OPENMC_DATA_PATH / "cross_sections.xml"
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setText("Configuration d'OpenMC requise")
    msg_box.setInformativeText(
        "Le simulateur de réacteur utilise OpenMC pour des calculs précis. "
        f"Le fichier cross_sections.xml n'a pas été trouvé dans {expected_path}. "
        "Pour continuer, veuillez localiser votre fichier `cross_sections.xml`."
        "\n\nCe fichier est essentiel pour qu'OpenMC puisse accéder aux données nucléaires."
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    ret = msg_box.exec()

    if ret == QMessageBox.StandardButton.Ok:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner cross_sections.xml",
            str(project_root / "data"),  # Start in data directory
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