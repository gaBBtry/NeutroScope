# Brief de Projet : Logiciel de Simulation Pédagogique NeutroScope

## 1. Titre du Projet

**NeutroScope**

## 2. Objectif Principal

L'objectif est de développer un logiciel de simulation interactif, **NeutroScope**, conçu comme un outil fondamental et introductif. Il s'adresse aux animateurs et apprenants en amont de formations plus appliquées au pilotage de réacteur. Le but est de solidifier la compréhension des principes physiques de base en permettant de visualiser et manipuler les concepts qui régissent la réaction en chaîne et la criticité. Ce programme se concentre sur le **cycle neutronique**, qui est l'élément central et le cœur de la simulation, pour préparer efficacement les apprenants aux aspects pratiques du pilotage en situation normale.

## 3. Concept et Fonctionnalités Clés

L'interface se voudra claire, moderne, visuellement intuitive et **exclusivement en français**. Elle utilisera des codes couleur cohérents et des animations fluides. Le programme doit être riche en données et informations pertinentes, présentées de manière accessible pour l'apprenant. Conformément à son objectif introductif, le cœur de NeutroScope est une représentation interactive du cycle de vie des neutrons dans un réacteur, illustrant comment une population de neutrons évolue d'une génération à l'autre. L'utilisateur doit pouvoir agir sur des paramètres clés pour voir leur impact en temps réel sur l'équilibre du réacteur.

### 3.1. Interface Principale : Le Cycle Neutronique

L'écran principal affichera une boucle visuelle, claire et fléchée, représentant les étapes fondamentales de la vie d'une génération de neutrons.
La visualisation doit donc parfaitement représenter le cycle présent dans docs/png-to-UI.png, mais avec les fuites en plus.

- **Point de départ** : La simulation commence avec une population de départ de neutrons **rapides** (issus de la fission), par exemple N = 1000.

- **Étape 1 : Facteur de fission rapide (ε)**
  - Les neutrons rapides peuvent provoquer quelques fissions supplémentaires dans le combustible avant de ralentir, augmentant légèrement la population de neutrons.
  - *Visuel* : Le flux de neutrons traverse cette étape avec une légère augmentation de leur nombre.

- **Étape 2 : Facteur anti-fuite rapide (P_AFR)**
  - Avant d'être ralentis, une partie des neutrons rapides s'échappe du cœur du réacteur. Seule une fraction continue son cycle.
  - *Visuel* : Le flux de neutrons subit une première diminution due aux fuites.

- **Étape 3 : Facteur anti-trappe (p)**
  - Pendant que les neutrons ralentissent (sont "modérés"), une partie est capturée sans produire de fission (notamment par les "résonances" de certains noyaux lourds). Seule une fraction "échappe" à cette capture.
  - *Visuel* : Le flux de neutrons subit une diminution notable en traversant cette étape.

- **Étape 4 : Facteur anti-fuite thermique (P_AFT)**
  - Une fois ralentis (devenus thermiques), une autre partie des neutrons s'échappe du cœur avant d'interagir avec la matière.
  - *Visuel* : Le flux de neutrons subit une seconde diminution due aux fuites.

- **Étape 5 : Facteur d'utilisation thermique (f)**
  - Les neutrons thermiques restants peuvent soit être absorbés par le combustible, soit être capturés par d'autres éléments (modérateur, structures, poisons, barres de contrôle). Seule une fraction est "utile".
  - *Visuel* : Le flux de neutrons subit une dernière diminution importante, dont l'ampleur dépend des actions de l'utilisateur.

- **Étape 6 : Facteur de reproduction (η)**
  - Les neutrons thermiques absorbés par le combustible provoquent des fissions, créant une nouvelle population, plus grande, de neutrons rapides pour la génération suivante.
  - *Visuel* : Le flux de neutrons passe cette dernière étape et le nombre de neutrons augmente fortement, bouclant le cycle.

- **Résultat** : La population finale de neutrons **rapides** est comparée à la population de départ pour déterminer l'état du réacteur.

### 3.2. Paramètres Interactifs

L'utilisateur doit disposer de "leviers" (curseurs, boutons, champs de saisie) pour modifier les paramètres physiques du réacteur. Chaque modification doit instantanément mettre à jour la simulation visuelle et les calculs.

- **Position des barres de contrôle** : Le principal levier de pilotage rapide. Leur insertion augmente l'absorption et diminue le facteur `f`.
- **Concentration en bore soluble** : Le principal levier de pilotage lent. Augmenter la concentration augmente l'absorption et diminue le facteur `f`.
- **Température du combustible** : L'augmentation de la température augmente la capture "par résonance", ce qui diminue le facteur `p` (Effet Doppler).
- **Température du modérateur** : L'augmentation de la température du modérateur (l'eau) diminue sa densité, ce qui affecte à la fois son efficacité à ralentir les neutrons et l'efficacité du bore. Cela impacte les facteurs `p` et `f`, ainsi que les probabilités de fuite.
- **Présence de "poisons" (ex: Xénon)** : Simuler la présence de produits de fission qui sont de forts absorbeurs de neutrons. Leur présence diminue le facteur `f`.

### 3.3. Affichages et Données en Temps Réel

Plusieurs indicateurs et panneaux d'information clés doivent être visibles en permanence pour quantifier l'état du réacteur et fournir un contexte riche.

