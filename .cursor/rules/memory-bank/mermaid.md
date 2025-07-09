# Diagrammes Architecturaux NeutroScope

Ce fichier contient les diagrammes Mermaid essentiels pour comprendre l'architecture et le fonctionnement de NeutroScope.

## 1. Architecture MVC Globale

```mermaid
graph TB
    subgraph "Vue (GUI)"
        MW[MainWindow]
        VP[VisualizationPanel]
        W[Widgets]
        MW --> VP
        MW --> W
    end
    
    subgraph "Contrôleur"
        RC[ReactorController]
    end
    
    subgraph "Modèle"
        RM[ReactorModel]
        PM[PresetManager]
        CFG[Config]
        RM --> PM
        RM --> CFG
    end
    
    MW --> RC
    RC --> RM
    
    style MW fill:#e3f2fd
    style RC fill:#fff3e0
    style RM fill:#e8f5e8
```

## 2. Structure Détaillée des Composants

```mermaid
graph TB
    subgraph "src/gui/ (Interface)"
        direction TB
        MW[main_window.py<br/>Interface principale]
        VZ[visualization.py<br/>Gestionnaire onglets]
        
        subgraph "widgets/"
            IP[info_panel.py]
            IM[info_manager.py]
            EW[enhanced_widgets.py]
            XP[xenon_plot.py]
            NC[neutron_cycle_plot.py]
            FF[four_factors_plot.py]
            FP[flux_plot.py]
            PMD[preset_manager_dialog.py]
        end
        
        MW --> VZ
        MW --> PMD
        VZ --> XP
        VZ --> NC
        VZ --> FF
        VZ --> FP
        MW --> IP
        MW --> IM
        MW --> EW
    end
    
    subgraph "src/controller/"
        RC[reactor_controller.py<br/>Orchestration]
    end
    
    subgraph "src/model/"
        RM[reactor_model.py<br/>Physique + Simulation]
        PM[preset_model.py<br/>Gestion presets]
        C[config.py<br/>Configuration]
        
        subgraph "calculators/"
            CALC[Modules spécialisés]
        end
        
        RM --> PM
        RM --> C
        RM --> CALC
    end
    
    MW --> RC
    RC --> RM
    
    style MW fill:#e3f2fd
    style RC fill:#fff3e0
    style RM fill:#e8f5e8
```

## 3. Flux de Données Utilisateur

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant MW as MainWindow
    participant RC as ReactorController
    participant RM as ReactorModel
    participant W as Widgets
    
    U->>MW: Modifie paramètre (slider)
    MW->>RC: update_parameter(value)
    RC->>RM: set_parameter(value)
    RM->>RM: calculate_all()
    RM-->>RC: reactor_params
    RC-->>MW: updated_params
    MW->>W: update_visualizations()
    W-->>U: Affichage mis à jour
    MW->>MW: check_for_custom_preset()
    MW->>MW: update_reset_button_state()
```

## 4. Système de Presets Avancé

```mermaid
graph TD
    subgraph "Sources de Presets"
        CFG[config.json<br/>Presets Système]
        USER[user_presets.json<br/>Presets Utilisateur]
    end
    
    subgraph "PresetManager"
        PM[PresetManager]
        PM --> LOAD[Chargement]
        PM --> CRUD[CRUD Operations]
        PM --> VALID[Validation]
        PM --> PERSIST[Persistance]
    end
    
    subgraph "Interface"
        COMBO[QComboBox<br/>Sélection]
        RESET[Bouton Reset]
        MANAGE[Gestionnaire Avancé]
    end
    
    CFG --> LOAD
    USER --> LOAD
    LOAD --> PM
    
    PM --> COMBO
    PM --> MANAGE
    COMBO --> RESET
    
    CRUD --> USER
    
    style CFG fill:#fff3e0
    style USER fill:#e8f5e8
    style PM fill:#e3f2fd
```

## 5. Cycle de Simulation Temporelle (Xénon-135)

```mermaid
graph TB
    subgraph "État Initial"
        EQUI[Équilibre Xénon<br/>calculate_xenon_equilibrium()]
    end
    
    subgraph "Simulation Temporelle"
        ADV[advance_time(hours)]
        BAT[Équations Bateman<br/>I-135 → Xe-135]
        UPD[update_xenon_dynamics(dt)]
        CALC[calculate_all()]
    end
    
    subgraph "Visualisation"
        XW[XenonVisualizationWidget]
        GRAPH[Graphiques concentrations]
        HIST[Historique temporel]
    end
    
    subgraph "Contrôles"
        RESET_XE[Reset Équilibre]
        TIME_CTL[Contrôles Temps]
    end
    
    EQUI --> ADV
    ADV --> BAT
    BAT --> UPD
    UPD --> CALC
    CALC --> XW
    XW --> GRAPH
    XW --> HIST
    
    TIME_CTL --> ADV
    RESET_XE --> EQUI
    
    style EQUI fill:#fff3e0
    style BAT fill:#e8f5e8
    style XW fill:#e3f2fd
