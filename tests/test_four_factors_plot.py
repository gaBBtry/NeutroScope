import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QWidget
from src.gui.widgets.four_factors_plot import FourFactorsPlot

# QApplication fixture maintenant dans conftest.py

@pytest.fixture
def factors_plot(qapp):
    parent_widget = QWidget()
    parent_widget.update_info_panel = MagicMock()
    plot = FourFactorsPlot(parent=parent_widget)
    plot._test_parent = parent_widget
    return plot

def test_four_factors_plot_initialization(factors_plot):
    """Test the initial state of the FourFactorsPlot."""
    assert factors_plot.axes.get_title() == 'Facteurs du Cycle Neutronique'
    assert factors_plot.axes.get_xlabel() == 'Facteur'
    assert factors_plot.axes.get_ylabel() == 'Valeur'

def get_sample_factors_data():
    return {
        'eta': 2.0, 'epsilon': 1.05, 'p': 0.8, 'f': 0.9,
        'k_infinite': 1.512, 'thermal_non_leakage_prob': 0.95,
        'fast_non_leakage_prob': 0.97, 'k_effective': 1.385
    }

def test_four_factors_update_plot(factors_plot):
    """Test the update_plot method."""
    data = get_sample_factors_data()
    factors_plot.update_plot(data)
    
    # Check if the number of bars is correct
    assert len(factors_plot.bars) == 8
    
    # Check if the critical line is drawn
    assert factors_plot.critical_line is not None
    assert factors_plot.critical_line.get_ydata()[0] == 1
    
    # Check if annotations are created for k_inf and k_eff
    assert len(factors_plot.value_annotations) == 2

def test_four_factors_on_mouse_move(factors_plot):
    """Test mouse move event for tooltips."""
    data = get_sample_factors_data()
    factors_plot.update_plot(data)
    
    # Mock an event over one of the bars
    mock_event = MagicMock()
    mock_event.inaxes = factors_plot.axes
    
    # To simulate containment, we need a bit more setup
    # We'll trigger the check manually
    with patch.object(factors_plot.bars[0], 'contains', return_value=(True, {})):
        factors_plot.on_mouse_move(mock_event)

    factors_plot.parent().update_info_panel.assert_called_once()
    args, _ = factors_plot.parent().update_info_panel.call_args
    assert "Facteur de reproduction (η)" in args[0]
    
def test_four_factors_on_axes_leave(factors_plot):
    """Test that leaving the axes clears the info panel."""
    factors_plot.on_axes_leave(None)
    factors_plot.parent().update_info_panel.assert_called_once_with("") 