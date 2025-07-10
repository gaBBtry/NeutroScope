# Architecture de NeutroScope - Configuration Centralisée et Interface Abstraite

Ce document décrit l'architecture logicielle finalisée de l'application NeutroScope, après la centralisation complète de la configuration et l'implémentation d'une interface abstraite préparant l'intégration future d'OpenMC.

## Vue d'ensemble : Architecture MVC Centralisée et Découplée

Le projet suit une architecture **Modèle-Vue-Contrôleur (MVC) Renforcée** qui a été optimisée pour garantir la **centralisation de configuration** et la **flexibilité des modèles physiques**. Cette évolution architecturale prépare NeutroScope pour des intégrations futures majeures.

**ARCHITECTURE FINALISÉE** : L'architecture a été renforcée pour supporter :
- **Configuration 100% centralisée** dans `config.json` comme source unique de vérité
- **Interface abstraite** pour les modèles physiques permettant l'intégration d'OpenMC
- **Architecture découplée** avec séparation claire des responsabilités
- **Système de tests robuste** validant l'intégrité de l'architecture

-   **Modèle (`src/model/`)**: Contient la logique de simulation physique avec interface abstraite, configuration centralisée et système de presets professionnel
-   **Vue (`src/gui/`)**: Interface utilisateur maintenue avec widgets spécialisés et système d'information contextuel complet
-   **Contrôleur (`src/controller/`)**: Orchestration des interactions modèle-vue avec accès centralisé à la configuration

## Structure du Projet Finalisée

```
NeutroScope/ (Architecture Centralisée et Future-Ready)
├── src/
│   ├── model/                      # MODÈLE (Physique + Interface Abstraite)
│   │   ├── reactor_model.py        # ✅ ADAPTÉ - Configuration centralisée
│   │   ├── abstract_reactor_model.py # 🚀 NOUVEAU - Interface pour OpenMC
│   │   ├── config.py               # 🚀 SIMPLIFIÉ - Fonctions de chargement
│   │   └── preset_model.py         # ✅ Système presets avec config centralisée
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration centralisée)
│   │   └── reactor_controller.py   # ✅ ADAPTÉ - Configuration centralisée
│   │
│   └── gui/                        # VUE (Interface maintenue)
│       ├── main_window.py          # ✅ Interface opérationnelle
│       ├── visualization.py        # ✅ Gestionnaire visualisations
│       └── widgets/                # ✅ Écosystème widgets complets
│           ├── realtime_simulation.py        # ✅ Simulation temps réel
│           ├── xenon_plot.py                 # ✅ Visualisation Xénon
│           ├── neutron_cycle_plot.py         # ✅ Cycle neutronique
│           ├── flux_plot.py                  # ✅ Distribution axiale
│           ├── four_factors_plot.py          # ✅ Facteurs neutroniques
│           ├── neutron_balance_plot.py       # ✅ Bilan neutronique
│           ├── enhanced_widgets.py           # ✅ Widgets informatifs
│           ├── info_manager.py               # ✅ Système information
│           ├── info_panel.py                 # ✅ Panneau information
│           ├── info_dialog.py                # ✅ Dialog information
│           └── credits_button.py             # ✅ Bouton crédits
│
├── tests/                          # ✅ Tests adaptés nouvelle architecture
├── docs/                           # ✅ Documentation architecture
│   ├── adr/                        # Architecture Decision Records
│   ├── architecture.md             # Ce fichier
│   ├── BUILD_WINDOWS.md            # Documentation déploiement
│   └── deployment.md               # Stratégie déploiement
├── config.json                     # 🚀 SOURCE UNIQUE DE VÉRITÉ
├── user_presets.json               # ✅ Presets utilisateur
├── requirements.txt                # ✅ Dépendances Python
├── build_windows.py                # ✅ Script build optimisé
└── main.py                         # ✅ Point d'entrée corrigé
```

---
## 1. Le Modèle (`src/model/`) - Configuration Centralisée et Interface Abstraite

Le cœur de la simulation a été **restructuré** pour assurer la centralisation de configuration et préparer l'intégration d'OpenMC.

### **`config.py`** - Configuration Centralisée Révolutionnée 🚀
**TRANSFORMATION MAJEURE** : Passage d'un système dupliqué à un chargement centralisé :

#### **Ancien Système (Problématique)**
- **Duplication massive** : ~70 variables Python redondantes avec `config.json`
- **Risque d'incohérence** : Possibilité de désynchronisation entre sources
- **Maintenance complexe** : Modifications requises en multiple endroits

