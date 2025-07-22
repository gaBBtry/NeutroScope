# Diagrammes Architecturaux NeutroScope

Ce fichier contient les diagrammes Mermaid essentiels pour comprendre l'architecture et le fonctionnement de NeutroScope.

## 1. Architecture MVC Globale

```mermaid
graph TB
    subgraph "Vue (GUI)"
        MW[main_window.py]
        VZ[visualization.py]
        subgraph "widgets/"
            IP[info_panel.py]
            IM[info_manager.py]
            EW[enhanced_widgets.py]
            XP[xenon_plot.py]
            NC[neutron_cycle_plot.py]
            FF[four_factors_plot.py]
            FP[flux_plot.py]
            NB[neutron_balance_plot.py]
            ID[info_dialog.py]
            CB[credits_button.py]
        end
        MW --> VZ
        VZ --> XP
        VZ --> NC
        VZ --> FF
        VZ --> FP
        VZ --> NB
        MW --> IP
        MW --> IM
        MW --> EW
        MW --> ID
        MW --> CB
    end
    subgraph "Contrôleur"
        RC[reactor_controller.py]
    end
    subgraph "Modèle"
        RM[reactor_model.py]
        PM[preset_model.py]
        CFG[config.py]
    end
    MW --> RC
    RC --> RM
    RM --> PM
    RM --> CFG
    style MW fill:#e3f2fd
    style RC fill:#fff3e0
    style RM fill:#e8f5e8
```

## 2. Flux de Données Utilisateur

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant MW as main_window.py
    participant RC as reactor_controller.py
    participant RM as reactor_model.py
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

## 3. Système de Presets

```mermaid
graph TD
    subgraph "Sources de Presets"
        CFG[config.json]
        USER[user_presets.json]
    end
    subgraph "PresetManager"
        PM[preset_model.py]
        PM --> LOAD[Chargement]
        PM --> CRUD[CRUD Operations]
        PM --> VALID[Validation]
        PM --> PERSIST[Persistance]
    end
    subgraph "Interface"
        COMBO[QComboBox]
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

## 4. Cycle de Simulation Temporelle (Xénon-135)

```mermaid
graph TB
    subgraph "État Initial"
        EQUI[Équilibre Xénon\ncalculate_xenon_equilibrium()]
    end
    subgraph "Simulation Temporelle"
        ADV[advance_time(hours)]
        BAT[Équations Bateman\nI-135 → Xe-135]
        UPD[update_xenon_dynamics(dt)]
        CALC[calculate_all()]
    end
    subgraph "Visualisation"
        XP[xenon_plot.py]
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
    CALC --> XP
    XP --> GRAPH
    XP --> HIST
    TIME_CTL --> ADV
    RESET_XE --> EQUI
    style EQUI fill:#fff3e0
    style BAT fill:#e8f5e8
    style XP fill:#e3f2fd
```

## 5. Système d'Information Contextuel

```mermaid
graph TD
    subgraph "Gestion Info"
        IM[info_manager.py]
        IM --> REG[register_widget()]
        IM --> TRACK[Mouse Tracking]
        IM --> EMIT[Signaux info]
    end
    subgraph "Affichage"
        IP[info_panel.py]
        ID[info_dialog.py]
        TT[Tooltips]
    end
    subgraph "Widgets Enhanced"
        EW[enhanced_widgets.py]
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

## 6. Gestion des États et Bouton Reset

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

## 7. Architecture des Visualisations

```mermaid
graph TB
    subgraph "VisualizationPanel"
        VZ[visualization.py]
        TABS[QTabWidget]
    end
    subgraph "Onglets Physique"
        NC[neutron_cycle_plot.py]
        FF[four_factors_plot.py]
        FP[flux_plot.py]
        NB[neutron_balance_plot.py]
    end
    subgraph "Onglet Temporel"
        XP[xenon_plot.py]
        XC[Contrôles Temps]
        XG[Graphiques Jumeaux]
    end
    subgraph "Données Modèle"
        RM[reactor_model.py]
        CD[cycle_data]
        FD[factors_data]
        XD[xenon_data]
    end
    VZ --> TABS
    TABS --> NC
    TABS --> FF
    TABS --> FP
    TABS --> NB
    TABS --> XP
    XP --> XC
    XP --> XG
    RM --> CD
    RM --> FD
    RM --> XD
    CD --> NC
    FD --> FF
    XD --> XP
    style TABS fill:#e3f2fd
    style RM fill:#e8f5e8
```

## 8. Pipeline de Build et Distribution

```mermaid
graph TD
    subgraph "Développement"
        SRC[src/]
        CFG[config.json]
        DEPS[requirements.txt]
    end
    subgraph "Build Process"
        PY[build_windows.py]
        BAT[build_windows.bat]
        INST[PyInstaller]
    end
    subgraph "Distribution"
        EXE[NeutroScope.exe]
        DIST[Distribution]
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

## 9. Workflow Développement et Mémoire

```mermaid
graph LR
    subgraph "Memory Bank"
        BRIEF[brief.md]
        PROD[product.md]
        ARCH[architecture.md]
        TECH[tech.md]
        CTX[context.md]
        MERM[mermaid.md]
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