#!/bin/bash
#
#SBATCH --export=ALL
#SBATCH -n 1
#SBATCH -p DGE
#SBATCH --mem=120000

module load python/3.6.7
conda env list
source activate geo_stuff
conda env list

cd $SLURM_SUBMIT_DIR

export UVCDAT_ANONYMOUS_LOG=no
python step2_get_time_series.py $EXTRA_ARGS
