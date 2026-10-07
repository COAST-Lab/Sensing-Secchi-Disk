# Measured vs estimated chl-a from an 8-band raw-Kd multiple linear regression
# Chl_est = b0 + b1*Kd415 + b2*Kd445 + b3*Kd480 + b4*Kd515 + b5*Kd555 + b6*Kd590 + b7*Kd630 + b8*Kd680

# Programs and functions
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from pathlib import Path

kd_path = Path.cwd() / "src" / "KD-Conversion.xlsx"

# Wavelengths (nm) and column holding the directly measured chl-a
wavelengths = [415, 445, 480, 515, 555, 590, 630, 680]
chl_col = "µg Chl a/L, direct"

# Read Kd workbook and keep only casts that have a "discrete" chl-a and all 8 Kd values
try:
    kd_df = pd.read_excel(kd_path, sheet_name="Kd")
except Exception as e:
    print(f"Error reading KD-Conversion.xlsx: {e}")
    raise
kd_cols = [f"{w}nm" for w in wavelengths]
kd_df = kd_df.dropna(subset=[chl_col] + kd_cols).reset_index(drop=True)

# The magic begins here, first build regression inputs, then the design matrix, then perform MLR
chl_measured = kd_df[chl_col].to_numpy(float)
X = np.column_stack([np.ones(len(chl_measured)), kd_df[kd_cols].to_numpy(float)])

# Least-squares fit and estimated chl-a
coeffs = np.linalg.lstsq(X, chl_measured, rcond=None)[0]
chl_est = X @ coeffs

# R2, adjusted R2 and RMSE
n, p = X.shape
sse = np.sum((chl_measured - chl_est) ** 2)
sst = np.sum((chl_measured - chl_measured.mean()) ** 2)
r2 = 1 - sse / sst
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p)
rmse = np.sqrt(sse / n)
print('n = ', n)
print('R2 = ', round(r2, 3))
print('Adjusted R2 = ', round(adj_r2, 3))
print('RMSE (ug/L) = ', round(rmse, 2))

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.linewidth": 0.8, "mathtext.fontset": "stix",
})

# Plot measured vs estimated chl-a with 1:1 line (unlabeled for now)
fig, ax = plt.subplots(figsize=(3.6, 3.6))
lim = max(chl_measured.max(), chl_est.max()) * 1.05
ax.plot([0, lim], [0, lim], "k--", lw=0.8, label=None)
ax.scatter(chl_measured, chl_est, s=18, color="#1f4e9c", edgecolor="k", lw=0.3, zorder=3)
ax.set_xlim(-1, lim)
ax.set_ylim(-1, lim)
ax.set_aspect("equal")
ax.set_xlabel(r"Measured Chl-$a$ (µg L$^{-1}$)")
ax.set_ylabel(r"Estimated Chl-$a$ (µg L$^{-1}$)")
ax.text(0.04, 0.96, f"$R^2$ = {r2:.2f}, adj. $R^2$ = {adj_r2:.2f}\nRMSE = {rmse:.1f} µg L$^{{-1}}$\n$n$ = {n}",
        transform=ax.transAxes, va="top", fontsize=7.5, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
ax.grid(alpha=0.25, lw=0.4)

fig_folder = Path.cwd() / "Sensing-Secchi-Disk-COAST" / "Thesis figures"
fig_folder.mkdir(exist_ok=True)
fig_path = fig_folder / "Chl_a_measured_vs_estimated.png"
try:
    fig.savefig(fig_path, dpi=300, bbox_inches='tight', pad_inches=0.15)
    print("File saved successfully.")
except Exception as e:
    print(f"Error saving file: {e}")
