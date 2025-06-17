"""
Tests de cohérence et d'intégration entre les différentes couches de l'application.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.controller.reactor_controller import ReactorController
from unittest.mock import patch, MagicMock

# --- Fixtures ---

@pytest.fixture(scope="session")
def qapp():
    """Fixture to create a QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def mock_openmc():
    """Fixture to mock the OpenMCModel to prevent real simulations during tests."""
    with patch('src.model.reactor_model.OpenMCModel') as mock:
        # Configure the mock to return a controllable runner instance
        mock_runner = MagicMock()
        # Set a default return value for k_effective
        mock_runner.run_simulation.return_value = 1.001
        mock.return_value = mock_runner
        yield mock

@pytest.fixture
def app(qapp, mock_openmc):
    """Provides a MainWindow instance for GUI tests with a mocked OpenMC backend."""
    window = MainWindow()
    window.show()
    return window

@pytest.fixture
def controller(mock_openmc):
    """Provides a ReactorController instance for logic tests with a mocked OpenMC backend."""
    return ReactorController()

# --- Tests d'intégration Logique (Controller <-> Model) ---

def test_controller_updates_model_rod_position(controller):
    """Verify that updating rod position via controller changes the model's state."""
    new_position = 75
    controller.update_control_rod_position(new_position)
    assert controller.model.control_rod_position == new_position

def test_controller_updates_model_boron(controller):
    """Verify that updating boron concentration via controller changes the model's state."""
    new_concentration = 1200
    controller.update_boron_concentration(new_concentration)
    assert controller.model.boron_concentration == new_concentration

def test_controller_applies_preset_to_model(controller):
    """Verify that applying a preset via controller updates the model correctly."""
    preset_name = controller.get_preset_names()[1] # Choose a preset
    controller.apply_preset(preset_name)
    
    from src.model import config
    preset_values = config.PRESETS[preset_name]
    
    assert controller.model.control_rod_position == preset_values["control_rod_position"]
    assert controller.model.boron_concentration == preset_values["boron_concentration"]
    assert controller.model.moderator_temperature == preset_values["moderator_temperature"]
    assert controller.model.fuel_enrichment == preset_values["fuel_enrichment"]

def test_controller_returns_correct_k_eff_after_update(controller):
    """Verify that the controller returns updated data after a change."""
    # Since OpenMC is mocked, we can control the k_eff values
    mock_runner = controller.model.openmc_runner
    
    # First calculation
    mock_runner.run_simulation.return_value = 1.05
    controller.update_control_rod_position(0) # Recalculate
    initial_params = controller.get_reactor_parameters()
    assert initial_params["k_effective"] == 1.05
    
    # Change a parameter and the mocked k_eff
    mock_runner.run_simulation.return_value = 0.95
    controller.update_control_rod_position(100) # Rods fully inserted
    final_params = controller.get_reactor_parameters()
    
    assert initial_params["k_effective"] != pytest.approx(final_params["k_effective"])
    assert final_params["k_effective"] == 0.95 # Check the new mocked value

# --- Tests d'intégration IHM (GUI <-> Controller <-> Model) ---

def test_gui_initial_state_coherence(app):
    """
    Test if the initial GUI state (after loading default preset)
    is coherent with the model's state.
    """
    model = app.controller.model
    k_eff_model = model.k_effective
    reactivity_model_pcm = model.reactivity * 100000

    k_eff_gui_text = app.k_effective_label.text()
    reactivity_gui_text = app.reactivity_label.text()

    k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
    reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

    assert k_eff_gui == pytest.approx(1.001, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(99.9, abs=1e-1)

def test_gui_preset_change_coherence(app, qtbot):
    """
    Test coherence for different presets changed via the GUI.
    """
    mock_runner = app.controller.model.openmc_runner
    presets = app.controller.get_preset_names()

    # Let's assign a unique k_eff for each preset change
    k_eff_values = [0.98, 1.02, 0.99, 1.01, 1.03, 0.97]

    for i, preset_name in enumerate(presets):
        if app.preset_combo.currentText() == preset_name:
            continue
            
        mock_runner.run_simulation.return_value = k_eff_values[i % len(k_eff_values)]

        with qtbot.waitSignal(app.preset_combo.currentTextChanged, timeout=1000):
            app.preset_combo.setCurrentText(preset_name)

        k_eff_model = mock_runner.run_simulation.return_value
        reactivity_model = (k_eff_model - 1) / k_eff_model
        reactivity_model_pcm = reactivity_model * 100000

        k_eff_gui_text = app.k_effective_label.text()
        reactivity_gui_text = app.reactivity_label.text()
        
        k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
        reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

        assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5), f"k_effective mismatch for preset {preset_name}"
        assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1), f"Reactivity mismatch for preset {preset_name}"

def test_gui_control_rod_slider_coherence(app, qtbot):
    """
    Test coherence after moving the control rod slider in the GUI.
    """
    mock_runner = app.controller.model.openmc_runner
    new_rod_position = 50
    new_k_eff = 0.995
    mock_runner.run_simulation.return_value = new_k_eff

    app.rod_slider.setValue(new_rod_position)
    
    reactivity_model = (new_k_eff - 1) / new_k_eff
    reactivity_model_pcm = reactivity_model * 100000

    k_eff_gui_text = app.k_effective_label.text()
    reactivity_gui_text = app.reactivity_label.text()

    k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
    reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

    assert k_eff_gui == pytest.approx(new_k_eff, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1)
    
    assert app.controller.model.control_rod_position == new_rod_position 