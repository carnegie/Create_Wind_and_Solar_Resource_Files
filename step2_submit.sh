

DATE=20200623v9

for REGION in \
        "TEX" \
        "NYS" \
        "TI" \
        "NYIS_2018" \
        "ERCO_2018" \
        "PJM_2018" \
        ; do

    for METHOD in {3..3}; do

        for YEAR in {1990..2019}; do

            echo "${REGION} METHOD:${METHOD} YEAR:${YEAR}"
            export EXTRA_ARGS="${YEAR} ${REGION} ${METHOD} ${DATE}"
            export SBATCH_JOB_NAME=cfs_${DATE}_${REGION}_mthd${METHOD}_y${YEAR} 
            sbatch step2_run_solar.sh

        done

    done

done
