"""
OpenMC model for the reactor
"""
import openmc
from ..model import config as global_config
from ..model.config import setup_openmc_data
import tempfile
import os
from pathlib import Path

class OpenMCModel:
    """
    This class will be responsible for building and running the OpenMC model
    of the reactor.
    """
    def __init__(self, reactor_params):
        """
        Initializes the OpenMC model.
        
        Parameters:
        -----------
        reactor_params: dict
            A dictionary containing the reactor parameters from the main model,
            e.g., {'boron_concentration': 500, 'moderator_temperature': 310, ...}
        """
        self.params = reactor_params
        self.model = None

    def build_model(self):
        """
        Builds the OpenMC model (geometry, materials, settings).
        This is where the main logic for creating the reactor model will go.
        """
        # Create materials, geometry, and settings
        self._create_materials()
        self._create_geometry()
        self._create_settings()
        
        # Create a model object that ties them all together
        self.model = openmc.model.Model(
            geometry=self.geometry,
            materials=self.materials,
            settings=self.settings
        )

    def _create_materials(self):
        """Create materials for the OpenMC model."""
        
        # --- Fuel Material (UO2) ---
        # Get enrichment from parameters. Enrichment is in weight percent.
        enrichment_wo = self.params.get('fuel_enrichment', 3.5)
        fuel_temp_K = self.params.get('fuel_temperature', 873.15) # Default 600°C
        
        # Convert U enrichment from weight percent to atom percent for easier material definition
        w5 = enrichment_wo / 100.0
        w8 = 1.0 - w5
        # Using nominal masses, a more precise calculation would use nuclide masses from a library
        m5 = 235.0
        m8 = 238.0
        a5_norm = w5 / m5
        a8_norm = w8 / m8
        enrichment_ao = (a5_norm / (a5_norm + a8_norm)) * 100.0

        # Create a UO2 material using atom fractions.
        uo2 = openmc.Material(name='UO2')
        uo2.set_density('g/cm3', 10.5)
        # Ratios are 1 U atom to 2 O atoms.
        # Proportions for nuclides will be normalized by OpenMC.
        # The total amount of U is 100 parts, for 200 parts of O.
        uo2.add_nuclide('U235', enrichment_ao * (100.0/100.0), 'ao')
        uo2.add_nuclide('U238', (100.0 - enrichment_ao) * (100.0/100.0), 'ao')
        uo2.add_nuclide('O16', 200.0, 'ao') # 2 O atoms for every 1 U atom (100% total U)
        uo2.temperature = fuel_temp_K
        
        # --- Moderator Material (Borated Water) ---
        mod_temp_K = self.params.get('moderator_temperature', 583.15) # Default 310°C
        boron_ppm = self.params.get('boron_concentration', 500.0)
        
        # Create a borated water material using weight fractions to avoid mixing percent types.
        water = openmc.Material(name='Borated Water')
        water.set_density('g/cm3', 0.7) # Density of water at ~300 C

        # Weight fractions of H and O in pure water
        # Using nominal masses
        m_H = 1.008
        m_O = 15.999
        m_H2O = 2 * m_H + m_O
        w_H_in_H2O = (2 * m_H) / m_H2O
        w_O_in_H2O = m_O / m_H2O

        # Boron concentration is given in ppm (parts per million) by weight.
        w_B = boron_ppm * 1e-6
        w_H2O = 1.0 - w_B

        # Add nuclides with their final weight fractions in the borated water.
        water.add_nuclide('H1', w_H_in_H2O * w_H2O, 'wo')
        water.add_nuclide('O16', w_O_in_H2O * w_H2O, 'wo')
        water.add_element('B', w_B, 'wo') # Use element B for natural abundance
        water.temperature = mod_temp_K
        
        # --- Homogenized Core Material ---
        # For this simple model, we will homogenize the fuel and moderator.
        # A typical PWR has a moderator-to-fuel volume ratio of about 2.
        V_mod_V_fuel = 2.0
        
        # The `mix_materials` function creates a new material by mixing others.
        # It can mix by volume fraction ('vo') or atom fraction ('ao').
        # We normalize the fractions to avoid warnings.
        total_vol = 1.0 + V_mod_V_fuel
        core_material = openmc.Material.mix_materials(
            [uo2, water],
            [1.0 / total_vol, V_mod_V_fuel / total_vol],
            'vo',
            name='Homogenized Core'
        )
        # Add thermal scattering data to the homogenized material
        core_material.add_s_alpha_beta('c_H_in_H2O')
        core_material.temperature = mod_temp_K
        
        # The Materials object is a collection of all materials used in the model.
        self.materials = openmc.Materials([core_material])

    def _create_geometry(self):
        """Create the geometry for the OpenMC model."""
        
        # Get core dimensions from the global configuration
        radius_cm = global_config.CORE_DIAMETER_M * 100 / 2.0
        height_cm = global_config.CORE_HEIGHT_M * 100
        
        # Create a cylinder representing the reactor core.
        # Surfaces are infinite, so we define a cylinder along the z-axis.
        core_cylinder = openmc.ZCylinder(r=radius_cm, name='Core Cylinder')
        
        # Create planes for the top and bottom of the core.
        # half_space=+1 means the region z > z0
        top_plane = openmc.ZPlane(z0=height_cm / 2.0, name='Core Top')
        bottom_plane = openmc.ZPlane(z0=-height_cm / 2.0, name='Core Bottom')
        
        # A "Region" is a boolean combination of surfaces.
        # -surface means the region with negative values of the surface equation
        # (e.g., inside a cylinder).
        core_region = -core_cylinder & -top_plane & +bottom_plane
        
        # A "Cell" is a region of space filled with a material.
        # We get the 'Homogenized Core' material from our self.materials list.
        core_cell = openmc.Cell(
            name='Core Cell',
            fill=self.materials[0],
            region=core_region
        )
        
        # Create a bounding box for the whole model.
        # This is important for termination of particles.
        # We make it a bit larger than the core.
        x_extent = radius_cm * 2.5
        y_extent = radius_cm * 2.5
        z_extent = height_cm * 1.5
        bounding_surface = openmc.model.RectangularParallelepiped(
            -x_extent/2, x_extent/2, -y_extent/2, y_extent/2, -z_extent/2, z_extent/2,
            boundary_type='vacuum'
        )
        bound_box = -bounding_surface
        
        # The region outside the core cell within the bounding box will be a vacuum.
        vacuum_cell = openmc.Cell(
            name='Vacuum Cell',
            fill=None, # No material = vacuum
            region=bound_box & ~core_region # ~ is the NOT operator
        )
        
        # A "Universe" is a collection of cells. The root universe is the base of the geometry.
        root_universe = openmc.Universe(
            name='Root Universe',
            cells=[core_cell, vacuum_cell]
        )
        
        # The Geometry object contains the root universe.
        self.geometry = openmc.Geometry(root_universe)

    def _create_settings(self):
        """Create the settings for the OpenMC model."""
        height_cm = global_config.CORE_HEIGHT_M * 100
        self.settings = openmc.Settings()
        
        # Tell OpenMC this is a k-eigenvalue calculation
        self.settings.run_mode = 'eigenvalue'
        
        # Set the number of particles and batches.
        # For a quick pedagogical simulation, these values are low.
        # For accurate results, they should be much higher.
        self.settings.batches = 20
        self.settings.inactive = 5 # Inactive batches are for source convergence
        self.settings.particles = 1000
        
        # Enable temperature interpolation for cross sections
        self.settings.temperature = {'method': 'interpolation'}
        
        # Define the initial source distribution.
        # We can create a simple point source at the center of the core.
        source_box = openmc.stats.Box(
            [-1, -1, -height_cm/4], 
            [1, 1, height_cm/4]
        )
        self.settings.source = openmc.IndependentSource(space=source_box)
        
        # Set output options
        self.settings.output = {'tallies': False, 'summary': True}


    def run_simulation(self):
        """
        Runs the OpenMC simulation and returns the k_effective value.
        """
        if self.model is None:
            self.build_model()
            
        # Run OpenMC in a temporary directory to avoid cluttering the project root
        with tempfile.TemporaryDirectory() as tmpdir:
            # We need to check if the cross sections are defined.
            # OpenMC will look for the OPENMC_CROSS_SECTIONS environment variable.
            if not setup_openmc_data():
                raise RuntimeError(
                    "Unable to locate OpenMC cross sections data. "
                    "Please ensure cross_sections.xml is available in the data directory "
                    "or set the OPENMC_CROSS_SECTIONS environment variable."
                )

            # The model.run() method can take a 'cwd' argument to specify the directory.
            # However, since some file paths might be relative, it's often safer
            # to temporarily change the current working directory.
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # This will run the simulation in the temporary directory.
                sp_path = self.model.run(output=False)

                # After the run, we need to read the results from the statepoint file.
                with openmc.StatePoint(sp_path) as sp:
                    k_eff = sp.keff.n
                    
            finally:
                # Always change back to the original directory
                os.chdir(original_cwd)
                
        return k_eff 