# Context: Memory Bank Initialization

## Current Focus
- The current task is the initialization of the Memory Bank for the NeutroScope project.

## Recent Changes
- This is the first action in this session.
- An exhaustive analysis of the project structure, source code, and dependencies has been performed.
- The core Memory Bank files (`product.md`, `architecture.md`, `tech.md`, `context.md`) have been created based on this analysis.

## Current Status

The project has undergone a major refactoring to align with the `brief.md`. The application is now a focused, educational tool for visualizing the neutron life cycle.

### Key Accomplishments
- **OpenMC Removal**: All code and dependencies related to the OpenMC simulation engine have been removed. The application now uses a single, analytical model based on the six-factor formula.
- **New `NeutronCyclePlot` Widget**: A new, central widget has been created to visualize the neutron cycle in a clear, circular layout, free of overlaps.
- **Test Suite Improvement**: Added comprehensive tests for the `FluxDistributionPlot` and `FourFactorsPlot` widgets, increasing total test coverage to over 70%.
- **Documentation Update**: The Memory Bank files (`architecture.md`, `product.md`, `tech.md`) have been updated to reflect the new, simplified architecture.

### Next Steps
- Continue to improve test coverage for the remaining GUI widgets.
- Refine the info-panel content to ensure it is clear, concise, and pedagogically valuable.
- Begin work on the "universal info-bubble" feature as described in the brief.

## Next Steps
- Present the newly created Memory Bank files to the user for review and verification.
- Ask the user to confirm the accuracy of the documented information.
- Await further instructions from the user. 