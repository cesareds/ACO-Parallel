#!/bin/bash

TIMEFORMAT=%R
PROCESSADORES=$(nproc)
NAME=$(uname)
ARQUIVO="tempos$NAME.txt"

# Limpa o arquivo antes de escrever
> "$ARQUIVO"

for j in $(seq 1 $PROCESSADORES); do
    echo "Rodando com $j processo(s)" | tee -a "$ARQUIVO"
    for i in $(seq 1 5); do
        echo "Execução $i:"
        exec_time=$( { time python3 main.py $j 90 180 1000 1000 > /dev/null; } 2>&1 )
        echo "$exec_time" | tee -a "$ARQUIVO"
    done
    echo | tee -a "$ARQUIVO"
done