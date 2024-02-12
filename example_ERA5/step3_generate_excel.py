# Note that the output from this script are UTC time
# If both are UTC time then it's fine
# If not, you need to adjust either solar/wind or demand data to match the local time
import csv
import numpy as np
import cdms2 as cdms
from glob import glob
import sys
import pandas as pd
import datetime


# Lei added here
# To correct one-hour lag for ERA5
hour_lag = 1


# Run this code like:
# python step3_generate_excel.py outfiles/20200623v9_TEX_mthd3/
#



# Require that this script is run with a target directory
assert(len(sys.argv) == 2), "You must provide a target directory"



# Should be of the form 'output/XXX'
# If you used the default naming in step2, XXX will be DATE_REGION_METHOD
# and can easily be split to return the region and method used which is
# needed to retrieve info from the .nc files
data_path = sys.argv[1]



info = data_path.strip('/').split('/')
f_dir = info[-1]
info = f_dir.split('_')
method = info[-1]
date = info[0]
if len(info) == 3:
    region = info[-2]
if len(info) == 4:
    region = '_'.join([info[1], info[2]])
nc_out = '_'.join([region, method])


print(f"\nRegion: {region}")
print(f"Selection method: {method}")
print(f"Processing date: {date}")
print(f".nc obj name: {nc_out}")
print(f"Data path: {data_path}")



# Find all files in directory and split into solar and wind collection
files = glob(data_path+'/*.nc')
print(f"\nFound these files in {data_path}")
files.sort()
s_files = []
w_files = []
for f in files:
    if 'scf' in f:
        s_files.append(f)
    if 'wcf' in f:
        w_files.append(f)


# Get year range from the output files
min_year = 9999
max_year = -9999
for f in files:
    print('-------', f)
    tmp = f.strip(data_path)
    tmp = tmp.replace('.nc', '')
    if tmp[-1] == '.': tmp = tmp[:-1]
    info = tmp.split('_')
    # yr = info[-1] 
    yr = info[-2] 
    yr = int(yr.replace('scf','').replace('wcf',''))
    if yr < min_year: 
        min_year = yr
    if yr > max_year:
        max_year = yr
print(f"\nFrom the list found the min and max years: {min_year}, {max_year}")


# """
def get_file_by_year(files, year):
    for f in files:
        year_filename = f.split('_')[-2].replace('scf','').replace('wcf','')
        if str(year) in f and str(year) == year_filename:
            return f
    print(f"No files found for year {year}")

# Basically, the following script read the solar/wind time series from NetCDF file, and then
# attach it with a time stamp and output to csv files
first = True
for yr in range(min_year, max_year+1):

    # Make datetime list with 1 hr spacing
    dts = pd.date_range(f"{yr}-01-01 01:00:00", f"{yr+1}-01-01 00:00:00", freq="1H")
    s_file = cdms.open(get_file_by_year(s_files, yr))
    s_nc_id = f'averaged_smask_{region}_{method}'
    s_cfs = s_file(s_nc_id,squeeze=1)
    w_file = cdms.open(get_file_by_year(w_files, yr))
    w_nc_id = f'averaged_wmask_{region}_{method}'
    w_cfs = w_file(w_nc_id,squeeze=1)
    df = pd.DataFrame({'date_time': dts, 's_cfs': s_cfs, 'w_cfs': w_cfs})
    if first:
        master = df
        first = False
    else:
        master = pd.concat([master, df])
    print(f"Year {yr}, length of df {len(master.index)}")

print("Generated dateframe")
print(master)


print("Now covert to MEM time stamps")

def make_MEM_compatible(df, save_name, cfs_var):

    with open(f'{save_name}.csv', 'w', newline='') as csvfile:

        Description_line = ['Capacity data calculated from MERRA-2']
        writer = csv.DictWriter(csvfile, fieldnames=Description_line)
        writer.writeheader()

        Blank_line = ['']
        writer = csv.DictWriter(csvfile, fieldnames=Blank_line)
        writer.writeheader()

        Begin_line = ['BEGIN_DATA']
        writer = csv.DictWriter(csvfile, fieldnames=Begin_line)
        writer.writeheader()

        fieldnames = ['year', 'month', 'day', 'hour', cfs_var]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        now_year = 0
        for i in range(len(df.index)):
            j = i+1 
            j = j if j < len(df.index) else 0
            mem_format = df.iloc[i]['date_time'] + datetime.timedelta(hours=-1)
            writer.writerow({
                'year': mem_format.year,
                'month': mem_format.month,
                'day': mem_format.day,
                'hour': mem_format.hour+1,
                cfs_var: df.iloc[j][cfs_var],
            })
            if mem_format.year != now_year:
                print(f"Processing {mem_format.year}")
                now_year = mem_format.year
    print(f"Outfile: {save_name}.csv")

make_MEM_compatible(master, data_path + f"{date}_{region}_{method}_{str(min_year)}-{str(max_year)}_solar", "s_cfs")
make_MEM_compatible(master, data_path + f"{date}_{region}_{method}_{str(min_year)}-{str(max_year)}_wind", "w_cfs")
# """
