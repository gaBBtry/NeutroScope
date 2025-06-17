"""
Tests for the OpenMCModel class.
These tests verify the construction of the OpenMC model and, optionally,
can run a quick simulation to ensure end-to-end functionality.
"""

import pytest
import os
import openmc
from src.model.openmc_model import OpenMCModel
from src.model import config as global_config

# --- Fixtures ---

@pytest.fixture
def default_params():
    """Default reactor parameters for testing."""
    return {
        "boron_concentration": 600.0,
        "moderator_temperature": 315.0 + 273.15,
        "fuel_temperature": 650.0 + 273.15,
        "fuel_enrichment": 4.5,
    }

@pytest.fixture
def openmc_model(default_params):
    """Provides an OpenMCModel instance."""
    return OpenMCModel(default_params)

# --- Unit Tests for Model Construction ---

def test_initialization(openmc_model, default_params):
    """Test that the model initializes correctly."""
    assert openmc_model.params == default_params
    assert openmc_model.model is None

def test_create_materials(openmc_model):
    """Test the material creation process."""
    openmc_model._create_materials()
    
    assert isinstance(openmc_model.materials, openmc.Materials)
    
    # Check that there is one homogenized core material
    assert len(openmc_model.materials) == 1
    core_mat = openmc_model.materials[0]
    assert core_mat.name == "Homogenized Core"

    # Verify enrichment is correctly applied
    # This is difficult to check directly on the mixed material.
    # We can infer it by checking the original UO2 definition inside the function.
    # For a more robust test, one might not homogenize in the test fixture.
    
    # Check temperature
    assert core_mat.temperature == pytest.approx(openmc_model.params['moderator_temperature'])

def test_create_geometry(openmc_model):
    """Test the geometry creation process."""
    # Materials must be created before geometry that uses them
    openmc_model._create_materials()
    openmc_model._create_geometry()
    
    assert isinstance(openmc_model.geometry, openmc.Geometry)
    
    # Check core dimensions
    matching_cells = openmc_model.geometry.get_cells_by_name("Core Cell")
    assert len(matching_cells) == 1
    core_cell = matching_cells[0]
    
    # Get the bounding box of the core cell region
    ll, ur = core_cell.region.bounding_box
    
    expected_radius = global_config.CORE_DIAMETER_M * 100 / 2.0
    expected_height = global_config.CORE_HEIGHT_M * 100
    
    assert ur[0] == pytest.approx(expected_radius)
    assert ll[0] == pytest.approx(-expected_radius)
    assert ur[2] == pytest.approx(expected_height / 2.0)
    assert ll[2] == pytest.approx(-expected_height / 2.0)

def test_create_settings(openmc_model):
    """Test the settings creation process."""
    openmc_model._create_settings()
    
    assert isinstance(openmc_model.settings, openmc.Settings)
    assert openmc_model.settings.run_mode == 'eigenvalue'
    assert openmc_model.settings.particles == 1000
    assert openmc_model.settings.batches == 20

def test_build_model(openmc_model):
    """Test the full model build process."""
    openmc_model.build_model()
    assert isinstance(openmc_model.model, openmc.model.Model)
    assert openmc_model.model.geometry is not None
    assert openmc_model.model.materials is not None
    assert openmc_model.model.settings is not None

# --- Tests for Simulation Execution ---

def test_run_simulation_no_cross_sections_env(openmc_model):
    """
    Verify that run_simulation raises a RuntimeError if the cross sections
    environment variable is not set.
    """
    # Ensure the environment variable is not set
    if 'OPENMC_CROSS_SECTIONS' in os.environ:
        del os.environ['OPENMC_CROSS_SECTIONS']
    
    with pytest.raises(RuntimeError, match="OPENMC_CROSS_SECTIONS environment variable is not set"):
        openmc_model.run_simulation()

@pytest.mark.slow
@pytest.mark.skipif('OPENMC_CROSS_SECTIONS' not in os.environ, reason="OPENMC_CROSS_SECTIONS env var not set")
def test_run_simulation_full(openmc_model):
    """
    (Optional) Run a quick, full simulation to check for errors.
    This is an integration test and may be slow.
    It requires the OPENMC_CROSS_SECTIONS environment variable to be set.
    """
    # Build the model
    openmc_model.build_model()
    
    # Make the simulation very fast for a test
    openmc_model.model.settings.batches = 5
    openmc_model.model.settings.inactive = 2
    openmc_model.model.settings.particles = 100
    
    # Run the simulation
    k_effective = openmc_model.run_simulation()
    
    # Check for a plausible result
    assert isinstance(k_effective, float)
    assert 0.5 < k_effective < 2.5 