#### **Nouveau Système (Solution)**
```python
def get_config():
    """Retourne la configuration complète depuis config.json"""
    return _config  # Chargé une seule fois au démarrage

# Fonctions helpers spécialisées
def get_physical_constants():
    return _config.get("physical_constants", {})

def get_four_factors():
    return _config.get("four_factors", {})

def get_control_rod_groups():
    return _config.get("control_rod_groups", {})
```

#### **Avantages de la Centralisation**
- **Source unique de vérité** : `config.json` est l'unique référence
- **Cohérence garantie** : Plus de risque de désynchronisation
- **Maintenance simplifiée** : Une seule modification pour tous les composants
- **Gestion d'erreurs robuste** : Validation centralisée avec messages clairs

### **`abstract_reactor_model.py`** - Interface pour OpenMC 🚀
**NOUVEAU MODULE CRITIQUE** : Définit le contrat que tout modèle physique doit respecter :

#### **Interface Complète Définie**
```python
class AbstractReactorModel(ABC):
    # Méthodes de contrôle des paramètres
    @abstractmethod
    def set_target_rod_group_R_position(self, position: float) -> None: pass
    
    @abstractmethod
    def set_target_rod_group_GCP_position(self, position: float) -> None: pass
    
    # Méthodes de récupération des paramètres calculés
    @abstractmethod
    def get_reactor_parameters(self) -> Dict[str, float]: pass
    
    # Méthodes de visualisation
    @abstractmethod
    def get_axial_flux_distribution(self) -> Tuple[Any, Any]: pass
    
    # Méthodes de gestion des presets
    @abstractmethod
    def apply_preset(self, preset_name: str) -> bool: pass
    
    # ... 21 méthodes abstraites au total
```

#### **Bénéfices de l'Interface Abstraite**
- **Interchangeabilité** : Remplacement facile du modèle physique par OpenMC
- **Contrat défini** : Interface claire pour tous les développeurs
- **Tests robustes** : Validation du comportement attendu
- **Évolutivité** : Ajout facile de nouvelles implémentations

### **`reactor_model.py`** - Implémentation Adaptée ✅
**ADAPTATION COMPLÈTE** : Le modèle existant a été adapté pour l'architecture centralisée :

#### **Configuration Centralisée Intégrée**
```python
class ReactorModel(AbstractReactorModel):
    def __init__(self):
        # Chargement centralisé unique
        self.config = get_config()
        
        # Toutes les constantes depuis la config centralisée
        self.delayed_neutron_fraction = self.config['physical_constants']['DELAYED_NEUTRON_FRACTION']
        # ... autres initialisations depuis config
```

#### **Accès Configuration Dynamique**
- **~50+ références mises à jour** : De `config.VARIABLE` vers `self.config['section']['key']`
- **Méthodes adaptées** : Tous les calculs physiques utilisent la source centralisée
- **Cohérence maintenue** : Comportement physique identique avec architecture améliorée

### **`preset_model.py`** - Système Presets Centralisé ✅
**MAINTENU ET ADAPTÉ** : Le système de presets utilise maintenant la configuration centralisée :

#### **Intégration Configuration Centralisée**
```python
def _load_system_presets(self):
    """Charge les presets système depuis config.json"""
    from .config import get_config
    config = get_config()
    system_presets = config.get('presets', {})
    # ... traitement des presets
```

## 2. Le Contrôleur (`src/controller/`) - Orchestration Centralisée

Le contrôleur a été **adapté** pour utiliser la configuration centralisée tout en maintenant ses responsabilités.

### **`reactor_controller.py`** - Configuration Centralisée Intégrée ✅
**ADAPTATION RÉUSSIE** : Le contrôleur accède maintenant à la configuration centralisée :

#### **Chargement Configuration Centralisé**
```python
class ReactorController:
    def __init__(self, model_class: Type[AbstractReactorModel] = ReactorModel):
        self.config = get_config()  # Accès centralisé
        self.model = model_class()
```

#### **Méthodes Adaptées**
- **Interface abstraite** : Le contrôleur fonctionne avec n'importe quelle implémentation
- **Configuration centralisée** : Accès aux paramètres via `self.config`
- **Rétrocompatibilité** : Toutes les méthodes existantes maintenues

## 3. La Vue (`src/gui/`) - Interface Maintenue et Opérationnelle

L'interface utilisateur a été **maintenue** sans changements majeurs, conservant sa fonctionnalité complète.

### **Architecture Interface Préservée**
- **`main_window.py`** : Interface principale opérationnelle
- **`visualization.py`** : Gestionnaire de visualisations maintenu
- **`widgets/`** : Écosystème complet de widgets préservé

