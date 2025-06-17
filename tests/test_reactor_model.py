"""
Tests for the ReactorModel class
"""
import pytest
from src.model.reactor_model import ReactorModel
import numpy as np
from unittest.mock import patch, MagicMock

@pytest.fixture
def reactor():
    """Provides a default ReactorModel instance for tests."""
    return ReactorModel()

def test_calculate_reactivity_critical(reactor):
    """Test reactivity calculation when k_effective is exactly 1.0 (critical)."""
    reactor.k_effective = 1.0
    reactor.calculate_reactivity()
    assert reactor.reactivity == 0.0

def test_calculate_reactivity_supercritical(reactor):
    """Test reactivity calculation when k_effective is greater than 1.0 (supercritical)."""
    reactor.k_effective = 1.005
    reactor.calculate_reactivity()
    # reactivity = (k_eff - 1) / k_eff = 0.005 / 1.005
    assert reactor.reactivity == pytest.approx(0.005 / 1.005)

def test_calculate_reactivity_subcritical(reactor):
    """Test reactivity calculation when k_effective is less than 1.0 (subcritical)."""
    reactor.k_effective = 0.995
    reactor.calculate_reactivity()
    # reactivity = (k_eff - 1) / k_eff = -0.005 / 0.995
    assert reactor.reactivity == pytest.approx(-0.005 / 0.995)

def test_calculate_reactivity_zero_k_effective(reactor):
    """Test reactivity calculation when k_effective is zero."""
    reactor.k_effective = 0.0
    reactor.calculate_reactivity()
    assert reactor.reactivity == -float('inf')

def test_initialization(reactor):
    """Test that the reactor model initializes with default values."""
    assert reactor.control_rod_position == 0.0
    assert reactor.boron_concentration == 500.0
    assert reactor.moderator_temperature == 310.0
    assert reactor.power_level == 100.0
    assert reactor.fuel_enrichment == 3.5
    assert reactor.k_effective is not None
    assert reactor.reactivity is not None

def test_update_control_rod_position(reactor):
    """Test updating the control rod position."""
    reactor.update_control_rod_position(50)
    assert reactor.control_rod_position == 50

def test_update_boron_concentration(reactor):
    """Test updating the boron concentration."""
    reactor.update_boron_concentration(1000)
    assert reactor.boron_concentration == 1000

def test_update_moderator_temperature(reactor):
    """Test updating the moderator temperature."""
    reactor.update_moderator_temperature(320)
    assert reactor.moderator_temperature == 320

def test_update_power_level(reactor):
    """Test updating the power level."""
    reactor.update_power_level(80)
    assert reactor.power_level == 80

def test_update_fuel_enrichment(reactor):
    """Test updating the fuel enrichment."""
    reactor.update_fuel_enrichment(4.0)
    assert reactor.fuel_enrichment == 4.0

def test_fuel_temperature_calculation(reactor):
    """Test the calculation of fuel temperature."""
    from src.model import config
    reactor.update_moderator_temperature(300)
    reactor.update_power_level(50)
    expected_temp = 300 + (50 * config.POWER_TO_FUEL_TEMP_COEFF)
    assert reactor.fuel_temperature == pytest.approx(expected_temp)

def test_calculate_doubling_time(reactor):
    """Test doubling time calculation."""
    # Positive reactivity -> finite doubling time
    reactor.reactivity = 0.001
    reactor.calculate_doubling_time()
    assert reactor.doubling_time > 0 and reactor.doubling_time != float('inf')

    # Zero reactivity -> infinite doubling time
    reactor.reactivity = 0.0
    reactor.calculate_doubling_time()
    assert reactor.doubling_time == float('inf')

    # Negative reactivity -> infinite doubling time
    reactor.reactivity = -0.001
    reactor.calculate_doubling_time()
    assert reactor.doubling_time == float('inf')

def test_get_axial_flux_distribution(reactor):
    """Test the axial flux distribution calculation."""
    height, flux = reactor.get_axial_flux_distribution()
    assert len(height) == 100
    assert len(flux) == 100
    assert np.max(flux) == pytest.approx(1.0)

def test_get_four_factors_data(reactor):
    """Test the four factors data dictionary."""
    data = reactor.get_four_factors_data()
    expected_keys = ["eta", "epsilon", "p", "f", "k_infinite", "thermal_non_leakage_prob", "fast_non_leakage_prob", "k_effective"]
    for key in expected_keys:
        assert key in data

