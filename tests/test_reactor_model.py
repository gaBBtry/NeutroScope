"""
Tests for the ReactorModel class
"""
import pytest
from src.model.reactor_model import ReactorModel

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