This note provides a detailed, quantitative analysis of Xenon and Iodine evolution in a Pressurized Water Reactor (PWR), based on the provided training and guidance documents.

## Fundamental Dynamics of Iodine and Xenon

Iodine-135 (I-135) and Xenon-135 (Xe-135) are fission products that significantly impact reactor control due to Xenon's extremely high neutron absorption capacity. Understanding their temporal dynamics is crucial for reactor piloting.

### Production and Disappearance Chains

**Iodine-135:**
* **Production:** I-135 is produced almost exclusively as a direct product of fission . It accounts for about **6% to 6.4%** of fission products .
* **Disappearance:** It disappears through radioactive decay, transforming into Xe-135 with a half-life of approximately **6.5 to 6.7 hours** .

**Xenon-135:**
Xe-135 is the most significant neutron poison in a reactor . Its concentration is governed by two production and two disappearance mechanisms:
* **Production:**
    1.  **Indirect:** The vast majority of Xe-135 comes from the radioactive decay of I-135 . This delayed production is the primary driver of xenon's complex behavior.
    2.  **Direct:** A very small fraction, **0.1% to 0.3%**, of fissions directly produce Xe-135 .
* **Disappearance:**
    1.  **Radioactive Decay:** Xe-135 is unstable and decays into Cesium-135 with a half-life of approximately **9.2 hours** .
    2.  **Neutron Capture (Burn-out):** As a powerful neutron absorber, Xe-135 can capture a neutron, transforming into the stable and neutronically insignificant Xe-136 . This process is directly proportional to the neutron flux (i.e., reactor power).

At a constant power level, these production and disappearance rates eventually balance, leading to a stable **equilibrium concentration** of Xenon . At 100% nominal power (Pn), the equilibrium Xenon creates a negative reactivity of approximately **-2700 to -2800 pcm** .

---
## Xenon and Iodine Behavior in Reactor Transients

Any change in reactor power disrupts the equilibrium, leading to significant transient changes in Xenon concentration.

### Reactor Shutdown (AAR): The Xenon Peak

When a reactor is shut down from a high power level, the neutron flux drops to nearly zero.
1.  **Immediate Effect:** Fission stops, halting the direct production of both I-135 and Xe-135. Crucially, the disappearance of Xe-135 by neutron capture also stops .
2.  **Build-up:** The large stockpile of I-135 accumulated at high power continues to decay into Xe-135 . Since the primary removal mechanism (burn-out) is gone, the Xe-135 concentration rises significantly .
3.  **Peak Xenon:** The concentration reaches a maximum, known as the **"pic Xénon,"** approximately **6 to 8 hours** after the shutdown . This peak can induce a massive negative reactivity, reaching up to **-4300 pcm** following a shutdown from 100% Pn .
4.  **Decay:** After the peak, as the I-135 stockpile is depleted, the Xe-135 concentration begins to decrease solely through its own radioactive decay . The Xenon concentration returns to its pre-shutdown level after approximately **18 hours** for PMOX fuel and **22 hours** for GARANCE fuel . The concentration becomes negligible after 48 to 72 hours .

### Power Increase: The Xenon Trough

When increasing power, the neutron flux rises.
1.  **Immediate Effect:** The rate of Xe-135 removal by neutron capture increases instantly and significantly. Simultaneously, the production rate of I-135 increases .
2.  **Trough Formation:** Because the production of new Xenon from the freshly created Iodine is delayed (by Iodine's ~6.7-hour half-life), the immediate effect is a net *decrease* in Xenon concentration . This causes a temporary increase in core reactivity.
3.  **Xenon Trough:** The concentration reaches a minimum, the **"creux Xénon,"** about **4 to 5 hours** after the power increase .
4.  **Recovery to Equilibrium:** After the trough, the large amount of new Iodine begins to decay, increasing the Xe-135 production rate. The Xenon concentration rises again, eventually stabilizing at a new, higher equilibrium level corresponding to the higher power level after **48 to 72 hours** .

### Power Decrease

A planned power decrease is a less extreme version of a reactor shutdown. The reduction in neutron flux lessens the Xe-135 burn-out rate. The existing I-135 continues to decay, causing a temporary rise in Xe-135 concentration and introducing negative reactivity that must be managed by the operators .

---
## Spatial Effects: Xenon Oscillations

Xenon dynamics also have a spatial component, leading to axial power oscillations. A disturbance, like inserting control rods, can push the neutron flux towards the bottom of the core, creating an imbalance .

1.  **Initiation:** The flux moves to the bottom half. More I-135 is now produced in the bottom, while in the low-flux top half, the existing I-135 decays, increasing the Xe-135 concentration there.
2.  **Oscillation:** This high concentration of Xenon in the top half further suppresses the flux there, pushing it even more towards the bottom. However, the new Iodine produced in the bottom starts decaying to Xenon, while the Xenon in the top decays away. This increase of Xenon in the bottom then pushes the flux back towards the top.
3.  **Period:** This creates a slow oscillation of power between the top and bottom halves of the core, with the flux and Xenon distributions being generally out of phase . The typical period of this oscillation is about **30 hours** . These oscillations must be actively managed ("damped") by the operators to prevent localized power peaks.