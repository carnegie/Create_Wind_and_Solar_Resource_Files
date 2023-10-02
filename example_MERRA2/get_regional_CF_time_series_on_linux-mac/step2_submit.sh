

DATE=20200624v4


# Apparently I need to deactivate my conda env to allow
# SLURM to pick up the new env on the other side...
conda deactivate

        #"TI" \
        #"NYIS_2018" \
        #"ERCO_2018" \
        #"PJM_2018" \

for REGION in \
        "TEX" \
        "NYS" \
        ; do

    for METHOD in {1..3}; do

        for YEAR in {1980..2019}; do

            for CFS in "scf" "wcf"; do
                echo "${DATE} ${REGION} METHOD:${METHOD} YEAR:${YEAR} cfs:${CFS}"
                export EXTRA_ARGS="${YEAR} ${REGION} ${METHOD} ${DATE} ${CFS}"
                export SBATCH_JOB_NAME=cfs_${DATE}_${REGION}_mthd${METHOD}_y${YEAR}_${CFS}
                sbatch step2_run.sh
            done

        done

    done

done
