"""
Tests for the ReactorController class
"""
import pytest
from unittest.mock import MagicMock, patch
from src.controller.reactor_controller import ReactorController

@pytest.fixture
def controller():
    """Provides a ReactorController instance with a mocked model."""
    with patch('src.controller.reactor_controller.ReactorModel') as mock_model_class:
        # This instantiation will call mock_model_class() once.
        # The controller's model attribute will be the instance created by the mock.
        controller_instance = ReactorController()
        yield controller_instance, mock_model_class

def test_initialization(controller):
    """Test controller initialization."""
    ctr, mock_class = controller
    assert ctr is not None
    assert ctr.model is not None
    # Check that the model class was instantiated exactly once.
    mock_class.assert_called_once()

def test_update_control_rod_position(controller):
    """Test updating control rod position calls the model."""
    ctr, _ = controller
    ctr.update_control_rod_position(50)
    ctr.model.update_control_rod_position.assert_called_once_with(50)

def test_update_boron_concentration(controller):
    """Test updating boron concentration calls the model."""
    ctr, _ = controller
    ctr.update_boron_concentration(1000)
    ctr.model.update_boron_concentration.assert_called_once_with(1000)

def test_update_average_temperature(controller):
    """Test updating moderator temperature calls the model."""
    ctr, _ = controller
    ctr.update_average_temperature(320)
    ctr.model.update_average_temperature.assert_called_once_with(320)

def test_update_fuel_enrichment(controller):
    """Test updating fuel enrichment calls the model."""
    ctr, _ = controller
    ctr.update_fuel_enrichment(4.0)
    ctr.model.update_fuel_enrichment.assert_called_once_with(4.0)

def test_get_reactor_parameters(controller):
    """Test getting reactor parameters from the model."""
    ctr, _ = controller
    # Configure the mock model to return specific values
    ctr.model.k_effective = 1.01
    ctr.model.reactivity = 0.01
    ctr.model.doubling_time = 100
    ctr.model.delayed_neutron_fraction = 0.0065

    params = ctr.get_reactor_parameters()
    expected_params = {
        "k_effective": 1.01,
        "reactivity": 0.01,
        "doubling_time": 100,
        "delayed_neutron_fraction": 0.0065
    }
    assert params == expected_params

def test_get_axial_flux_distribution(controller):
    """Test getting axial flux distribution from the model."""
    ctr, _ = controller
    ctr.get_axial_flux_distribution()
    ctr.model.get_axial_flux_distribution.assert_called_once()

def test_get_four_factors_data(controller):
    """Test getting four factors data from the model."""
    ctr, _ = controller
    ctr.get_four_factors_data()
    ctr.model.get_four_factors_data.assert_called_once()

def test_get_neutron_balance_data(controller):
    """Test getting neutron balance data from the model."""
    ctr, _ = controller
    ctr.get_neutron_balance_data()
    ctr.model.get_neutron_balance_data.assert_called_once()

def test_get_axial_offset_data(controller):
    """Test getting axial offset data from the model."""
    ctr, _ = controller
    ctr.get_axial_offset_data()
    ctr.model.get_axial_offset_data.assert_called_once()

def test_get_preset_names(controller):
    """Test getting preset names from the model."""
    ctr, _ = controller
    ctr.get_preset_names()
    ctr.model.get_preset_names.assert_called_once()

def test_apply_preset(controller):
    """Test applying a preset calls the model."""
    ctr, _ = controller
    preset_name = "test_preset"
    # Mock the return value of apply_preset
    ctr.model.apply_preset.return_value = True
    # Mock model attributes that will be accessed
    ctr.model.control_rod_position = 10
    ctr.model.boron_concentration = 20
    ctr.model.average_temperature = 30
    ctr.model.fuel_enrichment = 4.0
    
    result = ctr.apply_preset(preset_name)
    
    ctr.model.apply_preset.assert_called_once_with(preset_name)
    assert result is not None
    assert result["control_rod_position"] == 10

def test_apply_preset_failure(controller):
    """Test applying a non-existent preset."""
    ctr, _ = controller
    preset_name = "non_existent_preset"
    ctr.model.apply_preset.return_value = False
    
    result = ctr.apply_preset(preset_name)
    
    ctr.model.apply_preset.assert_called_once_with(preset_name)
    assert result is None

def test_get_current_preset_name(controller):
    """Test getting the current preset name from the model."""
    ctr, _ = controller
    ctr.get_current_preset_name()
    ctr.model.get_current_preset_name.assert_called_once()

def test_save_preset(controller):
    """Test saving a preset calls the model."""
    ctr, _ = controller
    ctr.save_preset("new_preset", overwrite=True)
    ctr.model.save_preset.assert_called_once_with("new_preset", True)

def test_get_current_configuration(controller):
    """Test getting current configuration from the model."""
    ctr, _ = controller
    # Configure mock attributes
    ctr.model.control_rod_position = 10
    ctr.model.boron_concentration = 20
    ctr.model.average_temperature = 30
    ctr.model.fuel_enrichment = 4.0

    config = ctr.get_current_configuration()
    
    expected_config = {
        "control_rod_position": 10,
        "boron_concentration": 20,
        "average_temperature": 30,
        "fuel_enrichment": 4.0
    }
    assert config == expected_config 