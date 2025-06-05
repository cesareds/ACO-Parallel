#!/bin/bash

TIMEFORMAT=%R
PROCESSADORES=$(nproc)
ARQUIVO="tempos.txt"

# Limpa o arquivo antes de escrever
> "$ARQUIVO"

echo "Serial:" | tee -a "$ARQUIVO"
exec_time=$( { time python3 main.py 1 | tee /dev/tty > /dev/null; } 2>&1 )
echo "$exec_time segundos" | tee -a "$ARQUIVO"

echo | tee -a "$ARQUIVO"

echo "Multiprocessing:" | tee -a "$ARQUIVO"
exec_time=$( { time python3 main.py $PROCESSADORES | tee /dev/tty > /dev/null; } 2>&1 )
echo "$exec_time segundos" | tee -a "$ARQUIVO"
