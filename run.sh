#!/bin/bash

rm grids2/*
rm runs2/*

export LC_NUMERIC=C

TIMEFORMAT=%R
PROCESSADORES=$(nproc)
DIRETORIO="$(pwd)/runs2"

mkdir -p "$DIRETORIO"

for alpha in $(seq 1.0 0.5 2.0); do
    for beta in $(seq 2.0 1.5 5.0); do
        for evaporation_rate in $(seq 0.1 0.25 0.6); do
            ARQUIVO_ITER="$DIRETORIO/tempos_${alpha}_${beta}_${evaporation_rate}.txt"
            touch $ARQUIVO_ITER
            
            for j in $(seq 1 $PROCESSADORES); do
            echo "Rodando com $j processo(s), alpha=$alpha, beta=$beta, evap=$evaporation_rate" | tee -a "$ARQUIVO_ITER"
                for i in $(seq 1 10); do
                    echo "Execução $i:" | tee -a "$ARQUIVO_ITER"
                    exec_time=$( { time python3 main.py "$j" 50 50 500 500 "$evaporation_rate" "$alpha" "$beta" "$i"; } 2>&1 )
                    echo "$exec_time" | tee -a "$ARQUIVO_ITER"
                done
            done
            echo | tee -a "$ARQUIVO_ITER"
        done
    done
done
