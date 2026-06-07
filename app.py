import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Propofol PK/PD Simulator", layout="centered")

st.title("Propofol PK/PD Simulator")
st.markdown("""
**Based on Schnider et al. (1999)** — the same mathematical model used in Target Controlled Infusion (TCI) pumps in operating rooms worldwide.

Built by **Daniel Torres**, Anesthesia Technician at Stanford Medicine | Biophysiology student at SFSU | Pre-med
""")

# ── Section 1 — What is Propofol ─────────────────────────────
with st.expander("What is Propofol?"):
    st.markdown("""
Propofol (2,6-diisopropylphenol) is an intravenous anesthetic agent used for induction and maintenance of general anesthesia and procedural sedation.

**Mechanism of Action**
Propofol enhances the activity of **GABA-A receptors** — the brain's primary inhibitory receptors. GABA (gamma-aminobutyric acid) is a neurotransmitter that suppresses neural activity. Propofol supercharges this effect, causing widespread suppression of brain activity that results in unconsciousness.

**Why is it preferred?**
- Rapid onset (30-60 seconds)
- Short duration of action
- Clean, clear-headed emergence — patients wake up quickly without prolonged grogginess
- Antiemetic properties — reduces post-operative nausea

**Why is it lipophilic?**
Propofol is highly fat-soluble, which is why it crosses the blood-brain barrier so quickly. This same property also explains why it distributes so readily into muscle and fat tissue.
    """)

# ── Section 2 — What is a PK Model ──────────────────────────
with st.expander("What is Pharmacokinetics (PK)?"):
    st.markdown("""
**Pharmacokinetics describes what the body does to the drug.**

The three-compartment model divides the body into three interconnected spaces:

**Central Compartment (Plasma)**
Where the drug enters first via IV injection. Highly perfused — drug distributes rapidly out of here into other tissues. This is what the blue line shows.

**Fast Peripheral Compartment (Muscle)**
Muscle tissue absorbs propofol quickly down a concentration gradient. When plasma levels drop, muscle releases drug back. This is the red line.

**Slow Peripheral Compartment (Fat)**
Adipose tissue absorbs propofol slowly but holds it for a long time due to propofol's high lipid solubility. Fat keeps releasing drug back into plasma long after the initial bolus — this is why patients who've been on a propofol infusion for hours are slow to wake up. This is the green line.

**Rate Constants (k values)**
The speed at which drug moves between compartments is governed by rate constants — the k values in the Schnider equations. These were determined experimentally by giving real patients propofol, drawing blood samples repeatedly, and working backwards mathematically.

**Patient-Specific Parameters**
The Schnider model adjusts for age, weight, height, and lean body mass — because these factors directly affect how much volume drug distributes into and how fast the liver clears it.
    """)

# ── Section 3 — What is PD ───────────────────────────────────
with st.expander("What is Pharmacodynamics (PD)?"):
    st.markdown("""
**Pharmacodynamics describes what the drug does to the body.**

While PK tells us where the drug goes, PD tells us what happens when it gets to its target — the brain.

**The GABA-A Receptor**
Propofol binds to GABA-A receptors in the cerebral cortex and other brain regions. This enhances chloride ion influx into neurons, hyperpolarizing them and making them less likely to fire. The result is dose-dependent sedation and unconsciousness.

**The Awareness Threshold**
At approximately **3 mcg/mL** effect-site concentration, patients begin to regain consciousness. Above this threshold the brain has enough propofol to maintain unconsciousness. Below it, awareness can return.

**Why plasma concentration alone isn't enough**
The brain isn't directly sampled in clinical practice. Plasma concentration is used as a proxy — but there's a lag between what's in the blood and what's actually at the receptor level in the brain. This is where ke0 comes in.
    """)

# ── Section 4 — What is ke0 ──────────────────────────────────
with st.expander("What is ke0? (The Brain Lag)"):
    st.markdown("""
**ke0 is the rate constant that describes how fast propofol equilibrates between plasma and the brain.**

When propofol is injected, plasma concentration spikes instantly. But the brain concentration starts at zero and climbs gradually as drug crosses the blood-brain barrier. ke0 quantifies that lag.

**Value used:** ke0 = 0.456 per minute (from Schnider et al. 1999)

This produces the roughly **2-3 minute lag** you see on the graph between the plasma peak and the brain peak.

**Clinical implication**
This is why anesthesiologists wait after injecting propofol before intubating. The plasma may have already peaked and started dropping — but the brain concentration is still climbing. Rushing to intubate before the brain has equilibrated risks inadequate depth of anesthesia.

**How ke0 was determined**
Schnider's team correlated plasma propofol concentrations with EEG changes in real patients. The point of maximum brain effect relative to peak plasma concentration allowed them to calculate the ke0 value that produced that timing.
    """)

