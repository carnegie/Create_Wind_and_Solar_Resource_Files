#!/bin/bash
#SBATCH -n 1
#SBATCH -o out_wind
#SBATCH -e err_wind
#SBATCH -p DGE
#SBATCH --mem=80000

module load python/3.6.0
source activate cdat8

export UVCDAT_ANONYMOUS_LOG=no
echo "hellow world"
cd /lustre/scratch/leiduan/MERRA2_data/
python step0_get_windCF.py 2019
