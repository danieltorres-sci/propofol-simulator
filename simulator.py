import numpy as np
import matplotlib.pyplot as plt

def simulate_patient(age, weight, height, sex, dose_mg):
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
    t_end = 60
    time = np.arange(0, t_end, dt)

    c1 = np.zeros(len(time))
    c2 = np.zeros(len(time))
    c3 = np.zeros(len(time))
    ce = np.zeros(len(time))
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

    return time, c1, ce

# ── Run both patients ────────────────────────────────────────
time, p1_plasma, p1_brain = simulate_patient(35, 70, 170, 'male', 120)
time, p2_plasma, p2_brain = simulate_patient(75, 65, 165, 'male', 120)

# ── Plot ─────────────────────────────────────────────────────
plt.figure(figsize=(11, 6))

plt.plot(time, p1_plasma, color='steelblue', linewidth=2, label='Plasma — 35yr')
plt.plot(time, p1_brain,  color='steelblue', linewidth=2, linestyle='--', label='Brain — 35yr')

plt.plot(time, p2_plasma, color='tomato', linewidth=2, label='Plasma — 75yr')
plt.plot(time, p2_brain,  color='tomato', linewidth=2, linestyle='--', label='Brain — 75yr')

plt.axhline(y=3.0, color='gray', linestyle=':', linewidth=1.5, label='Awareness threshold')

plt.xlabel('Time (minutes)')
plt.ylabel('Concentration (mcg/mL)')
plt.title('Propofol PK/PD — 35yr vs 75yr Male | Same 120mg Dose')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('comparison_35yr_vs_75yr.png', dpi=150)
plt.show()
print("Done! Saved as comparison_35yr_vs_75yr.png")