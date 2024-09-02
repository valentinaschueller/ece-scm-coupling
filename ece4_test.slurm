#!/bin/bash
#SBATCH --job-name=ece4-test    # create a short name for your job
#SBATCH -N 1 
#SBATCH -t 00:05:00          # total run time limit (HH:MM:SS)

python ece4_example.py