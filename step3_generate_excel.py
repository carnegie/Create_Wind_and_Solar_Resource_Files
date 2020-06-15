# Note that the output from this script are UTC time
# If both are UTC time then it's fine
# If not, you need to adjust either solar/wind or demand data to match the local time
import csv, numpy as np, cdms2 as cdms

data_path = 'where you put the output NetCDF files from the previous steps'
# The default template contain period from 1980 to 2019
# If you only want a shorter period, you should modify this template
ftemp = 'data/Lei_template.csv'
with open(ftemp, 'rU') as temp_f:
    reader_table = csv.reader(temp_f, delimiter=',')
    table = np.array(list(reader_table))[6:]

# Basically, the following script read the solar/wind time series from NetCDF file, and then
# attach it with a time stamp and output to csv files
s_NYS = []
w_NYS = []
for i in range(40):
    fo1_s = cdms.open(data_path+'averaged_NYS_scf'+str(1980+i)+'.nc')
    fo1_w = cdms.open(data_path+'averaged_NYS_wcf'+str(1980+i)+'.nc')
    vs_NYS = fo1_s('averaged_smask_NYS',squeeze=1)
    vw_NYS = fo1_w('averaged_wmask_NYS',squeeze=1)
    s_NYS = np.r_[s_NYS, vs_NYS]
    w_NYS = np.r_[w_NYS, vw_NYS]
new_table = np.array(np.c_[table[:,:4],  s_NYS,  table[:,:4], w_US] )    
np.savetxt('new_capacity.csv', new_table, fmt="%s", delimiter=',')
