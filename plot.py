import matplotlib.pyplot as plt
import re
import os

# Detectar o nome do sistema para abrir o arquivo correto
name = os.uname().sysname
filename = f"tempos{name}.txt"

# Inicialização
tempos = {}
n_procs = None

with open(filename, "r") as f:
    linhas = f.readlines()

for linha in linhas:
    if linha.startswith("Rodando com"):
        n_procs = int(re.search(r"\d+", linha).group())
        tempos[n_procs] = []
    elif re.match(r"^\d+\.\d+$", linha.strip()):
        tempos[n_procs].append(float(linha.strip()))

# Cálculo de médias e speedup
medias = {k: sum(v) / len(v) for k, v in tempos.items()}
tempo_seq = medias[1]
speedup = {k: tempo_seq / v for k, v in medias.items()}

# Ordenação
procs = sorted(speedup.keys())
speedup_vals = [speedup[k] for k in procs]

# Plot
plt.figure(figsize=(8, 5))
plt.plot(procs, speedup_vals, marker='o', label="Speedup")
plt.plot(procs, procs, linestyle="--", label="Speedup ideal (linear)", color="gray")

plt.title("Speedup vs Nº de Processos")
plt.xlabel("Nº de Processos")
plt.ylabel("Speedup")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
