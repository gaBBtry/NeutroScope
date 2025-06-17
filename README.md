# NeutroScope

Application pédagogique interactive pour la neutronique des Réacteurs à Eau Pressurisée (REP).

## Fonctionnalités

- **Deux modes de calcul** :
  - ⚡ **Mode rapide** : Calculs analytiques instantanés
  - 🎯 **Mode précis** : Simulation Monte Carlo avec OpenMC
- **Visualisations interactives** : flux axial, quatre facteurs, bilan neutronique
- **Contrôles réalistes** : barres, bore, température, enrichissement
- **Interface pédagogique** avec préréglages et informations contextuelles

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone [url-du-repo]
   cd NeutroScope
   ```

2. **Environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou .venv\Scripts\activate  # Windows
   ```

3. **Dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Données OpenMC (optionnel)**
   
   Pour le mode précis, placer les données ENDF/B-VII.1 dans :
   ```
   data/endfb-vii.1-hdf5/cross_sections.xml
   ```

## Utilisation

```bash
python main.py
```

Au démarrage, choisissez votre mode :
- **Mode rapide** : Idéal pour l'apprentissage, aucune donnée requise
- **Mode précis** : Simulation haute fidélité, nécessite les données OpenMC

## Configuration

Les modes sont configurables dans `config.json`. L'application détecte automatiquement les données disponibles.

## Documentation

- [Guide des modes de calcul](MODES_CALCUL.md) : Détails sur les deux modes
- Interface : Panneau de contrôle (gauche), visualisations (centre), aide (touche `I`) 
``` 