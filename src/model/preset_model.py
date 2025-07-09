"""
Modèle avancé pour la gestion des presets de réacteur avec métadonnées et validation
"""
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum

class PresetCategory(Enum):
    """Catégories de presets pour l'organisation"""
    BASE = "base"
    TEMPOREL = "temporel"
    AVANCE = "avance"
    PERSONNALISE = "personnalise"

class PresetType(Enum):
    """Types de presets selon leur source"""
    SYSTEME = "systeme"  # Presets intégrés non modifiables
    UTILISATEUR = "utilisateur"  # Presets créés par l'utilisateur

@dataclass
class PresetData:
    """Structure de données pour un preset avec métadonnées complètes"""
    # Identification
    id: str
    name: str
    description: str
    category: PresetCategory
    preset_type: PresetType
    
    # Métadonnées
    created_date: datetime
    modified_date: datetime
    author: str = "Système"
    version: str = "1.0"
    tags: List[str] = None
    
    # Paramètres de base du réacteur
    control_rod_position: float = 0.0  # 0-100%
    boron_concentration: float = 500.0  # ppm
    average_temperature: float = 310.0  # °C
    fuel_enrichment: float = 3.5  # %
    power_level: float = 100.0  # %
    
    # États temporels avancés (pour la dynamique Xénon)
    iodine_concentration: Optional[float] = None  # atomes/cm³
    xenon_concentration: Optional[float] = None   # atomes/cm³
    simulation_time: Optional[float] = None       # secondes
    
    # Paramètres physiques avancés (optionnels)
    fuel_temperature: Optional[float] = None      # °C
    additional_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialisation après création"""
        if self.tags is None:
            self.tags = []
        if self.additional_parameters is None:
            self.additional_parameters = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour la sérialisation"""
        result = asdict(self)
        # Convertir les enums en strings
        result['category'] = self.category.value
        result['preset_type'] = self.preset_type.value
        # Convertir les dates en ISO format
        result['created_date'] = self.created_date.isoformat()
        result['modified_date'] = self.modified_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresetData':
        """Crée un PresetData depuis un dictionnaire"""
        # Convertir les strings en enums
        data['category'] = PresetCategory(data['category'])
        data['preset_type'] = PresetType(data['preset_type'])
        # Convertir les dates ISO en datetime
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Valide les données du preset et retourne les erreurs"""
        errors = []
        
        # Validation des paramètres de base
        if not (0 <= self.control_rod_position <= 100):
            errors.append("Position barres de contrôle doit être entre 0 et 100%")
        
        if not (0 <= self.boron_concentration <= 5000):
            errors.append("Concentration bore doit être entre 0 et 5000 ppm")
        
        if not (200 <= self.average_temperature <= 400):
            errors.append("Température moyenne doit être entre 200 et 400°C")
        
        if not (0.5 <= self.fuel_enrichment <= 20):
            errors.append("Enrichissement combustible doit être entre 0.5 et 20%")
        
        if not (0 <= self.power_level <= 120):
            errors.append("Niveau de puissance doit être entre 0 et 120%")
        
        # Validation des concentrations Xénon si présentes
        if self.iodine_concentration is not None and self.iodine_concentration < 0:
            errors.append("Concentration Iode-135 ne peut pas être négative")
        
        if self.xenon_concentration is not None and self.xenon_concentration < 0:
            errors.append("Concentration Xénon-135 ne peut pas être négative")
        
        # Validation cohérence temporelle
        if self.simulation_time is not None and self.simulation_time < 0:
            errors.append("Temps de simulation ne peut pas être négatif")
        
        # Validation métadonnées
        if not self.name.strip():
            errors.append("Le nom du preset ne peut pas être vide")
        
        if len(self.name) > 50:
            errors.append("Le nom du preset ne peut pas dépasser 50 caractères")
        
        return errors
    
    def get_basic_parameters(self) -> Dict[str, float]:
        """Retourne les paramètres de base compatibles avec l'ancien système"""
        return {
            "control_rod_position": self.control_rod_position,
            "boron_concentration": self.boron_concentration,
            "average_temperature": self.average_temperature,
            "fuel_enrichment": self.fuel_enrichment,
            "power_level": self.power_level
        }

