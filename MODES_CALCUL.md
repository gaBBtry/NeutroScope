# Modes de Calcul de NeutroScope

NeutroScope propose désormais **deux modes de calcul** pour s'adapter à différents besoins d'utilisation :

## 🚀 Mode Rapide (Analytique)

- **Utilisation** : Calculs instantanés basés sur un modèle analytique simplifié
- **Avantages** :
  - ⚡ **Très rapide** : Résultats immédiats
  - 📱 **Léger** : Aucune donnée externe requise
  - 🎓 **Pédagogique** : Idéal pour comprendre les concepts de base
  - 🔧 **Accessible** : Fonctionne sur toutes les machines

- **Idéal pour** :
  - L'apprentissage des concepts de neutronique
  - L'exploration interactive des paramètres
  - Les démonstrations rapides
  - Les situations sans accès aux données OpenMC

## 🎯 Mode Précis (OpenMC)

- **Utilisation** : Simulation Monte Carlo complète avec OpenMC
- **Avantages** :
  - 🎯 **Haute précision** : Calculs Monte Carlo rigoureux
  - 🔬 **Réaliste** : Modélisation physique détaillée
  - 📊 **Professionnel** : Résultats comparables aux outils industriels
  - 🌐 **Complet** : Prend en compte tous les phénomènes physiques

- **Idéal pour** :
  - Les études approfondies
  - La validation de calculs
  - Les projets de recherche
  - Les applications professionnelles

- **Requis** :
  - Données nucléaires ENDF/B-VII.1 dans le dossier `data/`
  - Plus de temps de calcul (quelques secondes)

## 🔄 Changement de Mode

### Au démarrage
L'application vous demande automatiquement de choisir votre mode préféré au premier lancement.

### Configuration automatique
- **Données trouvées** : Si les données OpenMC sont disponibles dans `data/endfb-vii.1-hdf5/`, l'application propose automatiquement le mode précis
- **Données manquantes** : L'application proposera le mode rapide ou vous permettra de localiser les données

### Indicateur visuel
L'interface affiche en permanence le mode actuel :
- ⚡ **Mode rapide** : Icône bleue avec description
- 🎯 **Mode précis** : Icône verte avec description

## 📁 Structure des Données

Pour utiliser le mode précis, placez vos données nucléaires dans :
```
NeutroScope/
└── data/
    └── endfb-vii.1-hdf5/
        ├── cross_sections.xml
        ├── neutron/
        ├── photon/
        └── wmp/
```

## ⚙️ Configuration Avancée

Les modes sont configurables via `config.json` :

```json
{
  "openmc": {
    "default_mode": "auto",
    "data_path": "data/endfb-vii.1-hdf5"
  },
  "calculation_modes": {
    "fast": {
      "name": "Mode rapide (analytique)",
      "use_openmc": false
    },
    "precise": {
      "name": "Mode précis (OpenMC)",
      "use_openmc": true
    }
  }
}
```

## 🤝 Avantages Pédagogiques

Cette approche à deux modes permet :

1. **Progression graduelle** : Commencer par les concepts de base puis approfondir
2. **Comparaison** : Observer les différences entre modèles simplifiés et détaillés
3. **Flexibilité** : Adapter l'outil au niveau et aux objectifs de chaque utilisateur
4. **Accessibilité** : Utiliser l'outil même sans données spécialisées

## 📊 Comparaison des Modes

| Aspect | Mode Rapide | Mode Précis |
|--------|-------------|-------------|
| **Temps de calcul** | < 1 ms | 1-10 s |
| **Précision** | Éducative | Industrielle |
| **Dépendances** | Aucune | Données ENDF |
| **Complexité** | Simplifiée | Complète |
| **Utilisation** | Apprentissage | Recherche/Pro |

---

💡 **Conseil** : Commencez par le mode rapide pour vous familiariser avec les concepts, puis passez au mode précis pour des analyses approfondies ! 