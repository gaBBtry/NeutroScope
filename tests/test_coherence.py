"""
Tests de cohérence entre l'interface graphique (GUI) et le modèle de calcul.

Ces tests vérifient que les valeurs affichées dans l'interface utilisateur
reflètent correctement les valeurs calculées par le modèle du réacteur.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

# Crée une seule instance de QApplication pour tous les tests
@pytest.fixture(scope="session")
def qapp():
    """Fixture to create a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def app(qapp):
    """
    Provides a MainWindow instance for tests.
    Using qapp fixture to ensure QApplication is created.
    """
    window = MainWindow()
    # On s'assure que la fenêtre est affichée pour que les widgets soient actifs
    window.show()
    return window

def test_initial_state_coherence(app):
    """
    Teste si l'état initial (après chargement du preset par défaut)
    est cohérent entre le modèle et l'IHM.
    """
    # Le preset "Critique à puissance nominale" est chargé par défaut
    model = app.controller.model

    # Récupérer les valeurs du modèle
    k_eff_model = model.k_effective
    reactivity_model_pcm = model.reactivity * 100000

    # Récupérer les valeurs de l'IHM
    k_eff_gui_text = app.k_effective_label.text()
    reactivity_gui_text = app.reactivity_label.text()

    # Extraire les nombres des textes de l'IHM
    k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
    reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

    # Vérifier la cohérence
    assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1)

def test_preset_coherence(app, qtbot):
    """
    Teste la cohérence pour différents préréglages.
    """
    model = app.controller.model
    presets = app.controller.get_preset_names()

    for preset_name in presets:
        # Si le preset est déjà sélectionné, on ne fait rien pour éviter un timeout
        if app.preset_combo.currentText() == preset_name:
            continue
            
        # Changer de preset dans l'IHM
        # On attend que le signal soit traité
        with qtbot.waitSignal(app.preset_combo.currentTextChanged, timeout=1000):
            app.preset_combo.setCurrentText(preset_name)

        # Récupérer les valeurs du modèle après changement
        k_eff_model = model.k_effective
        reactivity_model_pcm = model.reactivity * 100000

        # Récupérer les valeurs de l'IHM
        k_eff_gui_text = app.k_effective_label.text()
        reactivity_gui_text = app.reactivity_label.text()
        
        # Extraire les nombres
        k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
        reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

        # Vérifier la cohérence
        assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5), f"k_effective mismatch for preset {preset_name}"
        assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1), f"Reactivity mismatch for preset {preset_name}"

def test_control_rod_slider_coherence(app, qtbot):
    """
    Teste la cohérence après avoir modifié la position des barres de contrôle via le slider.
    """
    model = app.controller.model
    new_rod_position = 50

    # Modifier la valeur du slider
    app.rod_slider.setValue(new_rod_position)
    
    # La modification du slider déclenche les calculs. Pas besoin de waitSignal ici car c'est synchrone.
    # On peut directement vérifier les valeurs.

    # Récupérer les valeurs du modèle
    k_eff_model = model.k_effective
    reactivity_model_pcm = model.reactivity * 100000

    # Récupérer les valeurs de l'IHM
    k_eff_gui_text = app.k_effective_label.text()
    reactivity_gui_text = app.reactivity_label.text()

    # Extraire les nombres
    k_eff_gui = float(k_eff_gui_text.split(":")[1].strip())
    reactivity_gui_pcm = float(reactivity_gui_text.split(":")[1].strip().split(" ")[0])

    # Vérifier la cohérence
    assert k_eff_gui == pytest.approx(k_eff_model, abs=1e-5)
    assert reactivity_gui_pcm == pytest.approx(reactivity_model_pcm, abs=1e-1)
    
    # Vérifier aussi la position de la barre dans le modèle
    assert model.control_rod_position == new_rod_position 