def test_get_neutron_balance_data(reactor):
    """Test the neutron balance data structure."""
    data = reactor.get_neutron_balance_data()
    assert "sections" in data
    assert "neutrons_produced_new" in data
    assert len(data["sections"]) == 6
    total_neutrons = sum(s["value"] for s in data["sections"])
    assert total_neutrons == pytest.approx(1000.0)

def test_get_axial_offset_data(reactor):
    """Test the axial offset calculation."""
    data = reactor.get_axial_offset_data()
    assert "axial_offset" in data
    assert "power_percentage" in data
    assert data["power_percentage"] == reactor.power_level

def test_presets(reactor):
    """Test preset management."""
    preset_names = reactor.get_preset_names()
    assert isinstance(preset_names, list)
    assert len(preset_names) > 0

    # Test applying a preset
    first_preset = preset_names[0]
    assert reactor.apply_preset(first_preset)
    
    # Check if a parameter has changed to what preset specifies
    # This assumes presets are not all identical to default
    from src.model import config
    preset_values = config.PRESETS[first_preset]
    assert reactor.control_rod_position == preset_values["control_rod_position"]

    # Test get current preset name
    assert reactor.get_current_preset_name() == first_preset

    # Modify a value and check if preset is 'Custom'
    reactor.update_control_rod_position(reactor.control_rod_position + 1)
    assert reactor.get_current_preset_name() == "Personnalisé"
    
    # Test saving a new preset
    new_preset_name = "My Test Preset"
    assert reactor.save_preset(new_preset_name)
    assert new_preset_name in reactor.get_preset_names()
    
    # Test overwriting a preset
    reactor.update_boron_concentration(999)
    assert reactor.save_preset(new_preset_name, overwrite=True)
    reactor.apply_preset(new_preset_name)
    assert reactor.boron_concentration == 999

    # Test applying non-existent preset
    assert not reactor.apply_preset("NonExistentPreset")

# --- Tests for OpenMC Integration ---

@patch('src.model.reactor_model.OpenMCModel')
def test_calculate_k_effective_with_openmc_success(mock_openmc_model, reactor):
    """
    Verify that calculate_k_effective calls the OpenMC model and uses its result.
    """
    # Configure the mock instance returned by OpenMCModel(params)
    mock_runner = MagicMock()
    mock_runner.run_simulation.return_value = 1.025
    mock_openmc_model.return_value = mock_runner

    # Call the method that should trigger the OpenMC calculation
    reactor.calculate_k_effective()

    # Verify that OpenMCModel was instantiated with the correct parameters
    mock_openmc_model.assert_called_once()
    params = mock_openmc_model.call_args[0][0]
    assert params['boron_concentration'] == reactor.boron_concentration
    assert params['moderator_temperature'] == reactor.moderator_temperature + 273.15 # Check Kelvin conversion

    # Verify that the simulation was run
    mock_runner.run_simulation.assert_called_once()

    # Verify that the reactor's k_effective is updated with the OpenMC result
    assert reactor.k_effective == 1.025

@patch('src.model.reactor_model.OpenMCModel')
def test_calculate_k_effective_with_openmc_failure_fallback(mock_openmc_model, reactor):
    """
    Verify that the model falls back to the analytical calculation if OpenMC fails.
    """
    # Store the initial k_effective from the analytical model
    initial_k_eff = reactor.k_effective

    # Configure the mock to raise an exception
    mock_runner = MagicMock()
    mock_runner.run_simulation.side_effect = Exception("OpenMC simulation failed")
    mock_openmc_model.return_value = mock_runner

    # Call the method that will attempt the OpenMC calculation
    reactor.calculate_k_effective()
    
    # Verify that the k_effective value is the result of the analytical calculation
    # (since the fixture-created reactor already ran calculate_all).
    # We re-run the analytical part to be sure.
    k_inf = reactor.eta * reactor.epsilon * reactor.p * reactor.f
    analytical_k_eff = k_inf * reactor.fast_non_leakage_prob * reactor.thermal_non_leakage_prob
    
    # Here, the logic is a bit tricky. The fallback runs the analytical model *again*.
    # Since the state hasn't changed, it should be the same as the initial state.
    assert reactor.k_effective == pytest.approx(initial_k_eff)
    # Ensure it did not get a value from a successful run
    assert reactor.k_effective != 1.025

def test_get_params_for_openmc(reactor):
    """
    Test the helper function that prepares parameters for OpenMC.
    """
    reactor.moderator_temperature = 300 # °C
    reactor.fuel_temperature = 600 # °C
    params = reactor._get_params_for_openmc()
    
    assert params["moderator_temperature"] == 300 + 273.15
    assert params["fuel_temperature"] == 600 + 273.15 