- **Indicateur principal de criticité (k_eff)** : Un indicateur proéminent (type jauge ou cadran) montrant le rapport entre la population de neutrons finale et initiale. Il doit clairement indiquer l'état :
  - **Sous-critique (k < 1)** : La réaction s'éteint.
  - **Critique (k = 1)** : La réaction est stable et auto-entretenue.
  - **Sur-critique (k > 1)** : La réaction diverge, la puissance augmente.

- **Panneau de données de réactivité** :
  - **Réactivité (ρ)** : Affichage de la réactivité (en pcm), qui est une mesure de l'écart à la criticité.
  - **Anti-réactivité par effet** : Affichage détaillé de la contribution (en pcm) de chaque effet à l'anti-réactivité totale (barres, bore, température, poisons).

- **Graphique d'évolution** : Une courbe simple montrant l'évolution de la population neutronique au fil des générations (ou du temps), illustrant visuellement la convergence, la stabilité ou la divergence.

- **Détail des facteurs du cycle** : Les valeurs calculées pour `η`, `ε`, `p`, `f`, `P_AFR` et `P_AFT` doivent être affichées en permanence à côté des étapes correspondantes du cycle visuel.

- **Journal de Simulation** : Un panneau textuel déroulant qui enregistre les actions de l'utilisateur et les changements d'état importants.
  > *Exemple : "10:32:15 - Augmentation de la concentration en bore à 800 ppm. Réactivité passe à -150 pcm."*

### 3.4. Scénarios Prédéfinis (Presets)

Pour faciliter l'apprentissage et garantir l'évolutivité, le logiciel inclura un menu de sélection de scénarios prédéfinis ('presets'). Ces derniers devront être chargés depuis un fichier de configuration externe (ex: format JSON), permettant ainsi d'ajouter ou de modifier facilement des cas d'étude sans recompiler le programme. Le choix d'un preset chargera automatiquement un ensemble de valeurs cohérentes pour tous les paramètres interactifs (concentration en bore, température, présence de poisons, etc.), plaçant l'utilisateur dans une configuration de réacteur réaliste et pertinente.

**Exemples de presets à inclure :**

- **Début de Cycle (Combustible Neuf)** : Forte concentration en bore, pas de poisons Xénon.
- **Fin de Cycle (Combustible Usé)** : Faible concentration en bore, présence de produits de fission.
- **Fonctionnement en Puissance (Xénon à l'équilibre)** : État stable où la production et la disparition du Xénon se compensent.
- **Pic Xénon post-arrêt** : Situation quelques heures après un arrêt du réacteur, montrant l'antiréactivité maximale du Xénon.
- **Divergence à chaud** : Conditions typiques d'un démarrage de réacteur avec le circuit primaire à sa température nominale.

## 4. Fonctionnalité Pédagogique Essentielle : L'Info-Bulle Universelle

C'est une exigence fondamentale du projet. À tout moment, le survol de n'importe quel élément de l'interface avec le pointeur de la souris doit faire apparaître une info-bulle. Cette dernière doit fournir une explication simple, concise et pédagogique de l'élément survolé.

**Exemples :**

> **Survol du curseur "Position des barres"** : "Les barres de contrôle contiennent un matériau qui absorbe les neutrons. Les insérer dans le cœur réduit le nombre de neutrons disponibles pour la fission, ce qui diminue la réactivité."

> **Survol de l'indicateur "k_eff"** : "Le facteur de multiplication k_eff est le rapport entre le nombre de neutrons d'une génération et celui de la génération précédente. Si k_eff = 1, la population est stable : le réacteur est critique."

> **Survol de l'étape "Facteur anti-trappe (p)"** : "Pendant leur ralentissement, les neutrons traversent des 'pièges' d'énergie où ils risquent d'être capturés. 'p' représente la probabilité pour un neutron d'échapper à ces captures."

Un simple appui sur la touche "i" du clavier permet d'ouvrir une fenêtre affichant d'avantage d'informations sur ce que survol le pointeur. Apuyer une nouvelle fois sur "i" ou "space" ou "escape" permet de fermer la fenêtre.

## 5. Spécifications Techniques et Recommandations

- **Langage principal** : Le cœur du programme et sa logique physique devront être développés en **Python**, pour sa simplicité et sa robustesse.
- **Interface utilisateur (UI)** : Pour garantir la rapidité, la compatibilité cross-platform (Windows, macOS, Linux) et un déploiement facile, l'utilisation d'un framework comme **PyQt6** ou **Kivy** est recommandée.
- **Performance** : Les calculs requis sont des opérations arithmétiques simples et ne demandent pas une grande puissance de calcul. L'application doit être très réactive et fluide.
- **Déploiement** : Le projet final devra être packagé en un exécutable unique et autonome (ne nécessitant pas l'installation de Python ou de librairies par l'utilisateur final). Des outils comme **PyInstaller** ou **cx_Freeze** devront être utilisés.
- **Scalabilité et Documentation** : Le code devra être structuré de manière modulaire (séparation claire entre le modèle physique et l'interface graphique) et abondamment commenté. Cela est crucial pour permettre des évolutions futures (ajout de nouvelles fonctionnalités, scénarios, etc.) et pour faciliter le transfert du projet.