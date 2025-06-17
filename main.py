"""
Programme pédagogique interactif sur la neutronique des REP
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QButtonGroup, QRadioButton
from PyQt6.QtCore import Qt
from src.gui.main_window import MainWindow
from src.model.config import setup_openmc_data, get_project_root, OPENMC_DATA_PATH, get_calculation_modes, set_calculation_mode, should_use_openmc

class ModeSelectionDialog(QDialog):
    """Dialog pour sélectionner le mode de calcul"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choix du mode de calcul")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.selected_mode = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Choisissez votre mode de calcul :")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description générale
        description = QLabel(
            "NeutroScope propose deux modes de calcul pour s'adapter à vos besoins :\n"
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(description)
        
        # Groupe de boutons radio
        self.button_group = QButtonGroup()
        
        # Récupérer les modes depuis la configuration
        modes = get_calculation_modes()
        
        for mode_id, mode_info in modes.items():
            if mode_id == "auto":  # On ne propose pas le mode auto dans l'interface
                continue
                
            radio = QRadioButton(mode_info["name"])
            radio.setObjectName(mode_id)
            
            # Description du mode
            desc_label = QLabel(mode_info["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("margin-left: 20px; margin-bottom: 10px; color: #666;")
            
            layout.addWidget(radio)
            layout.addWidget(desc_label)
            
            self.button_group.addButton(radio)
            
            # Sélectionner le mode rapide par défaut
            if mode_id == "fast":
                radio.setChecked(True)
                self.selected_mode = mode_id
        
        # Connecter le signal de changement
        self.button_group.buttonClicked.connect(self.on_mode_changed)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Continuer")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Quitter")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_mode_changed(self, button):
        """Gérer le changement de mode sélectionné"""
        self.selected_mode = button.objectName()

def choose_calculation_mode():
    """
    Propose à l'utilisateur de choisir le mode de calcul.
    Retourne le mode choisi ou None si annulé.
    """
    # Créer une application temporaire si nécessaire
    app = QApplication.instance() or QApplication(sys.argv)
    
    dialog = ModeSelectionDialog()
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        return dialog.selected_mode
    else:
        return None

def check_openmc_cross_sections():
    """
    Check calculation mode and setup OpenMC if needed.
    """
    # D'abord, demander à l'utilisateur le mode de calcul souhaité
    chosen_mode = choose_calculation_mode()
    
    if chosen_mode is None:
        # L'utilisateur a annulé
        sys.exit(0)
    
    # Définir le mode choisi
    set_calculation_mode(chosen_mode)
    
    # Si le mode choisi ne nécessite pas OpenMC, on peut continuer
    use_openmc = should_use_openmc()
    if use_openmc is False:
        print("✓ Mode rapide sélectionné - OpenMC non requis")
        return
    
    # Si OpenMC est requis, vérifier sa disponibilité
    if use_openmc is True:
        # Mode précis : OpenMC obligatoire
        if not setup_openmc_data():
            # OpenMC requis mais non disponible, demander le fichier
            ask_for_cross_sections_file()
    else:
        # Mode auto : essayer OpenMC, utiliser analytique si non disponible
        setup_openmc_data()  # Essayer silencieusement

def ask_for_cross_sections_file():
    """Demander à l'utilisateur de localiser le fichier cross_sections.xml"""
    app_for_dialog = QApplication.instance() or QApplication(sys.argv)
    
    project_root = get_project_root()
    expected_path = project_root / OPENMC_DATA_PATH / "cross_sections.xml"
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText("Données OpenMC requises")
    msg_box.setInformativeText(
        "Le mode précis nécessite OpenMC avec des données nucléaires.\n"
        f"Le fichier cross_sections.xml n'a pas été trouvé dans {expected_path}.\n\n"
        "Voulez-vous :\n"
        "• Localiser le fichier cross_sections.xml\n"
        "• Passer en mode rapide (analytique)"
    )
    
    locate_button = msg_box.addButton("Localiser le fichier", QMessageBox.ButtonRole.AcceptRole)
    fast_button = msg_box.addButton("Mode rapide", QMessageBox.ButtonRole.AcceptRole)
    quit_button = msg_box.addButton("Quitter", QMessageBox.ButtonRole.RejectRole)
    
    msg_box.exec()
    clicked_button = msg_box.clickedButton()
    
    if clicked_button == locate_button:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner cross_sections.xml",
            str(project_root / "data"),
            "XML Files (*.xml);;All Files (*)"
        )
        if file_path:
            os.environ['OPENMC_CROSS_SECTIONS'] = file_path
            QMessageBox.information(None, "Succès", f"Données OpenMC configurées :\n{file_path}")
        else:
            # Pas de fichier sélectionné, passer en mode rapide
            set_calculation_mode("fast")
            QMessageBox.information(None, "Mode rapide", "Passage automatique en mode rapide.")
    
    elif clicked_button == fast_button:
        set_calculation_mode("fast")
        QMessageBox.information(None, "Mode rapide", "Mode rapide activé.")
    
    else:
        # Quitter
        sys.exit(0)

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