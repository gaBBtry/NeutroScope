# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NeutroScope is a pedagogical nuclear reactor simulation application built with Python and PyQt6. It provides an interactive educational tool for learning nuclear reactor physics, specifically focusing on neutron lifecycle visualization and reactivity control parameters.

## Development Commands

### Running the Application
```bash
python main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Building Executable (Windows)
```bash
python build_windows.py
# or
build_windows.bat
```

### Testing
No specific test framework is configured. The application uses manual testing through the GUI.

## Architecture Overview

### Core Architecture Pattern
The application follows a **Model-View-Controller (MVC)** architecture:

- **Model**: `src/model/reactor_model.py` - Nuclear reactor physics calculations and simulation
- **View**: `src/gui/` - PyQt6 GUI components and visualizations  
- **Controller**: `src/controller/reactor_controller.py` - Bridges model and view

### Key Components

#### 1. Reactor Model (`src/model/reactor_model.py`)
- Implements nuclear reactor physics calculations
- Handles four-factor formula: k∞ = η × ε × p × f
- Manages xenon-135 dynamics and time-dependent simulations
- Calculates neutron leakage using two-group diffusion theory
- Supports reactor presets and configuration management

#### 2. Configuration System (`config.json` + `src/model/config.py`)
- Centralized configuration in `config.json` with strict validation
- Physical constants, reactor parameters, and GUI settings
- Preset reactor configurations for different operational states
- Parameter ranges and validation rules

#### 3. GUI Components (`src/gui/`)
- **MainWindow**: Primary application window with control panels
- **VisualizationPanel**: Reactor visualization plots and charts
- **Enhanced Widgets**: Custom PyQt6 widgets with info tooltips
- **Plots**: Specialized plotting widgets for flux, neutron balance, etc.

#### 4. Preset Management (`src/model/preset_model.py`)
- Advanced preset system with categories (Base, Temporal, Custom)
- Import/export functionality for sharing configurations
- Validation and version control for preset data

### Key Physics Calculations

#### Four-Factor Formula
The reactor uses the six-factor formula: k_eff = η × ε × p × f × P_NL_fast × P_NL_thermal

- **η (eta)**: Reproduction factor - neutrons per absorption in fuel
- **ε (epsilon)**: Fast fission factor - enhancement from fast fissions
- **p**: Resonance escape probability - fraction avoiding resonance capture
- **f**: Thermal utilization factor - fraction of thermal neutrons absorbed in fuel
- **P_NL**: Non-leakage probabilities for fast and thermal neutrons

#### Xenon-135 Dynamics
- Time-dependent simulation using Runge-Kutta 4th order integration
- Coupled I-135 → Xe-135 decay chain with neutron absorption
- Reactivity feedback effects from xenon poisoning

### Configuration Management

#### Parameter Validation
The configuration system enforces strict validation:
- All parameters must be defined in `config.json`
- Missing keys cause immediate KeyError at startup
- GUI settings control widget behavior and validation ranges

#### Preset System
- **Base Presets**: Standard reactor configurations (startup, end-of-cycle, etc.)
- **Temporal Presets**: Include time-dependent xenon concentrations
- **Custom Presets**: User-created configurations with full state

### GUI Architecture

#### Info Management System
- Centralized `InfoManager` handles all tooltips and help text
- Context-sensitive information panels
- Keyboard shortcut 'i' for detailed parameter explanations

#### Visualization Components
- Real-time reactor parameter plotting
- Axial flux distribution visualization
- Neutron balance and cycle diagrams
- Xenon dynamics time-series plots

### File Structure Conventions

#### Model Layer
- `reactor_model.py`: Core physics calculations
- `config.py`: Configuration loading and validation
- `preset_model.py`: Preset management system

#### GUI Layer
- `main_window.py`: Primary window and layout management
- `visualization.py`: Plot container and management
- `widgets/`: Custom enhanced widgets with info integration

#### Controller Layer
- `reactor_controller.py`: Single controller bridging model and view
- Exposes model methods to GUI components
- Handles parameter updates and recalculations

### Development Guidelines

#### Adding New Parameters
1. Add parameter definition to `config.json`
2. Add loading logic to `config.py`
3. Update `ReactorModel` to use the parameter
4. Add GUI controls in appropriate widget
5. Connect signals in `MainWindow`

#### Adding New Visualizations
1. Create widget class in `src/gui/widgets/`
2. Integrate with `InfoManager` for help text
3. Add to `VisualizationPanel` layout
4. Connect to controller data methods

#### Physics Model Extensions
- Model calculations are isolated in `ReactorModel`
- All physics constants come from `config.json`
- New calculations should follow the existing pattern of dedicated methods
- Time-dependent effects use the `advance_time()` framework

### Important Notes

#### Configuration Philosophy
- `config.json` is the single source of truth for all parameters
- Missing configuration keys cause immediate startup failure
- This ensures configuration completeness and prevents silent errors

#### State Management
- Reactor state is entirely contained in `ReactorModel`
- Controller provides read-only access to model state
- GUI components do not maintain physics state

#### Extensibility
- New reactor types can be added by subclassing `ReactorModel`
- Preset system supports arbitrary parameter sets
- Visualization framework supports dynamic plot addition