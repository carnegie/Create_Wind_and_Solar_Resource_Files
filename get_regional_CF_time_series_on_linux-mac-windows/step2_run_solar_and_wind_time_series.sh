#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --mem=80000
#SBATCH --time=6:00:00
#SBATCH --partition=DGE
#SBATCH --job-name=test_solar_wind
#SBATCH --output=test_solar_wind

module purge
module load python/3.6.7

export MPI_MCA_mca_base_component_show_load_errors=0
export PMIX_MCA_mca_base_component_show_load_errors=0

cd /lustre/scratch/users/eantonini/MEM/Create_Wind_and_Solar_Resource_Files
python step2_get_solar_and_wind_time_series.py
