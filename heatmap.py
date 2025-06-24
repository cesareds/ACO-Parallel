import matplotlib.pyplot as plt
import numpy as np
import os

# Parâmetros
ALPHAS = [1.0, 1.5, 2.0]
BETAS = [2.0, 3.5, 5.0]
EVAPOS = [0.10, 0.35, 0.60]
EVAPO_FILENAMES = ["01", "035", "06"]

directory = "runs2"

costs = np.zeros((len(ALPHAS), len(BETAS), len(EVAPOS)))

# Leitura dos custos médios
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

# Geração de heatmaps separados
for k, e in enumerate(EVAPOS):
    data = costs[:, :, k].T  # Transpõe para alpha em X e beta em Y
    fig, ax = plt.subplots(figsize=(6, 5))

    im = ax.imshow(data, cmap="viridis", origin="lower", vmin=np.nanmin(costs), vmax=np.nanmax(costs))
    ax.set_title(f"Evaporação = {e:.2f}", fontsize=14)
    ax.set_xticks(range(len(ALPHAS)))
    ax.set_yticks(range(len(BETAS)))
    ax.set_xticklabels(ALPHAS)
    ax.set_yticklabels(BETAS)
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Beta")

    # Adiciona texto com valores
    for i in range(len(BETAS)):
        for j in range(len(ALPHAS)):
            val = data[i, j]
            text = f"{val:.1f}" if not np.isnan(val) else "NaN"
            ax.text(j, i, text, ha="center", va="center", color="w")

    # Barra de cor individual
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, label="Custo médio")

    # Salva com nome específico
    fname = f"heatmap{EVAPO_FILENAMES[k]}.jpg"
    plt.tight_layout()
    plt.savefig(fname, dpi=300)
    plt.close()
