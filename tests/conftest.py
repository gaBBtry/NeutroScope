"""
Configuration commune pour tous les tests pytest de NeutroScope.
Centralise les fixtures communes pour éliminer les redondances.
"""
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """
    Fixture commune pour QApplication partagée entre tous les tests.
    Élimine la redondance de création QApplication dans chaque test de widget.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit() 