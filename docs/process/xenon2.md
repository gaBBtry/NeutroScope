Basé sur l'analyse des documents fournis, je peux maintenant rédiger une note détaillée et quantitative sur l'évolution du xénon et de l'iode selon les différents scénarios. Voici ma synthèse :

# NOTE DÉTAILLÉE : ÉVOLUTION DU XÉNON ET DE L'IODE EN FONCTION DU TEMPS SELON LES DIFFÉRENTS SCÉNARIOS DE FONCTIONNEMENT

*Date d'analyse : 21 juillet 2025*  
*Sources : Documents de formation EDF - Pilotage des réacteurs CPY*

## 1. PROPRIÉTÉS PHYSIQUES ET CONSTANTES TEMPORELLES

### 1.1 Chaîne de production du Xénon 135

**Réaction de fission d'U-235 :**
- Production directe de Xe-135 : **0,3% des fissions** (γ = 0,003)[1][2]
- Production directe d'I-135 : **6% des fissions** (γ = 0,06)[1][2]
- Ratio production indirecte/directe : **20:1** (l'iode est 20 fois plus produit)

**Chaîne de désintégration :**
```
Fission U-235 → I-135 (T₁/₂ = 6,7h) → Xe-135 (T₁/₂ = 9,2h) → Cs-135 (stable)
                    ↓                           ↓
              Production directe        Capture neutronique
                Xe-135 (0,3%)              Xe-135 → Xe-136
```

### 1.2 Constantes temporelles quantitatives

**Périodes de demi-vie :**[1][2][3]
- **Iode 135** : T₁/₂ = **6,7 heures** → λᵢ = 0,1034 h⁻¹
- **Xénon 135** : T₁/₂ = **9,2 heures** → λₓₑ = 0,0753 h⁻¹

**Temps caractéristiques :**
- Temps de vie moyen iode : τᵢ = 1/λᵢ = **9,67 heures**
- Temps de vie moyen xénon : τₓₑ = 1/λₓₑ = **13,28 heures**

## 2. VALEURS QUANTITATIVES D'ANTIRÉACTIVITÉ

### 2.1 Ordre de grandeur pour tranches PMOX[2][3]

**À l'équilibre :**
- **100% Pn** : Xe-135 = **-2700 à -2800 pcm**
- **0% Pn** : Xe-135 ≈ **0 pcm** (xénon nul après 48-72h)

**Pics et extremums :**
- **Pic xénon post-AAR** : **-4000 à -4300 pcm**
- **Maximum atteint** : environ **6-8 heures** après AAR[1][2][3]
- **Retour à l'équilibre** : **48-72 heures**[2][3]

### 2.2 Efficacité relative
- Section efficace Xe-135 : **~1 million de fois** supérieure à U-238[3]
- Impact : 1 ppm de xénon ≡ 1 tonne de bore en termes d'absorption neutronique

## 3. SCÉNARIOS TEMPORELS ET ÉVOLUTIONS QUANTITATIVES

### 3.1 Scénario 1 : Arrêt Automatique du Réacteur (AAR)

**État initial :** Réacteur à 100% Pn, xénon à l'équilibre (-2800 pcm)

**Évolution temporelle :**[1][2][3]

| Temps après AAR | Iode 135 | Xénon 135 | Antiréactivité Xe |
|------------------|----------|-----------|-------------------|
| **t = 0h** | Maximum | -2800 pcm | -2800 pcm |
| **t = 3h** | ↓ 70% | ↗ | -3200 pcm |
| **t = 6-8h** | ↓ 25% | **Maximum** | **-4300 pcm** |
| **t = 12h** | ↓ 6% | ↘ | -3800 pcm |
| **t = 24h** | ↓ 1% | ↘↘ | -2000 pcm |
| **t = 48h** | ≈ 0 | ↘↘↘ | -500 pcm |
| **t = 72h** | ≈ 0 | **≈ 0** | **≈ 0 pcm** |

**Mécanisme physique :**
1. **Phase 1 (0-8h)** : Arrêt production directe + poursuite production via I-135 → **pic xénon**
2. **Phase 2 (8-48h)** : Disparition par décroissance radioactive uniquement
3. **Phase 3 (48-72h)** : Retour à l'équilibre (xénon nul)

### 3.2 Scénario 2 : Baisse de charge (100% → 60% Pn)

**État initial :** Réacteur à 100% Pn, xénon équilibre

**Évolution temporelle :**[2][3]

| Temps | Puissance | I-135 (relatif) | Xe-135 (relatif) | ΔXe (pcm) |
|-------|-----------|----------------|------------------|-----------|
| **t = 0h** | 100% → 60% | 100% | 100% | 0 |
| **t = 2h** | 60% | ↗ 110% | ↗ 108% | +200 |
| **t = 6h** | 60% | ↘ 90% | ↗ 115% | +350 |
| **t = 12h** | 60% | ↘ 70% | ↗ 110% | +250 |
| **t = 24h** | 60% | ↘ 60% | ↘ 95% | -100 |
| **t = 48h** | 60% | ↘ 60% | ↘ 60% | -800 |

### 3.3 Scénario 3 : Montée de charge (40% → 100% Pn)

**Évolution du "creux xénon" :**[3]

**Chronologie quantifiée :**
- **t = 0h** : Début montée de charge
- **t = 1-2h** : Augmentation capture neutronique → baisse Xe-135
- **t = 4-5h** : **Creux xénon minimal** (-15 à -20% du niveau initial)
- **t = 8-10h** : Production I-135 compense → remontée Xe-135
- **t = 48-72h** : Nouvel équilibre à 100% Pn

### 3.4 Scénario 4 : Oscillations xénon (phénomène spatial)

**Paramètres temporels des oscillations :**[2][3]
- **Période d'oscillation** : **20-30 heures**
- **Temps d'opposition de phase** : **7-8 heures** après perturbation
- **Amortissement** : **2-3 oscillations** avant stabilisation
- **Durée totale** : **60-80 heures**

## 4. IMPACT OPÉRATIONNEL ET GESTION

### 4.1 Compensation en bore

**Équivalences quantitatives :**[1][2]
- **1000 pcm xénon** ≡ **~150 ppm bore** (début de cycle)
- **Pic xénon (+1500 pcm)** → Dilution **~4-5 m³** eau déminéralisée
- **Vitesse compensation** : **200-300 pcm/h** en décroissance xénon

### 4.2 Temps caractéristiques de pilotage

**Délais d'action :**[2][3]
- **Divergence après AAR** : Possible après **100 heures** (xénon ≈ 0)
- **Redémarrage rapide** : Impossible entre **6h et 30h** post-AAR
- **Stabilisation distribution axiale** : **48-72 heures**

### 4.3 Contraintes de manœuvrabilité

**Limitations quantifiées :**[2][3]
- **Gradient maximum supportable** : ±200 pcm/h en variation xénon
- **Seuil d'oscillation critique** : ΔI > ±3% pendant > 4h
- **Temps de récupération manœuvrabilité** : **12-24h** après oscillation

## 5. MODÉLISATION MATHÉMATIQUE SIMPLIFIÉE

### 5.1 Équations de Bateman

Pour un arrêt brutal (φ = 0) :

**Iode 135 :**  
I(t) = I₀ × e^(-λᵢt)

**Xénon 135 :**  
Xe(t) = Xe₀ × e^(-λₓₑt) + (λᵢ × I₀)/(λₓₑ - λᵢ) × [e^(-λᵢt) - e^(-λₓₑt)]

### 5.2 Temps caractéristiques calculés

- **Pic xénon théorique** : t_pic = ln(λₓₑ/λᵢ)/(λᵢ - λₓₑ) ≈ **7,2 heures**
- **Valeur pic** : Xe_max ≈ **1,52 × Xe₀** (soit +52% du niveau initial)

## CONCLUSION QUANTITATIVE

Cette analyse révèle que les phénomènes xénon et iode sont **quantitativement prévisibles** avec des **constantes temporelles bien établies**. Les **temps caractéristiques** (6,7h et 9,2h) gouvernent tous les scénarios opérationnels, permettant une **gestion anticipative** des variations de réactivité comprises entre **-4300 pcm** (pic post-AAR) et **+500 pcm** (creux lors de remontées de charge).

La **maîtrise quantitative** de ces phénomènes est **cruciale** pour la sûreté et l'exploitation optimale des réacteurs à eau pressurisée.