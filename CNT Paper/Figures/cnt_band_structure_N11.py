import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Parameters
N = 11
kxa = np.linspace(-np.pi, np.pi, 1000)
m = np.arange(N)  # Sub-band index array [0, 1, ..., N-1]

# Reshape arrays for 2D broadcasting
kxa_grid = kxa[:, np.newaxis]
m_grid = m[np.newaxis, :]

# Calculate dispersion relation E(k_x * a, m)
E = np.sqrt(
    1
    + 4 * np.cos(kxa_grid) * np.cos(np.pi * m_grid / N)
    + 4 * (np.cos(m_grid * np.pi / N)) ** 2
)

# Plotting setup
plt.figure(figsize=(9, 6))

# Generate a colormap with N distinct colors
colors = plt.cm.turbo(np.linspace(0.05, 0.95, N))

# Scaled x-axis data: (3 * k_x * a) / (2 * pi)
x_scaled = 1.5 * kxa / np.pi

for i in range(N):
    color = colors[i]

    # Plot positive (conduction) and negative (valence) bands
    plt.plot(x_scaled, E[:, i], color=color, linewidth=1.5)
    plt.plot(x_scaled, -E[:, i], color=color, linewidth=1.5)

    # Annotate index m at the right edge
    y_top = E[-1, i]
    y_bottom = -E[-1, i]

    plt.text(1.53, y_top, f'$m={i}$', color=color, fontsize=8, va='center', fontweight='bold')
    plt.text(1.53, y_bottom, f'$m={i}$', color=color, fontsize=8, va='center', fontweight='bold')

plt.title(f'CNT Electronic Band Structure ($N = {N}$)', fontsize=14)
plt.xlabel(r'$3 k_x a / 2 \pi$', fontsize=12)
plt.ylabel(r'Energy $E / t$', fontsize=12)

# Adjust x-limits to account for the scaled range [-1.5, 1.5] plus margin for labels
plt.xlim(-1.5, 1.7)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig(
    "/Users/shlok/Documents/Repos/Panjwa/CNT Paper/Figures/cnt_band_structure_N11.png",
    dpi=200, bbox_inches="tight",
)
print("saved Figures/cnt_band_structure_N11.png")
