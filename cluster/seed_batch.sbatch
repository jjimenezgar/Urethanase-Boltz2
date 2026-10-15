#!/bin/bash
#SBATCH --job-name=urethanase-seeds
#SBATCH --partition=general
#SBATCH --qos=test
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100
#SBATCH --output=logs/seeds-%j.log
set -euo pipefail
cd /scratch/jcjimenez/Urethanase-Boltz2-benchmark
export PYTHONPATH="$PWD/src"
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export XDG_CACHE_HOME="$PWD/.cache"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
export TORCH_HOME="$PWD/.cache/torch"
export TMPDIR="$PWD/.tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
source .venv/bin/activate
nvidia-smi
python -c 'import torch; assert torch.cuda.is_available(); print(torch.__version__)'
for seed in "$@"; do
    echo "Starting seed $seed at $(date -Is)"
    python scripts/run_benchmark.py --input inputs/umg_sp2_a1d5h_cached_msa.yaml --out-dir "results/seeds/seed_${seed}" --seed "$seed"
    echo "Completed seed $seed at $(date -Is)"
done
