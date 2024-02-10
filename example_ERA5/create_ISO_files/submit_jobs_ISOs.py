import subprocess

# Define the years to iterate over
ISOs = ['CISO']#, 'MISO', 'ERCOT', 'ISNE']
cfs = ['wcf'] #'scf', 

for iso in ISOs:
    for cf in cfs:
        
        # Read the original bash script
        with open('run_step2_batch.sh', 'r') as file:
            bash_script = file.read()
        
        # Replace YEAR_PLACEHOLDER with the current year
        modified_script = bash_script.replace('REGION_PLACEHOLDER', iso).replace('CF_PLACEHOLDER', cf)
        
        # Write the modified script to a temporary file
        temp_script_path = f'temp_run_step2_batch_{iso}_{cf}.sh'
        with open(temp_script_path, 'w') as file:
            file.write(modified_script)
        
        # Submit the job
        subprocess.run(['sbatch', temp_script_path])
        
        # Optional: Remove the temporary file if you don't need it after submission
        # Make sure the job submission system has picked up the job before deleting
        subprocess.run(['rm', temp_script_path])

