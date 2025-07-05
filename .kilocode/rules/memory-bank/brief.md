# Project Brief: NeutroScope

## Objective
NeutroScope is an interactive and educational desktop application designed for simulating the neutronics of a Pressurized Water Reactor (PWR). Its primary goal is to provide a pedagogical tool for understanding core reactor physics principles.

## Key Features
- **Interactive Control Panel:** Allows users to manipulate key reactor parameters in real-time, including control rod position, boron concentration, moderator temperature, and fuel enrichment.
- **Real-time Visualization:** Features a comprehensive dashboard with plots for axial neutron flux, the four factors, neutron balance, and a pilotage diagram, providing immediate visual feedback on parameter changes.
- **Dual Calculation Modes:** 
  - A **fast, analytical mode** for quick, qualitative analysis.
  - A **precise, high-fidelity mode** that leverages the OpenMC Monte Carlo particle transport code for accurate simulations.
- **Preset Scenarios:** Includes pre-configured states like "Startup," "Critical at Nominal Power," and "End of Cycle" to guide learning.

## Technologies Used
- **Language:** Python
- **GUI:** PyQt6
- **Scientific Computing & Plotting:** NumPy, Matplotlib
- **Core Simulation Engine:** OpenMC (for precise mode) and internal analytical models.
- **Testing:** Pytest, pytest-qt

## Significance
NeutroScope bridges the gap between theoretical reactor physics and practical operational behavior. It offers a user-friendly, hands-on environment for students, educators, and engineers to explore and visualize complex neutronic phenomena without the steep learning curve of traditional simulation software.