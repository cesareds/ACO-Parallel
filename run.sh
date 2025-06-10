#!/bin/bash

TIMEFORMAT=%R
PROCESSADORES=$(nproc)
NAME=$(uname)
DATETIME=$(date +%Y-%m-%d_%H-%M-%S)
DIRETORIO="$(pwd)/runs"

# Cria o diretório, se não existir
mkdir -p "$DIRETORIO"

# Limpa o arquivo inicial de log
ARQUIVO="tempos_${NAME}_${DATETIME}.txt"
> "$ARQUIVO"

# Laços com valores corretos usando seq para float
for j in $(seq 1 $PROCESSADORES); do
    for alpha in $(seq 1.0 0.5 2.0); do
        for beta in $(seq 2.0 1.5 5.0); do
            for evaporation_rate in $(seq 0.1 0.25 0.6); do
                ARQUIVO_ITER="$DIRETORIO/tempos_${j}_${alpha}_${beta}_${evaporation_rate}.txt"
                echo "Rodando com $j processo(s), alpha=$alpha, beta=$beta, evap=$evaporation_rate" | tee -a "$ARQUIVO" "$ARQUIVO_ITER"
                
                for i in $(seq 1 1); do
                    echo "Execução $i:" | tee -a "$ARQUIVO_ITER"
                    exec_time=$( { time python3 main.py "$j" 50 50 1000 1000 "$evaporation_rate" "$alpha" "$beta"; } 2>&1 )
                    echo "$exec_time" | tee -a "$ARQUIVO_ITER"
                done

                echo | tee -a "$ARQUIVO_ITER"
            done
        done
    done
done
