import matplotlib.pyplot as plt
import numpy as np

# Valores de parâmetros
alphas = [0.1, 0.5, 0.9]
betas = [1, 2, 3]
evaps = [0.01, 0.05, 0.1]

# Simular 27 valores de custo (ordem: alpha, beta, evap)
np.random.seed(0)
costs = np.random.rand(27) * 100

# Preparar estrutura
labels = []
data_by_evap = {e: [] for e in evaps}

index = 0
for a in alphas:
    for b in betas:
        labels.append(f"A{a}-B{b}")
        for e in evaps:
            data_by_evap[e].append(costs[index])
            index += 1

# Configurações de barras
x = np.arange(len(labels))  # Posições dos grupos
width = 0.25  # Largura de cada barra
offsets = [-width, 0, width]  # Deslocamento para cada evap

# Cores e legenda
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
evap_labels = [f"Evap {e}" for e in evaps]

# Criar gráfico
fig, ax = plt.subplots(figsize=(14, 6))

for i, (e, offset, color) in enumerate(zip(evaps, offsets, colors)):
    ax.bar(x + offset, data_by_evap[e], width, label=evap_labels[i], color=color)

# Eixo X
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha="right")

# Labels e legenda
ax.set_ylabel("Cost Total")
ax.set_title("Grouped Bar Chart: Alpha + Beta x Evaporation Rate")
ax.legend(title="Evaporation Rate")

plt.tight_layout()
plt.show()