# ── Section 5 — Why Age Matters ──────────────────────────────
with st.expander("Why Does Patient Age Matter?"):
    st.markdown("""
The Schnider model adjusts several parameters based on age:

- **V2 (muscle compartment volume)** decreases with age — less muscle mass means less distribution capacity
- **CL2 (intercompartmental clearance)** decreases with age — slower redistribution
- **CL1 (plasma clearance)** adjusts for lean body mass and weight — elderly patients often have reduced hepatic clearance

**The clinical result:**
The same 120mg dose produces a **higher and longer brain concentration** in a 75-year-old compared to a 35-year-old. The drug hits harder and lasts longer.

This is why anesthesiologists and CRNAs routinely reduce induction doses in elderly patients — typically by 30-50%. The simulation above demonstrates this quantitatively.
    """)

# ── Section 6 — TCI Pumps ────────────────────────────────────
with st.expander("How Does This Relate to TCI Pumps in the OR?"):
    st.markdown("""
**Target Controlled Infusion (TCI) pumps** use this exact Schnider model in real operating rooms worldwide.

The clinician enters a target plasma or effect-site concentration. The pump then:
1. Calculates the patient's compartment volumes and rate constants using their demographics
2. Determines what infusion rate is needed to achieve and maintain the target concentration
3. Continuously adjusts the infusion rate as the drug redistributes

This is pharmacokinetic modeling running in real time, built into a device the size of a laptop.

**The Diprifusor** was one of the first commercial TCI systems and used a precursor to the Schnider model. Modern systems like the Alaris and B. Braun use the Schnider model directly.

The simulation on this page is essentially a simplified version of what those pumps compute — the difference being that TCI pumps solve for the infusion rate needed to hit a target, while this simulator shows what happens after a single bolus.
    """)

# ── Sidebar Inputs ───────────────────────────────────────────
st.markdown("---")
st.subheader("Run the Simulation")
st.markdown("Adjust the patient parameters on the left and watch how the drug distribution changes.")

st.sidebar.header("Patient Parameters")
age     = st.sidebar.slider("Age (years)", 18, 90, 35)
weight  = st.sidebar.slider("Weight (kg)", 40, 150, 70)
height  = st.sidebar.slider("Height (cm)", 140, 210, 170)
sex     = st.sidebar.radio("Sex", ["male", "female"])
dose_mg = st.sidebar.slider("Propofol Dose (mg)", 50, 300, 120)

# ── Simulation ───────────────────────────────────────────────
if sex == 'male':
    lbm = 1.1 * weight - 128 * (weight / height) ** 2
else:
    lbm = 1.07 * weight - 148 * (weight / height) ** 2

v1  = 4.27
v2  = 18.9 - 0.391 * (age - 53)
v3  = 238
cl1 = 1.89 + 0.0456 * (weight - 77) - 0.0681 * (lbm - 59) + 0.0264 * (height - 177)
cl2 = 1.29 - 0.024 * (age - 53)
cl3 = 0.836

k10 = cl1 / v1
k12 = cl2 / v1
k13 = cl3 / v1
k21 = cl2 / v2
k31 = cl3 / v3
ke0 = 0.456

dt   = 0.01
time = np.arange(0, 60, dt)
c1   = np.zeros(len(time))
c2   = np.zeros(len(time))
c3   = np.zeros(len(time))
ce   = np.zeros(len(time))
c1[0] = dose_mg / v1

for i in range(1, len(time)):
    dc1 = (-k10 - k12 - k13) * c1[i-1] + k21 * c2[i-1] + k31 * c3[i-1]
    dc2 = k12 * c1[i-1] - k21 * c2[i-1]
    dc3 = k13 * c1[i-1] - k31 * c3[i-1]
    dce = ke0 * (c1[i-1] - ce[i-1])
    c1[i] = c1[i-1] + dc1 * dt
    c2[i] = c2[i-1] + dc2 * dt
    c3[i] = c3[i-1] + dc3 * dt
    ce[i] = ce[i-1] + dce * dt

# ── Plot ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(time, c1, label='Plasma', color='steelblue', linewidth=2)
ax.plot(time, c2, label='Muscle', color='tomato', linewidth=2)
ax.plot(time, c3, label='Fat', color='seagreen', linewidth=2)
ax.plot(time, ce, label='Brain (Effect-Site)', color='mediumpurple', linewidth=2, linestyle='--')
ax.axhline(y=3.0, color='gray', linestyle=':', linewidth=1.5, label='Awareness threshold')
ax.set_xlabel('Time (minutes)')
ax.set_ylabel('Concentration (mcg/mL)')
ax.set_title(f'Propofol PK/PD — {age}yr {sex}, {weight}kg | Dose: {dose_mg}mg')
ax.legend()
ax.grid(True)
plt.tight_layout()
st.pyplot(fig)

# ── Patient Stats ─────────────────────────────────────────────
st.markdown("---")
st.subheader("Calculated Patient Parameters")
col1, col2, col3 = st.columns(3)
col1.metric("Lean Body Mass", f"{lbm:.1f} kg")
col2.metric("Muscle Compartment V2", f"{v2:.1f} L")
col3.metric("Plasma Clearance CL1", f"{cl1:.2f} L/min")

st.markdown("---")
st.caption("Reference: Schnider TW et al. The influence of age on propofol pharmacodynamics. Anesthesiology. 1999;90(6):1502-1516.")