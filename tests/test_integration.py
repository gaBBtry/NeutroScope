"""
Tests de cohérence et d'intégration entre les différentes couches de l'application.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.controller.reactor_controller import ReactorController

# --- Fixtures ---

@pytest.fixture(scope="session")
def qapp():
    """Fixture to create a QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def app(qapp):
    """Provides a MainWindow instance for GUI tests."""
    window = MainWindow()
    window.show()
    return window

@pytest.fixture
def controller():
    """Provides a ReactorController instance for logic tests."""
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
    initial_params = controller.get_reactor_parameters()
    
    # Change a parameter that significantly affects k_effective
    controller.update_control_rod_position(100) # Rods fully inserted
    
    final_params = controller.get_reactor_parameters()
    
    assert initial_params["k_effective"] != pytest.approx(final_params["k_effective"])
    assert final_params["k_effective"] < 1.0 # Inserting rods should decrease k_eff

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

    assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1)

def test_gui_preset_change_coherence(app, qtbot):
    """
    Test coherence for different presets changed via the GUI.
    """
    model = app.controller.model
    presets = app.controller.get_preset_names()

    for preset_name in presets:
        if app.preset_combo.currentText() == preset_name:
            continue
            
        with qtbot.waitSignal(app.preset_combo.currentTextChanged, timeout=1000):
            app.preset_combo.setCurrentText(preset_name)

        k_eff_model = model.k_effective
        reactivity_model_pcm = model.reactivity * 100000

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
    model = app.controller.model
    new_rod_position = 50

    app.rod_slider.setValue(new_rod_position)
    
    k_eff_model = model.k_effective
    reactivity_model_pcm = model.reactivity * 100000

    k_eff_gui_text = app.k_effective_label.text()
    reactivity_gui_text = app.reactivity_label.text()

    k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
    reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

    assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1)
    
    assert model.control_rod_position == new_rod_position 