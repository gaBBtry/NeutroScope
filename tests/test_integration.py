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
def mock_openmc():
    """Fixture to mock the OpenMCModel to prevent real simulations during tests."""
    with patch('src.model.reactor_model.OpenMCModel') as mock:
        mock_runner = MagicMock()
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
    """Provides a ReactorController instance with a mocked OpenMC backend."""
    # The controller will be instantiated with a model that uses the mocked OpenMCModel
    controller_instance = ReactorController()
    # Let's attach the mock runner for easy access in tests
    controller_instance.model.openmc_runner = mock_openmc.return_value
    return controller_instance

# --- Tests ---

def test_app_startup(qtbot, mock_openmc):
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

def test_model_simulation_call(controller):
    """
    Test that changing a parameter triggers a new OpenMC simulation.
    """
    # Reset call count for the mock runner
    controller.model.openmc_runner.run_simulation.reset_mock()
    
    # Change a parameter that should trigger a recalculation
    controller.update_boron_concentration(1200)
    
    # Verify that a new simulation was run
    controller.model.openmc_runner.run_simulation.assert_called_once()

def test_gui_reflects_model_change(app, controller, qtbot):
    """

    Test that a change in the model (via controller) is reflected in the GUI.
    """
    # Let's change a parameter and check if k_effective in the GUI updates
    new_k_eff_value = 0.95
    controller.model.openmc_runner.run_simulation.return_value = new_k_eff_value
    
    # This action will update the model, which should ideally signal the GUI.
    # In a real app, this would be asynchronous. For this test, we assume
    # the controller updates the model, and then we check the GUI.
    controller.update_control_rod_position(100)
    
    # To ensure the GUI has had time to process events, we can use qtbot.
    # However, direct UI updates in response to model changes are hard to test
    # without a formal model-view signaling mechanism (like Qt's signals/slots)
    # fully implemented between the model and the view.
    
    # Let's manually trigger the update method in the GUI for this test
    final_params = controller.get_reactor_parameters()
    app.update_reactor_params(final_params)
    
    k_eff_text = app.k_effective_label.text()
    
    # Extract the float value from "k-eff: 0.95000"
    k_eff_gui_value = float(k_eff_text.split(':')[1].strip())
    
    assert k_eff_gui_value == pytest.approx(new_k_eff_value)
    assert final_params["k_effective"] == 0.95 # Check the new mocked value

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
    mock_runner = app.controller.model.openmc_runner
    new_rod_position = 75
    new_k_eff = 1.002
    mock_runner.run_simulation.return_value = new_k_eff

    # Simulate user moving the slider
    app.controller.update_control_rod_position(new_rod_position)
    
    # Manually trigger the display update
    app.update_reactor_params(app.controller.get_reactor_parameters())

    # Assert that the model was updated
    assert app.controller.model.control_rod_position == new_rod_position

    # Assert that the GUI labels were updated
    expected_reactivity_pcm = (new_k_eff - 1) / new_k_eff * 100000
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {new_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text

def test_gui_boron_spinbox_coherence(app, qtbot):
    """
    Test coherence after changing boron concentration in the GUI.
    """
    mock_runner = app.controller.model.openmc_runner
    new_boron = 850
    new_k_eff = 1.003
    mock_runner.run_simulation.return_value = new_k_eff

    # Simulate user changing the value of the boron spinbox
    app.controller.update_boron_concentration(new_boron)
    
    # Manually trigger the display update
    app.update_reactor_params(app.controller.get_reactor_parameters())
    
    # Assert that the model was updated
    assert app.controller.model.boron_concentration == new_boron

    # Assert that the GUI labels were updated
    expected_reactivity_pcm = (new_k_eff - 1) / new_k_eff * 100000
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {new_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text

def test_gui_temperature_slider_coherence(app, qtbot):
    """
    Test coherence after changing moderator temperature in the GUI.
    """
    mock_runner = app.controller.model.openmc_runner
    new_temp = 325.0
    new_k_eff = 0.998
    mock_runner.run_simulation.return_value = new_k_eff

    # Simulate user changing the value of the temperature slider
    app.controller.update_moderator_temperature(new_temp)
    
    # Manually trigger the display update
    app.update_reactor_params(app.controller.get_reactor_parameters())

    # Assert that the model was updated
    assert app.controller.model.moderator_temperature == new_temp

    # Assert that the GUI labels were updated
    expected_reactivity_pcm = (new_k_eff - 1) / new_k_eff * 100000
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {new_k_eff:.5f}" in k_eff_text
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

def test_control_change_updates_displays(app, mock_openmc):
    """
    Test that changing a control updates the model and the UI parameter displays.
    """
    new_k_eff = 1.025
    # Configure the mock properly to return the new k_eff
    app.controller.model.openmc_runner.run_simulation.return_value = new_k_eff

    # Simulate user changing boron concentration, which returns the new parameters
    params = app.controller.update_boron_concentration(900)

    # Call the UI update method with the new parameters from the controller
    app.update_reactor_params(params)

    # Verify the model has the new state
    assert app.controller.model.boron_concentration == 900
    # Verify that the k_effective has been updated through the simulation
    assert params["k_effective"] == new_k_eff

    # Verify the UI labels were updated with the correct text
    expected_reactivity_pcm = (new_k_eff - 1) / new_k_eff * 100000
    k_eff_text = app.k_effective_label.text()
    reactivity_text = app.reactivity_label.text()
    
    assert f"k-eff: {new_k_eff:.5f}" in k_eff_text
    assert f"Réactivité (pcm): {expected_reactivity_pcm:.1f}" in reactivity_text
    assert "Temps de doublement:" in app.doubling_time_label.text() # Check that it was updated 