```

## 6. Système d'Information Contextuel

```mermaid
graph TD
    subgraph "Gestion Info"
        IM[InfoManager<br/>Centralisé]
        IM --> REG[register_widget()]
        IM --> TRACK[Mouse Tracking]
        IM --> EMIT[Signaux info]
    end
    
    subgraph "Affichage"
        IP[InfoPanel<br/>Toujours visible]
        ID[InfoDialog<br/>Touche 'i']
        TT[Tooltips<br/>Survol souris]
    end
    
    subgraph "Widgets Enhanced"
        IGB[InfoGroupBox]
        IW[InfoWidget]
        IS[InfoSlider]
        IC[InfoComboBox]
    end
    
    EMIT --> IP
    EMIT --> ID
    
    IGB --> REG
    IW --> REG
    IS --> REG
    IC --> REG
    
    TRACK --> TT
    
    style IM fill:#e3f2fd
    style IP fill:#fff3e0
    style ID fill:#e8f5e8
```

## 7. Gestion des États et Bouton Reset

```mermaid
stateDiagram-v2
    [*] --> PresetSelected: Sélection preset
    
    PresetSelected --> ParametersMatch: État correspond
    PresetSelected --> ParametersModified: Utilisateur modifie
    
    ParametersMatch --> ResetDisabled: Bouton désactivé
    ParametersModified --> CustomMode: Mode "Personnalisé"
    
    CustomMode --> ResetEnabled: Bouton activé
    
    ResetEnabled --> ResetClicked: Clic Reset
    ResetClicked --> PresetSelected: Restauration
    
    ParametersModified --> NewPresetSelected: Changement preset
    NewPresetSelected --> PresetSelected: Nouveau preset
    
    ResetEnabled --> NewPresetSelected: Changement preset
```

## 8. Architecture des Visualisations

```mermaid
graph TB
    subgraph "VisualizationPanel"
        TABS[QTabWidget]
    end
    
    subgraph "Onglets Physique"
        NC[Cycle Neutronique<br/>neutron_cycle_plot.py]
        FF[Quatre Facteurs<br/>four_factors_plot.py]
        FP[Flux Axial<br/>flux_plot.py]
        NB[Bilan Neutronique<br/>neutron_balance_plot.py]
        PD[Pilotage<br/>pilotage_diagram_plot.py]
    end
    
    subgraph "Onglet Temporel"
        XV[Dynamique Xénon<br/>xenon_plot.py]
        XC[Contrôles Temps]
        XG[Graphiques Jumeaux]
    end
    
    subgraph "Données Modèle"
        RM[ReactorModel]
        CD[cycle_data]
        FD[factors_data]
        XD[xenon_data]
    end
    
    TABS --> NC
    TABS --> FF
    TABS --> FP
    TABS --> NB
    TABS --> PD
    TABS --> XV
    
    XV --> XC
    XV --> XG
    
    RM --> CD
    RM --> FD
    RM --> XD
    
    CD --> NC
    FD --> FF
    XD --> XV
    
    style TABS fill:#e3f2fd
    style RM fill:#e8f5e8
```

## 9. Workflow Développement et Mémoire

```mermaid
graph LR
    subgraph "Memory Bank"
        BRIEF[brief.md<br/>Vision]
        PROD[product.md<br/>Produit]
        ARCH[architecture.md<br/>Architecture]
        TECH[tech.md<br/>Technologies]
        CTX[context.md<br/>État actuel]
        MERM[mermaid.md<br/>Diagrammes]
    end
    
    subgraph "Développement"
        INIT[Initialisation]
        TASK[Tâche]
        UPDATE[Mise à jour]
    end
    
    INIT --> BRIEF
    TASK --> CTX
    UPDATE --> CTX
    
    BRIEF --> PROD
    PROD --> ARCH
    ARCH --> TECH
    
    CTX --> TASK
    MERM --> ARCH
    
    style BRIEF fill:#fff3e0
    style CTX fill:#e8f5e8
    style TASK fill:#e3f2fd
```

## 10. Pipeline de Build et Distribution

```mermaid
graph TD
    subgraph "Développement"
        SRC[Code Source<br/>Python + PyQt6]
        CFG[Configuration<br/>config.json]
        DEPS[Dependencies<br/>requirements.txt]
    end
    
    subgraph "Build Process"
        PY[build_windows.py]
        BAT[build_windows.bat]
        INST[PyInstaller]
    end
    
    subgraph "Distribution"
        EXE[NeutroScope.exe<br/>Exécutable Windows]
        DIST[Distribution<br/>OneDrive entreprise]
    end
    
    subgraph "Utilisateurs Finaux"
        EDU[Étudiants]
        PROF[Professeurs]
        INDUS[Professionnels]
    end
    
    SRC --> PY
    CFG --> PY
    DEPS --> PY
    
    PY --> BAT
    BAT --> INST
    INST --> EXE
    
    EXE --> DIST
    DIST --> EDU
    DIST --> PROF
    DIST --> INDUS
    
    style SRC fill:#e8f5e8
    style EXE fill:#fff3e0
    style DIST fill:#e3f2fd
```