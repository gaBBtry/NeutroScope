# Simulation Temps Réel - NeutroScope

## Vue d'ensemble

NeutroScope intègre désormais un système de **simulation temps réel** qui permet d'observer l'évolution dynamique continue du réacteur à 1 hertz. Cette fonctionnalité transforme le simulateur d'un outil d'analyse statique en une plateforme de simulation temporelle avancée.

## Fonctionnalités Principales

### Moteur de Simulation Temps Réel
- **Fréquence fixe** : Avancement automatique à 1Hz (1 calcul par seconde)
- **Vitesse variable** : De 1 seconde simulée/seconde réelle à 1 heure simulée/seconde réelle
- **Mapping logarithmique** : Contrôle fluide de la vitesse via curseur
- **Haute précision** : Utilise l'architecture temporelle Xénon existante

### Contrôles Type Lecteur Multimédia

#### Boutons de Contrôle
- **▶ (Play)** : Démarre la simulation temps réel
- **⏸⏸ (Pause)** : Met en pause la simulation (garde l'état actuel)
- **⏹ (Stop)** : Arrête et remet à zéro le temps de simulation

#### Curseur de Vitesse Temporelle
- **Plage** : 1 s/s à 3600 s/s (1 h/s)
- **Affichage dynamique** : Vitesse actuelle en s/s, min/s ou h/s
- **Graduation** : Ticks visuels pour référence
- **Mapping logarithmique** : Contrôle précis aux faibles vitesses, plage étendue aux hautes vitesses

## Interface Utilisateur

### Localisation des Contrôles
Les contrôles de simulation temps réel sont situés dans le **panneau de contrôle gauche**, immédiatement sous la section "Préréglages".

### Informations Affichées
- **État actuel** : "Simulation en cours", "Simulation en pause", "Simulation arrêtée"
- **Vitesse actuelle** : Affichage en temps réel de la vitesse sélectionnée
- **Temps simulé** : Temps total simulé en heures ou jours
- **Indicateur visuel** : Boutons activés/désactivés selon l'état

### Interaction avec Autres Contrôles
- **Pendant simulation** : Les contrôles manuels Xénon sont désactivés
- **Paramètres réacteur** : Modification possible en temps réel (bore, barres, température)
- **Visualisations** : Mise à jour automatique continue à 1Hz

## Utilisation Pratique

### Démarrage d'une Simulation
1. **Configurer l'état initial** : Choisir un preset ou ajuster manuellement les paramètres
2. **Sélectionner la vitesse** : Utiliser le curseur pour définir la vitesse temporelle désirée
3. **Démarrer** : Appuyer sur le bouton ▶ pour lancer la simulation
4. **Observer** : Les graphiques se mettent à jour automatiquement

### Scénarios d'Usage Typiques

#### Étude de la Dynamique Xénon
```
1. Preset "Fonctionnement Xénon équilibre" (100% puissance)
2. Vitesse : 10-60 s/s pour observation détaillée
3. Play → Observer l'évolution des concentrations
4. Modifier puissance en cours de simulation → Observer effets transitoires
```

#### Simulation d'Arrêt Réacteur
```
1. Preset "Critique à puissance nominale"
2. Vitesse : 30-300 s/s pour observation rapide
3. Play → Démarrer simulation
4. Réduire puissance à 0% en cours → Observer pic Xénon
5. Pause/Stop selon besoin d'analyse
```

#### Formation Opérateurs
```
1. Preset "Démarrage"
2. Vitesse : 1-10 s/s pour formation détaillée
3. Play → Simulation temps quasi-réel
4. Exercices de pilotage en temps réel
5. Pause pour explications, reprise pour practice
```

## Avantages Pédagogiques

### Compréhension Temporelle
- **Phénomènes lents** : Visualisation accélérée de l'évolution Xénon
- **Cause-effet** : Observation immédiate des conséquences des actions
- **Continuité** : Compréhension des transitions et régimes transitoires

### Flexibilité d'Apprentissage
- **Vitesse adaptable** : Du temps réel à l'accéléré selon besoins pédagogiques
- **Contrôle total** : Pause, modification, reprise selon rythme d'apprentissage
- **Expérimentation** : Test d'hypothèses en temps accéléré

### Authenticité Opérationnelle
- **Pilotage en temps réel** : Experience proche de la conduite réelle
- **Pression temporelle** : Apprentissage de la gestion du temps en situation
- **Réactivité** : Développement des réflexes opérationnels

## Aspects Techniques

### Architecture Logicielle
- **RealtimeSimulationEngine** : Moteur central basé sur QTimer
- **Intégration MVC** : Utilise l'architecture existante sans modifications majeures
- **Performance** : Calculs optimisés pour maintenir 1Hz stable
- **Signaux Qt** : Communication asynchrone avec l'interface

### Gestion de l'État
- **Synchronisation** : État cohérent entre simulation manuelle et automatique
- **Persistance** : Temps simulé conservé pendant pause
- **Reset complet** : Remise à zéro sur stop (temps + concentrations Xénon)
- **Historique** : Conservation des données pour visualisations continues

### Optimisations
- **Solutions analytiques** : Équations de Bateman résolues exactement
- **Mise à jour sélective** : Recalcul uniquement des paramètres modifiés
- **Gestion mémoire** : Limitation historique graphiques pour performance
- **Thread principal** : Exécution dans le thread UI pour simplicité

## Limitations et Considérations

### Limitations Actuelles
- **Vitesse maximale** : 1 h/s (3600 s/s) pour maintenir précision
- **Fréquence fixe** : 1Hz non configurable (optimisé pour fluidité UI)
- **Mono-threading** : Exécution dans thread principal (acceptable pour charges actuelles)

### Considérations d'Usage
- **Vitesses élevées** : Phénomènes rapides peuvent être manqués à haute vitesse
- **Modification en cours** : Changements de paramètres créent discontinuités dans historique
- **Ressources système** : Consommation CPU constante pendant simulation

## Extensions Futures Possibles

### Fonctionnalités Avancées
- **Vitesse variable dynamique** : Accélération/décélération automatique selon phénomènes
- **Enregistrement/Replay** : Sauvegarde et relecture de sessions
- **Points d'arrêt** : Pause automatique sur conditions définies
- **Simulation distribuée** : Multi-threading pour simulations complexes

### Intégrations Possibles
- **Procédures opérationnelles** : Séquences automatisées de manipulation
- **Formation scénarisée** : Exercices guidés avec objectifs temporels
- **Analyse statistique** : Métriques de performance opérateur
- **Interface réseau** : Simulation multi-utilisateurs

## Conclusion

La simulation temps réel transforme NeutroScope en un outil pédagogique de niveau professionnel, permettant une compréhension approfondie des phénomènes temporels dans les réacteurs nucléaires. L'interface intuitive et la performance optimisée offrent une expérience d'apprentissage immersive et authentique, préparant efficacement les apprenants aux défis opérationnels réels. 