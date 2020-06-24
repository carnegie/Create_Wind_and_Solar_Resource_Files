

DATE=20200624v3

#        "NYS" \
#        "TI" \
#        "NYIS_2018" \
#        "ERCO_2018" \
#        "PJM_2018" \

# Apparently I need to deactivate my conda env to allow
# SLURM to pick up the new env on the other side...
conda deactivate

for REGION in \
        "TEX" \
        ; do

    for METHOD in {3..3}; do

        #for YEAR in {1990..2019}; do
        for YEAR in {1990..1991}; do

            for CFS in "scf" "wcf"; do
                echo "${REGION} METHOD:${METHOD} YEAR:${YEAR} cfs:${CFS}"
                export EXTRA_ARGS="${YEAR} ${REGION} ${METHOD} ${DATE} ${CFS}"
                export SBATCH_JOB_NAME=cfs_${DATE}_${REGION}_mthd${METHOD}_y${YEAR}_${CFS}
                sbatch step2_run.sh
            done

        done

    done

done
