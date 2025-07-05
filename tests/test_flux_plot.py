import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from src.gui.widgets.flux_plot import FluxDistributionPlot

@pytest.fixture(scope="session")
def qapp():
    """Fixture to create a QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def flux_plot(qapp):
    """Provides a FluxDistributionPlot instance with a mock parent."""
    from PyQt6.QtWidgets import QWidget
    
    parent_widget = QWidget()
    parent_widget.update_info_panel = MagicMock()
    
    plot = FluxDistributionPlot(parent=parent_widget)
    # Store a reference to the parent on the plot object to prevent it from
    # being garbage collected prematurely.
    plot._test_parent = parent_widget
    return plot

def test_flux_plot_initialization(flux_plot):
    """Test the initial state of the FluxDistributionPlot."""
    assert flux_plot.axes.get_title() == 'Distribution Axiale du Flux'
    assert flux_plot.axes.get_xlabel() == 'Flux neutronique relatif'
    assert flux_plot.axes.get_ylabel() == 'Hauteur relative du cœur'
    assert flux_plot.axes.get_ylim() == (0, 1)
    assert flux_plot.axes.get_xlim() == (0, 1.1)

def test_flux_plot_update_plot(flux_plot):
    """Test the update_plot method."""
    height = [0, 0.5, 1]
    flux = [0, 1, 0]
    rod_pos = 50.0  # 50% insertion from the top

    flux_plot.update_plot(height, flux, rod_pos)

    line_data = flux_plot.line.get_data()
    assert list(line_data[0]) == flux, "Flux data should be set as x-axis"
    assert list(line_data[1]) == height, "Height data should be set as y-axis"

    rod_line_y = flux_plot.rod_line.get_ydata()[0]
    expected_rod_height = 1.0 - (rod_pos / 100.0)
    assert rod_line_y == pytest.approx(expected_rod_height)

def test_on_mouse_move_updates_info_panel(flux_plot):
    """Test that on_mouse_move calls the parent's update_info_panel."""
    # Create a mock event object that simulates a mouse event
    mock_event = MagicMock()
    mock_event.inaxes = flux_plot.axes
    mock_event.xdata = 0.5
    mock_event.ydata = 0.5

    flux_plot.on_mouse_move(mock_event)

    # Verify that the parent's update_info_panel method was called
    flux_plot.parent().update_info_panel.assert_called_once()
    
    # Verify the content of the call
    args, _ = flux_plot.parent().update_info_panel.call_args
    assert isinstance(args[0], str)
    assert isinstance(args[1], str)
    assert "Hauteur relative : 0.50" in args[0]
    assert "Flux neutronique relatif : 0.50" in args[0]

def test_on_axes_leave_clears_info_panel(flux_plot):
    """Test that on_axes_leave calls update_info_panel with empty strings."""
    mock_event = MagicMock()  # The event object itself is not used in the method
    flux_plot.on_axes_leave(mock_event)
    flux_plot.parent().update_info_panel.assert_called_once_with("", "")

def test_on_mouse_move_outside_axes(flux_plot):
    """Test that on_mouse_move does nothing if the event is outside the axes."""
    mock_event = MagicMock()
    mock_event.inaxes = None  # Simulate event outside of the plot's axes

    flux_plot.on_mouse_move(mock_event)

    # Verify that update_info_panel was not called
    flux_plot.parent().update_info_panel.assert_not_called() 