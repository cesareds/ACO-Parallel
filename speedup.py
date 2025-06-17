import matplotlib.pyplot as plt
import re
import os
import numpy as np

# Detectar o nome do sistema para abrir o arquivo correto
name = os.uname().sysname
filename = f"tempos{name}.txt"
filename = "temposLinux.txt"
filename = "tempos110.txt"
filename = "temposDarwin2025-06-08_02-14-57.txt"

directory = "runs"

ALPHAS = [1.0, 1.5, 2.0]
BETAS = [2.0, 3.5, 5.0]
EVAPOS = [0.10, 0.35, 0.60]


alphas = [[], [], []]
betas  = [[], [], []]
evapos = [[], [], []]

tempos = [[],[],[],[],[],[],[],[]]

for a in ALPHAS:
    for b in BETAS:
        for e in EVAPOS:
            with open(f"{directory}/tempos_{a}_{b}_{e:.2f}.txt", "r") as f:
                lines = f.readlines()
                cost = None
                j = 0
                k = 0
                for line in lines:
                    l = line.split()
                    try:
                        if l[0] == 'Cost':
                            cost = int(l[-1])
                            for i in range(3):
                                if a == ALPHAS[i]:
                                    alphas[i].append(cost)
                                if b == BETAS[i]:
                                    betas[i].append(cost)
                                if e == EVAPOS[i]:
                                    evapos[i].append(cost)
                        try:
                            tempos[j].append(float(l[0]))
                            print(f"Tempos[j]{float(l[0])}, j {j}, i {k}")
                            k += 1
                            if k == 7:
                                j += 1
                                k = 0
                        except:
                            pass
                    except:
                        pass


    
for i in range(len(tempos)):
    tempos[i] = np.mean(tempos[i])
    print(f"TEMPOS FINAL {i}:\t {tempos[i]}")


# Plot
plt.figure(figsize=(8, 5))
plt.plot([x for x in range(1, 9)], tempos[0]/tempos, marker='o', label="Speedup")
plt.plot([x for x in range(1, 9)], [x for x in range(1, 9)], linestyle="--", label="Speedup ideal (linear)", color="gray")

plt.title("Speedup vs Nº de Processos")
plt.xlabel("Nº de Processos")
plt.ylabel("Speedup")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('speedup.jpg')
plt.show()