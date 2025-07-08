"""
Dialog avancé pour la gestion des presets avec fonctionnalités CRUD complètes
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QMessageBox, QFileDialog, QSplitter,
    QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from ...model.preset_model import PresetManager, PresetData, PresetCategory, PresetType


class PresetManagerDialog(QDialog):
    """Dialog principal pour la gestion avancée des presets"""
    
    preset_applied = pyqtSignal(str)  # Signal émis quand un preset est appliqué
    
    def __init__(self, preset_manager: PresetManager, current_state_preset: PresetData, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.current_state_preset = current_state_preset
        self.current_preset_item = None
        
        self.setWindowTitle("Gestionnaire de Presets - NeutroScope")
        self.setModal(True)
        self.resize(900, 600)
        
        self.setup_ui()
        self.connect_signals()
        self.load_presets()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Toolbar avec boutons principaux
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Splitter principal horizontal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Panneau gauche : liste des presets
        left_panel = self.create_preset_list_panel()
        main_splitter.addWidget(left_panel)
        
        # Panneau droit : détails et édition
        right_panel = self.create_details_panel()
        main_splitter.addWidget(right_panel)
        
        # Définir les proportions du splitter
        main_splitter.setSizes([300, 600])
        
        # Boutons de dialogue
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Appliquer")
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        close_button = QPushButton("Fermer")
        button_layout.addWidget(close_button)
        close_button.clicked.connect(self.accept)
        
        layout.addLayout(button_layout)
        
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        
        # Boutons principaux
        self.new_button = QPushButton("Nouveau")
        self.duplicate_button = QPushButton("Dupliquer")
        self.delete_button = QPushButton("Supprimer")
        
        layout.addWidget(self.new_button)
        layout.addWidget(self.duplicate_button)
        layout.addWidget(self.delete_button)
        
        layout.addWidget(QLabel("|"))  # Séparateur
        
        # Import/Export
        self.import_button = QPushButton("Importer...")
        self.export_button = QPushButton("Exporter...")
        
        layout.addWidget(self.import_button)
        layout.addWidget(self.export_button)
        
        layout.addStretch()
        
        # Filtre par catégorie
        layout.addWidget(QLabel("Catégorie:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("Toutes", None)
        for category in PresetCategory:
            self.category_filter.addItem(self.get_category_display_name(category), category)
        layout.addWidget(self.category_filter)
        
        return toolbar
        
    def create_preset_list_panel(self):
        """Crée le panneau de liste des presets"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Liste des presets avec colonnes
        self.preset_tree = QTreeWidget()
        self.preset_tree.setHeaderLabels(["Nom", "Catégorie", "Type", "Modifié"])
        self.preset_tree.setRootIsDecorated(True)
        self.preset_tree.setAlternatingRowColors(True)
        self.preset_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Ajuster la largeur des colonnes
        header = self.preset_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.preset_tree)
        
        return widget
        
    def create_details_panel(self):
        """Crée le panneau de détails et d'édition"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Onglets pour les différents aspects
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Onglet Général
        general_tab = self.create_general_tab()
        self.tabs.addTab(general_tab, "Général")
        
        # Onglet Paramètres
        parameters_tab = self.create_parameters_tab()
        self.tabs.addTab(parameters_tab, "Paramètres")
        
        # Onglet État Temporal
        temporal_tab = self.create_temporal_tab()
        self.tabs.addTab(temporal_tab, "État Temporal")
        
        return widget
        
    def create_general_tab(self):
        """Crée l'onglet général avec métadonnées"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Champs éditables
        self.name_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        self.category_combo = QComboBox()
        for category in PresetCategory:
            self.category_combo.addItem(self.get_category_display_name(category), category)
        
        # Champs en lecture seule
        self.id_label = QLabel()
        self.type_label = QLabel()
        self.author_label = QLabel()
        self.created_label = QLabel()
        self.modified_label = QLabel()
        
        layout.addRow("ID:", self.id_label)
        layout.addRow("Nom:", self.name_edit)
        layout.addRow("Description:", self.description_edit)
        layout.addRow("Catégorie:", self.category_combo)
        layout.addRow("Type:", self.type_label)
        layout.addRow("Auteur:", self.author_label)
        layout.addRow("Créé:", self.created_label)
        layout.addRow("Modifié:", self.modified_label)
        
        return widget
        
    def create_parameters_tab(self):
        """Crée l'onglet des paramètres physiques"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Paramètres de base du réacteur
        self.rod_position_spin = QDoubleSpinBox()
        self.rod_position_spin.setRange(0, 100)
        self.rod_position_spin.setSuffix(" %")
        self.rod_position_spin.setDecimals(1)
        
        self.boron_concentration_spin = QDoubleSpinBox()
        self.boron_concentration_spin.setRange(0, 5000)
        self.boron_concentration_spin.setSuffix(" ppm")
        self.boron_concentration_spin.setDecimals(0)
        
        self.moderator_temp_spin = QDoubleSpinBox()
        self.moderator_temp_spin.setRange(200, 400)
        self.moderator_temp_spin.setSuffix(" °C")
        self.moderator_temp_spin.setDecimals(1)
        
        self.fuel_enrichment_spin = QDoubleSpinBox()
        self.fuel_enrichment_spin.setRange(0.5, 20)
        self.fuel_enrichment_spin.setSuffix(" %")
        self.fuel_enrichment_spin.setDecimals(2)
        
        self.power_level_spin = QDoubleSpinBox()
        self.power_level_spin.setRange(0, 120)
        self.power_level_spin.setSuffix(" %")
        self.power_level_spin.setDecimals(1)
        
        layout.addRow("Position Barres de Contrôle:", self.rod_position_spin)
        layout.addRow("Concentration Bore:", self.boron_concentration_spin)
        layout.addRow("Température Modérateur:", self.moderator_temp_spin)
        layout.addRow("Enrichissement Combustible:", self.fuel_enrichment_spin)
        layout.addRow("Niveau de Puissance:", self.power_level_spin)
        
        return widget
        
    def create_temporal_tab(self):
        """Crée l'onglet pour l'état temporel"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Case à cocher pour activer l'état temporel
        self.temporal_enabled_check = QCheckBox("Inclure l'état temporel")
        layout.addRow(self.temporal_enabled_check)
        
        # Paramètres temporels
        self.simulation_time_spin = QDoubleSpinBox()
        self.simulation_time_spin.setRange(0, 1000000)
        self.simulation_time_spin.setSuffix(" h")
        self.simulation_time_spin.setDecimals(1)
        
        self.iodine_concentration_spin = QDoubleSpinBox()
        self.iodine_concentration_spin.setRange(0, 1e20)
        self.iodine_concentration_spin.setSuffix(" atomes/cm³")
        self.iodine_concentration_spin.setDecimals(2)
        
        self.xenon_concentration_spin = QDoubleSpinBox()
        self.xenon_concentration_spin.setRange(0, 1e20)
        self.xenon_concentration_spin.setSuffix(" atomes/cm³")
        self.xenon_concentration_spin.setDecimals(2)
        
        layout.addRow("Temps de Simulation:", self.simulation_time_spin)
        layout.addRow("Concentration I-135:", self.iodine_concentration_spin)
        layout.addRow("Concentration Xe-135:", self.xenon_concentration_spin)
        
        # Désactiver initialement
        self.temporal_enabled_check.toggled.connect(self.on_temporal_enabled_changed)
        self.on_temporal_enabled_changed(False)
        
        return widget
        
    def connect_signals(self):
        """Connecte tous les signaux"""
        # Toolbar
        self.new_button.clicked.connect(self.new_preset)
        self.duplicate_button.clicked.connect(self.duplicate_preset)
        self.delete_button.clicked.connect(self.delete_preset)
        self.import_button.clicked.connect(self.import_presets)
        self.export_button.clicked.connect(self.export_presets)
        self.category_filter.currentTextChanged.connect(self.filter_presets)
        
        # Liste des presets
        self.preset_tree.currentItemChanged.connect(self.on_preset_selection_changed)
        
        # Boutons du dialog
        self.apply_button.clicked.connect(self.apply_preset)
        
        # Champs d'édition - surveiller les changements
        self.name_edit.textChanged.connect(self.on_preset_modified)
        self.description_edit.textChanged.connect(self.on_preset_modified)
        self.category_combo.currentTextChanged.connect(self.on_preset_modified)
        
        # Paramètres physiques
        self.rod_position_spin.valueChanged.connect(self.on_preset_modified)
        self.boron_concentration_spin.valueChanged.connect(self.on_preset_modified)
        self.moderator_temp_spin.valueChanged.connect(self.on_preset_modified)
        self.fuel_enrichment_spin.valueChanged.connect(self.on_preset_modified)
        self.power_level_spin.valueChanged.connect(self.on_preset_modified)
        
        # Paramètres temporels
        self.temporal_enabled_check.toggled.connect(self.on_preset_modified)
        self.simulation_time_spin.valueChanged.connect(self.on_preset_modified)
        self.iodine_concentration_spin.valueChanged.connect(self.on_preset_modified)
        self.xenon_concentration_spin.valueChanged.connect(self.on_preset_modified)
        
    def load_presets(self):
        """Charge tous les presets dans l'arbre"""
        self.preset_tree.clear()
        
        # Créer des groupes par catégorie
        category_items = {}
        for category in PresetCategory:
            parent_item = QTreeWidgetItem([self.get_category_display_name(category)])
            parent_item.setData(0, Qt.ItemDataRole.UserRole, ("category", category))
            font = QFont()
            font.setBold(True)
            parent_item.setFont(0, font)
            self.preset_tree.addTopLevelItem(parent_item)
            category_items[category] = parent_item
        
        # Ajouter les presets
        for preset in self.preset_manager.get_all_presets().values():
            parent = category_items[preset.category]
            item = QTreeWidgetItem([
                preset.name,
                self.get_category_display_name(preset.category),
                "Système" if preset.preset_type == PresetType.SYSTEME else "Utilisateur",
                preset.modified_date.strftime("%d/%m/%Y %H:%M")
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, ("preset", preset))
            parent.addChild(item)
        
        # Ajouter l'état actuel comme pseudo-preset
        current_item = QTreeWidgetItem([
            "État Actuel",
            self.get_category_display_name(self.current_state_preset.category),
            "Temporaire",
            "Maintenant"
        ])
        current_item.setData(0, Qt.ItemDataRole.UserRole, ("current", self.current_state_preset))
        
        # Ajouter à la catégorie appropriée
        parent = category_items[self.current_state_preset.category]
        parent.insertChild(0, current_item)  # En première position
        
        # Développer tous les groupes
        self.preset_tree.expandAll()
        
    def filter_presets(self):
        """Filtre les presets par catégorie"""
        selected_category = self.category_filter.currentData()
        
        for i in range(self.preset_tree.topLevelItemCount()):
            category_item = self.preset_tree.topLevelItem(i)
            category_data = category_item.data(0, Qt.ItemDataRole.UserRole)
            
            if category_data and category_data[0] == "category":
                category = category_data[1]
                # Afficher/masquer selon le filtre
                category_item.setHidden(selected_category is not None and selected_category != category)
        
    def on_preset_selection_changed(self, current, previous):
        """Gère le changement de sélection de preset"""
        if current is None:
            self.clear_details()
            return
            
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] not in ("preset", "current"):
            self.clear_details()
            return
            
        preset = data[1]
        self.current_preset_item = current
        self.load_preset_details(preset)
        
        # Activer/désactiver les boutons selon le type
        is_user_preset = (data[0] == "preset" and preset.preset_type == PresetType.UTILISATEUR)
        is_current = (data[0] == "current")
        
        self.duplicate_button.setEnabled(True)
        self.delete_button.setEnabled(is_user_preset)
        self.apply_button.setEnabled(not is_current)
        
        # Activer/désactiver l'édition
        editable = is_user_preset
        self.name_edit.setEnabled(editable)
        self.description_edit.setEnabled(editable)
        self.category_combo.setEnabled(editable)
        self.enable_parameter_editing(editable)
        
    def load_preset_details(self, preset: PresetData):
        """Charge les détails d'un preset dans les champs"""
        # Général
        self.id_label.setText(preset.id)
        self.name_edit.setText(preset.name)
        self.description_edit.setPlainText(preset.description)
        
        # Sélectionner la bonne catégorie
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == preset.category:
                self.category_combo.setCurrentIndex(i)
                break
        
        self.type_label.setText("Système" if preset.preset_type == PresetType.SYSTEME else "Utilisateur")
        self.author_label.setText(preset.author)
        self.created_label.setText(preset.created_date.strftime("%d/%m/%Y %H:%M:%S"))
        self.modified_label.setText(preset.modified_date.strftime("%d/%m/%Y %H:%M:%S"))
        
        # Paramètres physiques
        self.rod_position_spin.setValue(preset.control_rod_position)
        self.boron_concentration_spin.setValue(preset.boron_concentration)
        self.moderator_temp_spin.setValue(preset.moderator_temperature)
        self.fuel_enrichment_spin.setValue(preset.fuel_enrichment)
        self.power_level_spin.setValue(preset.power_level)
        
        # État temporel
        has_temporal = (preset.simulation_time is not None or 
                       preset.iodine_concentration is not None or 
                       preset.xenon_concentration is not None)
        
        self.temporal_enabled_check.setChecked(has_temporal)
        
        if has_temporal:
            self.simulation_time_spin.setValue(preset.simulation_time or 0)
            self.iodine_concentration_spin.setValue(preset.iodine_concentration or 0)
            self.xenon_concentration_spin.setValue(preset.xenon_concentration or 0)
        else:
            self.simulation_time_spin.setValue(0)
            self.iodine_concentration_spin.setValue(0)
            self.xenon_concentration_spin.setValue(0)
            
    def clear_details(self):
        """Efface tous les champs de détail"""
        self.id_label.setText("")
        self.name_edit.setText("")
        self.description_edit.setPlainText("")
        self.type_label.setText("")
        self.author_label.setText("")
        self.created_label.setText("")
        self.modified_label.setText("")
        
        self.duplicate_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        
    def enable_parameter_editing(self, enabled: bool):
        """Active/désactive l'édition des paramètres"""
        self.rod_position_spin.setEnabled(enabled)
        self.boron_concentration_spin.setEnabled(enabled)
        self.moderator_temp_spin.setEnabled(enabled)
        self.fuel_enrichment_spin.setEnabled(enabled)
        self.power_level_spin.setEnabled(enabled)
        self.temporal_enabled_check.setEnabled(enabled)
        self.on_temporal_enabled_changed(self.temporal_enabled_check.isChecked() and enabled)
        
    def on_temporal_enabled_changed(self, enabled: bool):
        """Gère l'activation/désactivation de l'état temporel"""
        self.simulation_time_spin.setEnabled(enabled)
        self.iodine_concentration_spin.setEnabled(enabled)
        self.xenon_concentration_spin.setEnabled(enabled)
        
    def on_preset_modified(self):
        """Appelé quand un preset est modifié"""
        # Ici on pourrait ajouter un indicateur visuel de modification
        pass
        
    def get_category_display_name(self, category: PresetCategory) -> str:
        """Retourne le nom d'affichage d'une catégorie"""
        names = {
            PresetCategory.BASE: "Configuration de Base",
            PresetCategory.TEMPOREL: "Simulation Temporelle",
            PresetCategory.AVANCE: "Paramètres Avancés",
            PresetCategory.PERSONNALISE: "Personnalisé"
        }
        return names.get(category, category.value)
        
    def new_preset(self):
        """Crée un nouveau preset basé sur l'état actuel"""
        try:
            # Demander le nom
            name, ok = self.get_text_input("Nouveau Preset", "Nom du nouveau preset:")
            if not ok or not name.strip():
                return
                
            # Créer le preset avec les paramètres actuels
            parameters = self.current_state_preset.get_basic_parameters()
            if self.temporal_enabled_check.isChecked():
                parameters.update({
                    "simulation_time": self.current_state_preset.simulation_time,
                    "iodine_concentration": self.current_state_preset.iodine_concentration,
                    "xenon_concentration": self.current_state_preset.xenon_concentration
                })
            
            preset = self.preset_manager.create_preset(
                name=name.strip(),
                description=f"Preset créé depuis l'état actuel",
                parameters=parameters,
                category=PresetCategory.PERSONNALISE
            )
            
            if preset:
                self.load_presets()
                QMessageBox.information(self, "Succès", f"Preset '{name}' créé avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", f"Un preset avec le nom '{name}' existe déjà.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")
            
    def duplicate_preset(self):
        """Duplique le preset sélectionné"""
        if not self.current_preset_item:
            return
            
        data = self.current_preset_item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        source_preset = data[1]
        
        try:
            # Demander le nom pour la copie
            name, ok = self.get_text_input("Dupliquer Preset", 
                                         f"Nom pour la copie de '{source_preset.name}':",
                                         f"{source_preset.name} (Copie)")
            if not ok or not name.strip():
                return
                
            # Préparer les paramètres
            parameters = source_preset.get_basic_parameters()
            if (source_preset.simulation_time is not None or 
                source_preset.iodine_concentration is not None or
                source_preset.xenon_concentration is not None):
                parameters.update({
                    "simulation_time": source_preset.simulation_time,
                    "iodine_concentration": source_preset.iodine_concentration,
                    "xenon_concentration": source_preset.xenon_concentration
                })
            
            preset = self.preset_manager.create_preset(
                name=name.strip(),
                description=f"Copie de '{source_preset.name}': {source_preset.description}",
                parameters=parameters,
                category=source_preset.category if source_preset.category != PresetCategory.BASE else PresetCategory.PERSONNALISE
            )
            
            if preset:
                self.load_presets()
                QMessageBox.information(self, "Succès", f"Preset '{name}' dupliqué avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", f"Un preset avec le nom '{name}' existe déjà.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la duplication: {str(e)}")
            
    def delete_preset(self):
        """Supprime le preset sélectionné"""
        if not self.current_preset_item:
            return
            
        data = self.current_preset_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "preset":
            return
            
        preset = data[1]
        
        if preset.preset_type == PresetType.SYSTEME:
            QMessageBox.warning(self, "Erreur", "Impossible de supprimer un preset système.")
            return
            
        # Confirmation
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le preset '{preset.name}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.preset_manager.delete_preset(preset.id):
                    self.load_presets()
                    QMessageBox.information(self, "Succès", f"Preset '{preset.name}' supprimé.")
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de supprimer le preset.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
                
    def import_presets(self):
        """Importe des presets depuis un fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer des presets", "", 
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        
        if not file_path:
            return
            
        try:
            imported_ids = self.preset_manager.import_presets(file_path, overwrite=False)
            if imported_ids:
                self.load_presets()
                QMessageBox.information(
                    self, "Succès", 
                    f"{len(imported_ids)} preset(s) importé(s) avec succès."
                )
            else:
                QMessageBox.information(self, "Information", "Aucun nouveau preset à importer.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import: {str(e)}")
            
    def export_presets(self):
        """Exporte les presets sélectionnés"""
        # Pour simplifier, on exporte tous les presets utilisateur
        user_presets = [
            preset.id for preset in self.preset_manager.get_all_presets().values()
            if preset.preset_type == PresetType.UTILISATEUR
        ]
        
        if not user_presets:
            QMessageBox.information(self, "Information", "Aucun preset utilisateur à exporter.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter des presets", 
            f"presets_neutroscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        
        if not file_path:
            return
            
        try:
            if self.preset_manager.export_presets(file_path, user_presets):
                QMessageBox.information(
                    self, "Succès",
                    f"{len(user_presets)} preset(s) exporté(s) vers:\n{file_path}"
                )
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de l'export.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")
            
    def apply_preset(self):
        """Applique le preset sélectionné"""
        if not self.current_preset_item:
            return
            
        data = self.current_preset_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "preset":
            return
            
        preset = data[1]
        self.preset_applied.emit(preset.name)
        QMessageBox.information(self, "Succès", f"Preset '{preset.name}' appliqué.")
        
    def get_text_input(self, title: str, label: str, default_text: str = "") -> tuple:
        """Affiche un dialog de saisie de texte"""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(self, title, label, text=default_text)
        return text, ok 