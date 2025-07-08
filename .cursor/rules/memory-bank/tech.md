# Technology Stack and Development Environment

This document outlines the technologies, tools, and practices used in the NeutroScope project.

## Core Technologies

-   **Programming Language**: **Python 3.13+**
    -   Chosen for its extensive scientific computing ecosystem, readability, and rapid development capabilities.
-   **User Interface (UI)**: **PyQt6**
    -   A robust, cross-platform GUI framework that provides a native look and feel.

## Key Libraries

-   **Numerical Operations**: **NumPy**
    -   Used for all numerical calculations, especially array and matrix operations in the reactor model.
-   **Data Visualization**: **Matplotlib**
    -   Integrated with PyQt6 to generate all plots and graphs (flux distribution, four-factors, etc.).

## Development and Tooling

-   **Environment Management**: **venv**
    -   Standard Python tool for creating isolated virtual environments to manage dependencies.
-   **Dependency Management**: `requirements.txt`
    -   A standard file listing all necessary Python packages.
-   **Testing Framework**: **Pytest**
    -   Used for writing and running all unit and integration tests.
    -   **Plugins**:
        -   `pytest-qt`: For testing PyQt6 components.
        -   `pytest-cov`: For measuring test coverage.
-   **Version Control**: **Git**
    -   All source code is managed in a Git repository.

## Build and Deployment

-   **Build Tool**: **PyInstaller**
    -   Creates standalone Windows executables with all dependencies bundled.
    -   Configuration optimized for PyQt6 applications with matplotlib integration.
-   **Build Scripts**: 
    -   `build_windows.bat`: Automated batch script for end users
    -   `build_windows.py`: Python script with advanced error handling and validation
-   **Deployment Method**: **OneDrive Enterprise Sharing**
    -   Executable distributed via corporate OneDrive links
    -   No installation required on target machines
    -   Compatible with Windows 10/11 and Windows 8.1

## Project Structure

-   The project follows a standard structure separating the model, view, and controller logic:
    -   `src/model`: Core simulation logic.
    -   `src/gui`: UI components.
    -   `src/controller`: Connects the model and the GUI.
    -   `tests/`: Contains all test files.
    -   `docs/`: Project documentation.
    -   `config.json`: External configuration for presets and physical parameters. 