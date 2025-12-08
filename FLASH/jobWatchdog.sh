#!/bin/bash

#SBATCH -o %j.o
#SBATCH -e %j.e
#SBATCH -p skx
#SBATCH -N 16
#SBATCH --tasks-per-node=48
#SBATCH -t 08:00:00
#SBATCH --job-name=flashWatchdog

module list
pwd
date

total_nodes=$SLURM_NNODES
cores_per_node=48
total_cores=$((total_nodes * cores_per_node))
flash_cores=$((total_cores - 1))
WATCH_INTERVAL=120	#seconds

# Start watchdog in background on 1 MPI rank
ibrun -n 1 bash -c "
    sleep 600
    prev_count=0
    while true; do
        curr_count=\$(ls -1 *_part_* 2>/dev/null | wc -l)
        if [[ \"\$curr_count\" -eq \"\$prev_count\" ]]; then
            echo \"No new *_part_* files detected. Cancelling job \$SLURM_JOB_ID\"
            scancel \$SLURM_JOB_ID
            exit 0
        fi
        prev_count=\$curr_count
        sleep $WATCH_INTERVAL
    done
" &

# Run FLASH on remaining cores
scontrol show hostnames $HOSTLIST > hosts.txt
mpiexec -f hosts.txt -n $flash_cores  -ppn $cores_per_node ./flash4

