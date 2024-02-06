#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --mem=8G
#SBATCH --time=2:00:00
#SBATCH --job-name=run_step2_batch
#SBATCH --output=run_step2_batch


cd /carnegie/nobackup/scratch/jdowling/Create_Wind_and_Solar_Resource_Files/example_ERA5/

source /home/jdowling/miniconda3/etc/profile.d/conda.sh

#export GRB_LICENSE_FILE=/central/software/gurobi/951/linux64/license_files/gurobi.lic

conda activate capacity_factors_env

#python run_pypsa.py -f test/test_case.xlsx
python step2_get_time_series_newERA5.py 2019 US 3 20240205 scf ERA5 ERA5
