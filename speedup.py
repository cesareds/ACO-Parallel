import matplotlib.pyplot as plt
import re
import os
import numpy as np


directory_lp2d = "runs_labp2d"
directory_f110 = "runs2"

ALPHAS = [1.0, 1.5, 2.0]
BETAS = [2.0, 3.5, 5.0]
EVAPOS = [0.10, 0.35, 0.60]


alphas_lp2d = [[], [], []]
betas_lp2d  = [[], [], []]
evapos_lp2d = [[], [], []]
alphas_f110 = [[], [], []]
betas_f110  = [[], [], []]
evapos_f110 = [[], [], []]


tempos_lp2d = [[],[],[],[],[],[],[],[]]
tempos_f110 = [[],[],[],[],[],[],[],[]]

for a in ALPHAS:
    for b in BETAS:
        for e in EVAPOS:
            with open(f"{directory_lp2d}/tempos_{a}_{b}_{e:.2f}.txt", "r") as f:
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
                                    alphas_lp2d[i].append(cost)
                                if b == BETAS[i]:
                                    betas_lp2d[i].append(cost)
                                if e == EVAPOS[i]:
                                    evapos_lp2d[i].append(cost)
                        try:
                            tempos_lp2d[j].append(float(l[0]))
                            print(f"Tempos[j]{float(l[0])}, j {j}, i {k}")
                            k += 1
                            if k == 7:
                                j += 1
                                k = 0
                        except:
                            pass
                    except:
                        pass


for a in ALPHAS:
    for b in BETAS:
        for e in EVAPOS:
            with open(f"{directory_f110}/tempos_{a}_{b}_{e:.2f}.txt", "r") as f:
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
                                    alphas_f110[i].append(cost)
                                if b == BETAS[i]:
                                    betas_f110[i].append(cost)
                                if e == EVAPOS[i]:
                                    evapos_f110[i].append(cost)
                        try:
                            tempos_f110[j].append(float(l[0]))
                            print(f"Tempos[j]{float(l[0])}, j {j}, i {k}")
                            k += 1
                            if k == 7:
                                j += 1
                                k = 0
                        except:
                            pass
                    except:
                        pass


for i in range(len(tempos_lp2d)):
    tempos_lp2d[i] = np.mean(tempos_lp2d[i])
    print(f"TEMPOS LP2D FINAL {i}:\t {tempos_lp2d[i]}")

for i in range(len(tempos_f110)):
    tempos_f110[i] = np.mean(tempos_f110[i])
    print(f"TEMPOS F110 FINAL {i}:\t {tempos_f110[i]}")

# Plot
plt.figure(figsize=(10, 5))
# plt.plot([x for x in range(1, 9)], tempos_lp2d[0]/tempos_lp2d, marker='o', label="Speedup LabP2D -- ens5 -- i7 4770", color="blue")
plt.plot([x for x in range(1, 9)], tempos_f110[0]/tempos_f110, marker='o', label="Speedup F110 -- Dell -- i7 9700", color="red", markerfacecolor="green", markeredgecolor="green")
plt.plot([x for x in range(1, 9)], [x for x in range(1, 9)], linestyle="--", label="Ideal", color="gray")

plt.title("Speedup vs Nº de Processos")
plt.xlabel("Nº de Processos")
plt.ylabel("Speedup")
plt.grid(True)
plt.legend(fontsize=18)
plt.tight_layout()
plt.savefig('speedup_110.jpg', dpi=1999)