class PresetManager:
    """Gestionnaire avancé des presets avec persistence et validation"""
    
    def __init__(self, system_presets_file: str = "config.json", 
                 user_presets_file: str = "user_presets.json"):
        self.system_presets_file = Path(system_presets_file)
        self.user_presets_file = Path(user_presets_file)
        self._presets: Dict[str, PresetData] = {}
        self._load_all_presets()
    
    def _load_all_presets(self):
        """Charge tous les presets (système + utilisateur)"""
        self._load_system_presets()
        self._load_user_presets()
    
    def _load_system_presets(self):
        """Charge les presets système depuis config.json"""
        try:
            with open(self.system_presets_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            system_presets = config.get('presets', {})
            now = datetime.now()
            
            for name, params in system_presets.items():
                preset = PresetData(
                    id=f"system_{name.lower().replace(' ', '_')}",
                    name=name,
                    description=self._get_preset_description(name),
                    category=self._get_preset_category(name),
                    preset_type=PresetType.SYSTEME,
                    created_date=now,
                    modified_date=now,
                    author="NeutroScope",
                    **params
                )
                self._presets[preset.id] = preset
                
        except FileNotFoundError:
            print(f"Fichier de presets système non trouvé: {self.system_presets_file}")
        except json.JSONDecodeError as e:
            print(f"Erreur de lecture des presets système: {e}")
    
    def _load_user_presets(self):
        """Charge les presets utilisateur depuis user_presets.json"""
        if not self.user_presets_file.exists():
            return
        
        try:
            with open(self.user_presets_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            for preset_data in user_data.get('presets', []):
                preset = PresetData.from_dict(preset_data)
                self._presets[preset.id] = preset
                
        except json.JSONDecodeError as e:
            print(f"Erreur de lecture des presets utilisateur: {e}")
    
    def _save_user_presets(self):
        """Sauvegarde les presets utilisateur"""
        user_presets = [
            preset.to_dict() 
            for preset in self._presets.values() 
            if preset.preset_type == PresetType.UTILISATEUR
        ]
        
        user_data = {
            "version": "1.0",
            "created_date": datetime.now().isoformat(),
            "presets": user_presets
        }
        
        try:
            # Créer le répertoire si nécessaire
            self.user_presets_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.user_presets_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur de sauvegarde des presets utilisateur: {e}")
    
    def _get_preset_description(self, name: str) -> str:
        """Génère une description basée sur le nom du preset"""
        descriptions = {
            "Démarrage": "Configuration typique pour le démarrage d'un réacteur avec barres partiellement retirées",
            "Critique à puissance nominale": "État d'équilibre critique à puissance nominale de fonctionnement",
            "Fin de cycle": "Configuration en fin de cycle avec combustible appauvri et faible bore",
            "Surcritique": "État surcritique démontrant une augmentation de puissance",
            "Sous-critique": "État sous-critique démontrant une diminution de puissance",
            "Fonctionnement Xénon équilibre": "Fonctionnement stable avec Xénon-135 à l'équilibre",
            "Post-arrêt pic Xénon": "Situation après arrêt montrant le pic d'empoisonnement Xénon"
        }
        return descriptions.get(name, f"Preset personnalisé: {name}")
    
    def _get_preset_category(self, name: str) -> PresetCategory:
        """Détermine la catégorie d'un preset basé sur son nom"""
        temporal_presets = ["Fonctionnement Xénon équilibre", "Post-arrêt pic Xénon"]
        
        if name in temporal_presets:
            return PresetCategory.TEMPOREL
        else:
            return PresetCategory.BASE
    
    def get_all_presets(self) -> Dict[str, PresetData]:
        """Retourne tous les presets"""
        return self._presets.copy()
    
    def get_presets_by_category(self, category: PresetCategory) -> Dict[str, PresetData]:
        """Retourne les presets d'une catégorie donnée"""
        return {
            id: preset for id, preset in self._presets.items()
            if preset.category == category
        }
    
    def get_preset_names(self) -> List[str]:
        """Retourne la liste des noms de presets pour compatibilité"""
        return [preset.name for preset in self._presets.values()]
    
    def get_preset_by_name(self, name: str) -> Optional[PresetData]:
        """Trouve un preset par son nom"""
        for preset in self._presets.values():
            if preset.name == name:
                return preset
        return None
    
    def get_preset_by_id(self, preset_id: str) -> Optional[PresetData]:
        """Retourne un preset par son ID"""
        return self._presets.get(preset_id)
    
    def create_preset(self, name: str, description: str, parameters: Dict[str, Any],
                     category: PresetCategory = PresetCategory.PERSONNALISE,
                     tags: List[str] = None) -> Optional[PresetData]:
        """Crée un nouveau preset utilisateur"""
        # Générer un ID unique
        preset_id = f"user_{name.lower().replace(' ', '_').replace('é', 'e').replace('è', 'e')}"
        
        # Vérifier que le nom n'existe pas déjà
        if self.get_preset_by_name(name):
            return None
        
        now = datetime.now()
        preset = PresetData(
            id=preset_id,
            name=name,
            description=description,
            category=category,
            preset_type=PresetType.UTILISATEUR,
            created_date=now,
            modified_date=now,
            author="Utilisateur",
            tags=tags or [],
            **parameters
        )
        
        # Valider le preset
        errors = preset.validate()
        if errors:
            raise ValueError(f"Preset invalide: {', '.join(errors)}")
        
        self._presets[preset_id] = preset
        self._save_user_presets()
        return preset
    
    def update_preset(self, preset_id: str, **updates) -> bool:
        """Met à jour un preset existant"""
        preset = self._presets.get(preset_id)
        if not preset or preset.preset_type == PresetType.SYSTEME:
            return False
        
        # Appliquer les mises à jour
        for key, value in updates.items():
            if hasattr(preset, key):
                setattr(preset, key, value)
        
        preset.modified_date = datetime.now()
        
        # Valider après mise à jour
        errors = preset.validate()
        if errors:
            raise ValueError(f"Mise à jour invalide: {', '.join(errors)}")
        
        self._save_user_presets()
        return True
    
    def delete_preset(self, preset_id: str) -> bool:
        """Supprime un preset utilisateur"""
        preset = self._presets.get(preset_id)
        if not preset or preset.preset_type == PresetType.SYSTEME:
            return False
        
        del self._presets[preset_id]
        self._save_user_presets()
        return True
    
    def export_presets(self, file_path: str, preset_ids: List[str] = None) -> bool:
        """Exporte des presets vers un fichier"""
        try:
            if preset_ids is None:
                presets_to_export = list(self._presets.values())
            else:
                presets_to_export = [
                    self._presets[id] for id in preset_ids 
                    if id in self._presets
                ]
            
            export_data = {
                "version": "1.0",
                "export_date": datetime.now().isoformat(),
                "presets": [preset.to_dict() for preset in presets_to_export]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur d'export: {e}")
            return False
    
    def import_presets(self, file_path: str, overwrite: bool = False) -> List[str]:
        """Importe des presets depuis un fichier"""
        imported_ids = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            for preset_data in import_data.get('presets', []):
                preset = PresetData.from_dict(preset_data)
                
                # Vérifier si le preset existe déjà
                if preset.id in self._presets and not overwrite:
                    continue
                
                # Changer le type en utilisateur lors de l'import
                preset.preset_type = PresetType.UTILISATEUR
                preset.modified_date = datetime.now()
                
                # Valider avant import
                errors = preset.validate()
                if not errors:
                    self._presets[preset.id] = preset
                    imported_ids.append(preset.id)
            
            if imported_ids:
                self._save_user_presets()
            
        except Exception as e:
            print(f"Erreur d'import: {e}")
        
        return imported_ids 