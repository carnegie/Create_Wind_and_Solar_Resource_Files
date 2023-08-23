#!/bin/bash
#SBATCH -o o_s20
#SBATCH -e e_s20
#SBATCH -n 1
#SBATCH -p DGE
#SBATCH --mem=120000

module load python/3.6.0
source activate cdat81
cd /lustre/scratch/leiduan/MERRA2_data/generate_CF/Create210920_newERA5/

export UVCDAT_ANONYMOUS_LOG=no

REGION='US'
METHOD=3
DATE=2023-08-22
scf_or_wcf='scf'
SOURCE='ERA5'
MASK='ERA5'

YEAR=2020
python step2_get_time_series_newERA5.py ${YEAR} ${REGION} ${METHOD} ${DATE} ${scf_or_wcf} ${SOURCE} ${MASK}

