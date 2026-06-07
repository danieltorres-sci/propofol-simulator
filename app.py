import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="Propofol PK/PD Simulator", layout="centered")

st.title("Propofol PK/PD Simulator")
st.markdown("""
**Based on Schnider et al. (1999)** — the same mathematical model used in Target Controlled Infusion (TCI) pumps in operating rooms worldwide.

Built by **Daniel Torres**, Anesthesia Technician at Stanford Medicine | Biophysiology student at SFSU | Pre-med
""")

# ── Sidebar Inputs ───────────────────────────────────────────
st.sidebar.header("Patient Parameters")
age     = st.sidebar.slider("Age (years)", 18, 90, 35)
weight  = st.sidebar.slider("Weight (kg)", 40, 150, 70)
height  = st.sidebar.slider("Height (cm)", 140, 210, 170)
sex     = st.sidebar.radio("Sex", ["male", "female"])
dose_mg = st.sidebar.slider("Propofol Dose (mg)", 50, 300, 120)

# ── Science Explainer ────────────────────────────────────────
st.markdown("---")
st.subheader("What is this showing?")
st.markdown("""
Propofol distributes across **three body compartments** after an IV bolus:

- **Plasma (blue)** — Drug enters here first. Spikes instantly then drops fast as it redistributes.
- **Muscle (red)** — Absorbs drug quickly down a concentration gradient. Returns it to plasma slowly.
- **Fat (green)** — Absorbs drug slowly but holds it for a long time. Explains slow wake-up after long surgeries.
- **Brain/Effect-Site (purple)** — Estimated brain concentration using ke0. Lags behind plasma by 2-3 minutes — this is why we wait after injecting before intubating.
- **Awareness threshold (dotted)** — Below 3 mcg/mL the patient may start regaining consciousness.
""")

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