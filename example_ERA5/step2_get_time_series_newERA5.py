import cdms2 as cdms
import MV2 as MV
import numpy as np
import sys, cdutil, os

print("\nRunning ")
print(sys.argv[0])
print("Input arg list")
print(sys.argv)

# Default year is 2019 when no year info is provided
year = 2019 if len(sys.argv) <= 1 else int(sys.argv[1])
region = 'US' if len(sys.argv) <= 2 else sys.argv[2]
mthd = 1 if len(sys.argv) <= 3 else int(sys.argv[3])
date = 'Nan' if len(sys.argv) <= 4 else sys.argv[4]
scf_or_wcf = 'scf' if len(sys.argv) <= 5 else sys.argv[5]
source = 'Nan' if len(sys.argv) <= 6 else sys.argv[6]
mask = 'Nan' if len(sys.argv) <= 7 else sys.argv[7]

#landsea files:
ERA5path = '/carnegie/nobackup/scratch/jdowling/Create_Wind_and_Solar_Resource_Files/example_ERA5/data/ERA5_landsea_mask.nc'
MERRA2path = '/carnegie/nobackup/scratch/jdowling/Create_Wind_and_Solar_Resource_Files/example_ERA5/data/land_sea_mask_merra.nc4'

if source == 'MERRA_2': 
    print ('Dealing with ERA5 only')
    stop

if source == 'ERA5': 
    if mask == 'MERRA_2':
        print ('Dealing only ERA5 with ERA5 mask only')
        stop 
    if mask == 'ERA5':
        # data_patch = '/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/ERA5/ERA5_CF_Data/orginal_resolution/'
        data_patch = '/carnegie/nobackup/scratch/jdowling/CFs/ERA5/'
        app = 'SolarCFs_ERA5_' if scf_or_wcf == 'scf' else 'WindCFs_ERA5_'
        pre = 's' if scf_or_wcf == 'scf' else 'w'
        # f_mask = cdms.open('/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/ERA5_landsea_mask.nc')
        f_mask = cdms.open(ERA5path)
        v = f_mask('lsm', squeeze=1)[0]
        lat = v.getAxis(0)
        lon = v.getAxis(1)
        f_mask.close() 
        case_name = [] 
        for month_idx in np.arange(1, 13, 1):
            # case_name.append(app + str(year) + '_' + str(month_idx) + '_Org.nc')
            case_name.append(app + str(year) + '_' + str(month_idx) + '.nc')
        # fm = cdms.open('recreateWrong_selected_USmask_outfile_ERA5.nc')
        fm = cdms.open('step1p2_selected_USmask_outfile_ERA5.nc')


# Region to do list and correspondiing mask file:
TwoLettersCode = ['US']

for reg_idx in TwoLettersCode:
    region = reg_idx
    region_mask = pre+'mask_%s_mthd%i' % (region, mthd)
    mask_idx = MV.array(fm(region_mask))

    if not os.path.exists('outfiles'):
        os.makedirs('outfiles')
    if not os.path.exists('outfiles/%s_%s_mthd%i' % (date, region, mthd)):
        os.makedirs('outfiles/%s_%s_mthd%i' % (date, region, mthd))

    # Assemble monthly data
    g=cdms.open('outfiles/%s_%s_mthd%i/averaged_%s_%s%i_%s.nc' % (date, region, mthd, region, scf_or_wcf, year, source), 'w') 
    YearlyArray = []
    for case_name_idx in case_name:
        fs = cdms.open(data_patch+case_name_idx)
        cfs = MV.array(fs(scf_or_wcf, squeeze=1))
        cfs[cfs<0] = 0.
        cfs[cfs>1] = 1.
        fs.close()

        len_axis = len(cfs.getAxis(0))

        cfs_idx = MV.array(cfs[:] * mask_idx)
        cfs_idx.setAxis(1,lat)
        cfs_idx.setAxis(2,lon)
        new_data = cdutil.averager(cfs_idx, axis='yx')
        YearlyArray = np.r_[YearlyArray, new_data]

    YearlyArray = MV.array(YearlyArray)
    YearlyArray.id = 'averaged_' + region_mask
    g.write(YearlyArray)
    g.close()
    del(cfs_idx)
    del(YearlyArray) 