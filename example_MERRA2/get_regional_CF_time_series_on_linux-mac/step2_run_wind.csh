#!/bin/bash
#SBATCH -n 1
#SBATCH -o p_out_nercWCF25
#SBATCH -e p_err_nercWCF25
#SBATCH -p DGE
#SBATCH --mem=120000

module load python/3.6.0
source activate cdat8

echo "hellow world"
cd /lustre/scratch/leiduan/MERRA2_data/generate_CF/NYSTEX_data/
export UVCDAT_ANONYMOUS_LOG=no
python get_wind_time_series.py  2019

