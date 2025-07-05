"""
Tests de cohérence et d'intégration entre les différentes couches de l'application.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QSlider, QSpinBox, QLabel, QComboBox
from src.gui.main_window import MainWindow
from src.controller.reactor_controller import ReactorController
from unittest.mock import patch, MagicMock
from src.model import config as global_config

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
    """Provides a ReactorController instance."""
    return ReactorController()

# --- Tests ---

def test_app_startup(qtbot):
    """
    A very basic test to ensure the MainWindow can be created without crashing.
    """
    window = MainWindow()
    qtbot.addWidget(window)
    assert window is not None
    assert window.isVisible() is False
    
    window.show()
    assert window.isVisible() is True
    
    initial_preset_name = "Démarrage"
    assert window.preset_combo.currentText() == initial_preset_name

def test_initial_preset_is_applied(app):
    """
    Test that the initial preset is correctly applied when the application starts.
    """
    initial_preset_name = "Démarrage"
    assert app.preset_combo.currentText() == initial_preset_name

def test_controller_updates_model(controller):
    """
    Test that controller methods correctly call the underlying model's update methods.
    """
    controller.model = MagicMock() # Replace real model with a mock
    
    controller.update_control_rod_position(50)
    controller.model.update_control_rod_position.assert_called_once_with(50)
    
    controller.update_boron_concentration(1000)
    controller.model.update_boron_concentration.assert_called_once_with(1000)

def test_controller_applies_preset(controller):
    """
    Test that the controller correctly applies a preset and updates the model.
    """
    controller.model = MagicMock()
    preset_name = "Démarrage"
    
    controller.apply_preset(preset_name)
    controller.model.apply_preset.assert_called_once_with(preset_name)

def test_gui_reflects_model_change(app, controller, qtbot):
    """

    Test that a change in the model (via controller) is reflected in the GUI.
    """
    # Change a parameter
    controller.update_control_rod_position(100)
    
    # Get the updated parameters from the model
    final_params = controller.get_reactor_parameters()
    
    # Manually trigger the GUI update
    app.update_reactor_params(final_params)
    
    k_eff_text = app.k_effective_label.text()
    k_eff_gui_value = float(k_eff_text.split(':')[1].strip())
    
    # Assert that the GUI value matches the model value
    assert k_eff_gui_value == pytest.approx(final_params["k_effective"], abs=1e-5)

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
    # First calculation
    initial_params = controller.get_reactor_parameters()
    initial_k_eff = initial_params["k_effective"]
    
    # Change a parameter
    controller.update_control_rod_position(100) # Rods fully inserted
    final_params = controller.get_reactor_parameters()
    final_k_eff = final_params["k_effective"]
    
    # The new k_effective should be different (lower)
    assert initial_k_eff != pytest.approx(final_k_eff)
    assert final_k_eff < initial_k_eff

# --- Tests d'intégration IHM (GUI <-> Controller <-> Model) ---

def test_gui_initial_state_coherence(app):
    """Test if GUI labels correctly reflect the initial state of the model."""
    # Manually call the update to sync GUI with initial model state
    app.update_reactor_params(app.controller.get_reactor_parameters())
    
    # Check if the labels contain the expected text (rather than using mock assertions)
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert "k-eff:" in k_eff_text
    assert "Réactivité (pcm):" in reactivity_text

def test_gui_preset_change_coherence(app, qtbot):
    """
    Test coherence for different presets changed via the GUI.
    """
    presets = app.controller.get_preset_names()

    for preset_name in presets:
        if app.preset_combo.currentText() == preset_name:
            continue

        with qtbot.waitSignal(app.preset_combo.currentTextChanged, timeout=1000):
            app.preset_combo.setCurrentText(preset_name)

        # After the UI change, the controller has already updated the model
        params = app.controller.get_reactor_parameters()
        k_eff_model = params['k_effective']
        reactivity_model_pcm = params['reactivity'] * 100000

        k_eff_gui_text = app.k_effective_label.text()
        reactivity_gui_text = app.reactivity_label.text()
        
        k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
        reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

        assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5), f"k_effective mismatch for preset {preset_name}"
        assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1), f"Reactivity mismatch for preset {preset_name}"

def test_gui_preset_updates_inputs(app, qtbot):
    """
    Test if changing a preset via the GUI updates the input widget states.
    """
    preset_name = app.controller.get_preset_names()[1] # choose a preset

    # Simulate applying the preset
    app.controller.apply_preset(preset_name)
    
    # Call the method that updates input widgets from the model state
    config = app.controller.get_current_configuration()
    config["reactor_params"] = app.controller.get_reactor_parameters()
    app.update_ui_from_preset(config)

    # Verify that input widgets are updated to reflect the new preset
    preset_values = app.controller.get_current_configuration()
    assert app.rod_slider.value() == int(preset_values["control_rod_position"])
    assert app.boron_spinbox.value() == preset_values["boron_concentration"]
    assert app.moderator_temp_slider.value() == int(preset_values["moderator_temperature"])
    assert app.fuel_enrichment_slider.value() == int(preset_values["fuel_enrichment"] * 10)

def test_gui_control_rod_slider_coherence(app, qtbot):
    """
    Test coherence after moving the control rod slider in the GUI.
    """
    new_rod_position = 75

    # Simulate user moving the slider, which directly calls the controller
    app.on_rod_position_changed(new_rod_position)

    # Assert that the model was updated
    assert app.controller.model.control_rod_position == new_rod_position

    # Assert that the GUI labels were updated
    final_params = app.controller.get_reactor_parameters()
    expected_k_eff = final_params['k_effective']
    expected_reactivity_pcm = final_params['reactivity'] * 100000
    
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {expected_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text

def test_gui_boron_spinbox_coherence(app, qtbot):
    """
    Test coherence after changing boron concentration in the GUI.
    """
    new_boron = 850

    # Simulate user changing the value of the boron spinbox
    app.on_boron_concentration_changed(new_boron)
    
    # Assert that the model was updated
    assert app.controller.model.boron_concentration == new_boron

    # Assert that the GUI labels were updated
    final_params = app.controller.get_reactor_parameters()
    expected_k_eff = final_params['k_effective']
    expected_reactivity_pcm = final_params['reactivity'] * 100000
    
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {expected_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text

def test_gui_temperature_slider_coherence(app, qtbot):
    """
    Test coherence after changing moderator temperature in the GUI.
    """
    new_temp = 325.0

    # Simulate user changing the value of the temperature slider
    app.on_moderator_temperature_changed(int(new_temp))

    # Assert that the model was updated
    assert app.controller.model.moderator_temperature == new_temp

    # Assert that the GUI labels were updated
    final_params = app.controller.get_reactor_parameters()
    expected_k_eff = final_params['k_effective']
    expected_reactivity_pcm = final_params['reactivity'] * 100000
    
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {expected_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text

def test_gui_data_displays_update_on_change(app, qtbot):
    """
    Test that data displays (plots, tables) are updated when parameters change.
    """
    # Mock controller methods to return predictable data
    app.controller.get_axial_flux_distribution = MagicMock(return_value=([0, 1], [0.5, 0.5]))
    # Provide a complete dictionary for the four factors data with all required keys
    app.controller.get_four_factors_data = MagicMock(return_value={
        'eta': 2.0, 'epsilon': 1.05, 'p': 0.8, 'f': 0.9,
        'k_infinite': 1.6, 'thermal_non_leakage_prob': 0.95,
        'fast_non_leakage_prob': 0.97, 'k_effective': 1.001
    })
    app.controller.get_neutron_balance_data = MagicMock(return_value={'sections': [{'name': 'Absorption', 'value': 0.5, 'color': '#ff9999', 'tooltip': 'Neutrons absorbed'}, {'name': 'Leakage', 'value': 0.3, 'color': '#66b3ff', 'tooltip': 'Neutrons leaked'}, {'name': 'Fission', 'value': 0.2, 'color': '#99ff99', 'tooltip': 'Neutrons from fission'}]})
    app.controller.get_axial_offset_data = MagicMock(return_value={'axial_offset': 0.05, 'power_percentage': 75.0})

    # Trigger an update by changing a parameter, which should call update_visualizations internally
    app.controller.update_control_rod_position(25)

    # Manually trigger the visualization update to ensure it's called
    app.update_visualizations()
    
    # Verify that the methods to fetch new data were called
    app.controller.get_axial_flux_distribution.assert_called()
    app.controller.get_four_factors_data.assert_called()
    app.controller.get_neutron_balance_data.assert_called()
    app.controller.get_axial_offset_data.assert_called()

# --- Integration Tests ---

def test_preset_application_updates_ui(app):
    """
    Test that applying a preset correctly updates the model and subsequently the UI widgets.
    """
    preset_name = "Critique à puissance nominale"
    preset_config = global_config.PRESETS[preset_name]
    
    # Simulate applying the preset in the controller
    result = app.controller.apply_preset(preset_name)
    assert result is not None # Ensure preset was applied in the model

    # Now, call the UI update method that would be triggered by the preset change
    config_from_controller = app.controller.get_current_configuration()
    config_from_controller["reactor_params"] = app.controller.get_reactor_parameters()
    app.update_ui_from_preset(config_from_controller)

    # Verify that the UI widgets were updated with the correct values from the preset
    assert app.rod_slider.value() == int(preset_config["control_rod_position"])
    assert app.boron_spinbox.value() == preset_config["boron_concentration"]
    assert app.moderator_temp_slider.value() == int(preset_config["moderator_temperature"])
    assert app.fuel_enrichment_slider.value() == int(preset_config["fuel_enrichment"] * 10)

def test_control_change_updates_displays(app):
    """
    Test that changing a control updates the model and the UI parameter displays.
    """
    # Simulate user changing boron concentration
    params = app.controller.update_boron_concentration(900)

    # Call the UI update method with the new parameters from the controller
    app.update_reactor_params(params)

    # Verify the model has the new state
    assert app.controller.model.boron_concentration == 900
    
    new_k_eff = params["k_effective"]

    # Verify the UI labels were updated with the correct text
    expected_reactivity_pcm = (new_k_eff - 1) / new_k_eff * 100000
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {new_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text
    assert "Temps de doublement:" in app.doubling_time_label.text() # Check that it was updated 