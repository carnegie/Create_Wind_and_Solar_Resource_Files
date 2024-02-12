#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=0
#SBATCH --time=4:00:00
#SBATCH --job-name=run_step2_batch
#SBATCH --output=run_step2_batch


cd /carnegie/nobackup/scratch/awongel/Create_Wind_and_Solar_Resource_Files/example_ERA5/

source /home/awongel/miniconda3/etc/profile.d/conda.sh

conda activate capacity_factors_env

python step2_get_time_series_newERA5.py 2018 REGION_PLACEHOLDER 3 20240211 CF_PLACEHOLDER MERRA2 MERRA2