#### **Fonctionnalités Maintenues**
- **Simulation temps réel** : Moteur de simulation opérationnel
- **Visualisations** : Tous les graphiques et widgets fonctionnels
- **Système d'information** : Info-bulles et panneaux contextuels complets

## Flux de Données Optimisé

### **Configuration Centralisée**
1. **Chargement unique** : `config.json` lu une seule fois au démarrage
2. **Distribution** : Configuration accessible via `get_config()` dans tous les modules
3. **Cohérence** : Source unique garantit la synchronisation

### **Interface Abstraite**
1. **Contrôleur** → **Interface** : Le contrôleur utilise l'interface abstraite
2. **Implémentation** → **Interface** : ReactorModel implémente l'interface
3. **Extensibilité** : OpenMC peut remplacer ReactorModel sans changer le contrôleur

## Principes Architecturaux Renforcés

### **Nouveaux Principes de Centralisation**
1. **Source Unique de Vérité** : `config.json` est l'unique référence pour tous les paramètres
2. **Découplage par Interface** : Interface abstraite sépare définition et implémentation
3. **Configuration Dynamique** : Accès en runtime plutôt que constants compilées
4. **Validation Centralisée** : Contrôles de cohérence unifiés

### **Principes MVC Renforcés**
1. **Séparation Stricte** : Responsabilités clairement définies et respectées
2. **Interface Abstraite** : Modèle découplé du contrôleur via interface
3. **Configuration Externalisée** : Paramètres séparés du code logique
4. **Tests Robustes** : Validation de l'architecture et du comportement

## État des Tests et Validation

### **Tests Adaptés et Validés** ✅
Tous les tests ont été mis à jour pour la nouvelle architecture :

#### **Tests Unitaires**
- `test_reactor_model.py` : Adaptation à la configuration centralisée
- `test_reactor_controller.py` : Validation de l'interface abstraite
- **Corrections** : Méthodes obsolètes remplacées, nouveaux patterns validés

#### **Tests d'Intégration**
- `test_integration.py` : Validation complète de l'architecture MVC
- **Validation fonctionnelle** : Tous les flux de données testés et validés

### **Validation Opérationnelle Confirmée** ✅
```
Application Status:
  - Model initialization: ✓
  - Configuration loaded: ✓
  - Presets available: 4
  - Interface abstract: ✓
```

## Impact Architectural et Bénéfices

### **Architecture Renforcée** 🚀
- **Robustesse** : Configuration centralisée élimine les incohérences
- **Flexibilité** : Interface abstraite permet l'échange de modèles physiques
- **Maintenabilité** : Code simplifié et responsabilités claires
- **Évolutivité** : Base solide pour intégrations futures

### **Préparation OpenMC Complète** 🎯
- **Interface définie** : Contrat clair pour l'implémentation OpenMC
- **Configuration découplée** : Paramètres externalisés et modifiables
- **Tests en place** : Validation automatique du comportement attendu
- **Architecture prouvée** : Système testé et opérationnel

### **Code Optimisé** ✅
- **Réduction de complexité** : ~100 lignes de duplication supprimées
- **Lisibilité améliorée** : Accès explicite via configuration centralisée
- **Performance maintenue** : Aucun impact sur les performances
- **Sécurité renforcée** : Validation centralisée et gestion d'erreurs

## Conclusion Architecturale

### **Mission Accomplie** 🎯
L'architecture de NeutroScope a été **finalisée avec succès** :
- **Configuration 100% centralisée** dans `config.json`
- **Interface abstraite** prête pour OpenMC
- **Tests validés** et application opérationnelle
- **Code optimisé** et maintenable

### **Architecture Future-Ready** 🚀
NeutroScope dispose maintenant d'une architecture :
- **Découplée** : Interface abstraite pour flexibilité maximale
- **Centralisée** : Configuration unique et cohérente
- **Testée** : Suite de validation complète et robuste
- **Évolutive** : Base solide pour OpenMC et futures innovations

### **Nouvelle Référence Établie**
Cette architecture constitue maintenant :
- **Standard d'excellence** : Référence pour applications éducatives robustes
- **Base évolutive** : Fondation solide pour intégrations avancées
- **Modèle architectural** : Exemple de centralisation et découplage réussis
- **Préparation industrielle** : Architecture prête pour outils de simulation professionnels

**CONCLUSION ARCHITECTURALE** : L'architecture de NeutroScope a été **transformée avec succès** pour créer un système robuste, centralisé et évolutif. Cette finalisation établit une base technique solide pour l'intégration future d'OpenMC et autres évolutions majeures, tout en maintenant la simplicité et la fiabilité du système existant. 