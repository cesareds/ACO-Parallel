import matplotlib.pyplot as plt
import numpy as np
import os

# Parâmetros
ALPHAS = [1.0, 1.5, 2.0]
BETAS = [2.0, 3.5, 5.0]
EVAPOS = [0.10, 0.35, 0.60]

directory = "runs"

# Inicializa matriz 3D de custos
costs = np.zeros((len(ALPHAS), len(BETAS), len(EVAPOS)))

# Lê os arquivos e armazena a média dos custos
for i, a in enumerate(ALPHAS):
    for j, b in enumerate(BETAS):
        for k, e in enumerate(EVAPOS):
            filepath = f"{directory}/tempos_{a}_{b}_{e:.2f}.txt"
            try:
                with open(filepath, "r") as f:
                    lines = f.readlines()
                    run_costs = [int(line.split()[-1]) for line in lines if line.startswith("Cost")]
                    costs[i, j, k] = np.mean(run_costs) if run_costs else np.nan
            except FileNotFoundError:
                costs[i, j, k] = np.nan

# Gera a figura com 3 heatmaps
fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)

# Criação do heatmap para cada evaporação
heatmaps = []
for k, e in enumerate(EVAPOS):
    data = costs[:, :, k].T  # Transpor: X=alpha, Y=beta
    ax = axes[k]
    im = ax.imshow(data, cmap="viridis", origin="lower", vmin=np.nanmin(costs), vmax=np.nanmax(costs))
    heatmaps.append(im)

    ax.set_title(f"Evaporação = {e:.2f}")
    ax.set_xticks(range(len(ALPHAS)))
    ax.set_yticks(range(len(BETAS)))
    ax.set_xticklabels(ALPHAS)
    ax.set_yticklabels(BETAS)
    ax.set_xlabel("Alpha")
    if k == 0:
        ax.set_ylabel("Beta")

    # Anota os valores nas células
    for i in range(len(BETAS)):
        for j in range(len(ALPHAS)):
            val = data[i, j]
            text = f"{val:.1f}" if not np.isnan(val) else "NaN"
            ax.text(j, i, text, ha="center", va="center", color="w")

# Adiciona colorbar fora dos subplots
cbar = fig.colorbar(heatmaps[0], ax=axes, location='right', shrink=0.8, label="Custo médio")

plt.suptitle("Custo médio por Alpha e Beta para diferentes taxas de evaporação", fontsize=16)
plt.savefig('heatmap.jpg')
plt.show()
