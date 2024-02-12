import cdms2 as cdms
import MV2 as MV
import sys
import cdutil
import numpy as np



# ------------------------------------------------------------------------

# 'ERA5' or 'MERRA2'
weather_data = 'MERRA2'

# When using ERA5:
if weather_data == 'ERA5':
    fmask = cdms.open('data/ERA5_landsea_mask.nc')
    land_mask_tmp = fmask('lsm', squeeze=1)[0]
    data_path = '/carnegie/nobackup/scratch/Climate_Energy_Lab/CFs/ERA5_Org/'

# When using MERRA2:
elif weather_data == 'MERRA2':
    fmask = cdms.open('../example_MERRA2/data/land_sea_mask_merra.nc4')
    land_mask_tmp = fmask('FRLAND',squeeze=1)
    data_path = '/carnegie/nobackup/scratch/Climate_Energy_Lab/CFs/MERRA2/'

else:
    print(f"Data source {weather_data} not recognized, aborting.")
    sys.exit()

lat = land_mask_tmp.getAxis(0)
lon = land_mask_tmp.getAxis(1)
fmask.close()

land_mask_tmp[land_mask_tmp>=0.5] = 1.
land_mask_tmp[land_mask_tmp<0.5]  = 0.
land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)
ocean_mask = (MV.filled(land_mask_tmp, 0) - 1) * -1
ocean_mask = MV.array(MV.masked_equal(ocean_mask,0.)) * 0 + 1
ocean_mask.setAxis(0,lat);      ocean_mask.setAxis(1,lon)

start_year = 2018
n_years = 1
scf = np.zeros([len(lat), len(lon)])
wcf = np.zeros([len(lat), len(lon)])
for i in range(n_years):
    year = i + start_year
    if weather_data == 'ERA5':
        file_name = f'Annual_ERA5_{year}_12_Org.nc'
        file_open = cdms.open(f'{data_path}{file_name}')
        scf = scf + file_open('annual_scf')/float(n_years)
        wcf = wcf + file_open('annual_wcf')/float(n_years)
        file_open.close()

    else:
        filen_name_scf = f'SolarCFs_Annual_{year}.nc'
        file_name_wcf = f'WindCFs_Annual_{year}.nc'
        scf_file_open = cdms.open(f'{data_path}{filen_name_scf}')
        wcf_file_open = cdms.open(f'{data_path}{file_name_wcf}')
        scf = scf + scf_file_open('scf_annual')/float(n_years)
        wcf = wcf + wcf_file_open('wcf_annual')/float(n_years)
        scf_file_open.close()
        wcf_file_open.close()






# ------------------------------------------------------------------------
def set_axes(var):
    var_new = MV.array(var)
    var_new.setAxis(0,lat)
    var_new.setAxis(1,lon)
    return var_new

def select_CF(sCF, wCF, idx, *i):
    if idx == 1.:
        masked_sCF = np.ceil(sCF)
        masked_wCF = np.ceil(wCF)
        s_avg_tmp = cdutil.averager(sCF,axis='yx')
        w_avg_tmp = cdutil.averager(wCF,axis='yx')
    elif idx == 2.:
        # set threshold;
        # you can change this values based on needs;
        s_thresholds = 0.26
        w_thresholds = 0.26
        # set grids with values lower than the threshold to 0;
        sCF[sCF<s_thresholds] = 0.
        wCF[wCF<w_thresholds] = 0.
        # mask grids with a value of 0 (grids that are not needed);
        masked_sCF = set_axes(MV.masked_equal(sCF,0.)*0.+1)
        masked_wCF = set_axes(MV.masked_equal(wCF,0.)*0.+1)
        s_avg_tmp = cdutil.averager(masked_sCF*sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF*wCF,axis='yx')
    elif idx ==3.:
        # set threshold, top X%;
        # you can change this values based on needs;
        p_threshold_s = 0.25
        p_threshold_w = 0.25
        # sort all grids, values for grids that are
        # outside the interested region are set to -1;
        s_reshape = np.sort(np.array(MV.filled(sCF,-1)).ravel())[::-1]
        w_reshape = np.sort(np.array(MV.filled(wCF,-1)).ravel())[::-1]
        # remove grids with values of -1;
        s_no_minus1 = s_reshape[s_reshape!=-1]
        w_no_minus1 = w_reshape[w_reshape!=-1]
        # find the threshold for the top X%   
        num_s = int(len(s_no_minus1)*p_threshold_s)
        num_w = int(len(w_no_minus1)*p_threshold_w)
        s_thresholds = s_no_minus1[num_s-1]
        w_thresholds = w_no_minus1[num_w-1]
        # mask grids with a value lower than the derived thresholds (grids that are not needed);
        masked_sCF = set_axes( MV.masked_less(sCF,s_thresholds)*0.+1 )
        masked_wCF = set_axes( MV.masked_less(wCF,w_thresholds)*0.+1 )
        s_avg_tmp = cdutil.averager(masked_sCF*sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF*wCF,axis='yx')
    print(f"For method {idx}, averaged solar capacity factor for the filtered grids is: {s_avg_tmp}")
    print(f"For method {idx}, averaged wind capacity factor for the filtered grids is: {w_avg_tmp}")
    print(f"Selected grid cells solar {np.ceil(masked_sCF).sum()}\nSelected grid cells wind {np.ceil(masked_wCF).sum()}")
    return masked_sCF, masked_wCF


def redo_loop(sCF, wCF, idx, *i):
    if idx ==3.:
        s_reshape = np.sort(np.array(MV.filled(sCF,-1)).ravel())[::-1]
        w_reshape = np.sort(np.array(MV.filled(wCF,-1)).ravel())[::-1]
        s_no_minus1 = s_reshape[s_reshape!=-1]
        w_no_minus1 = w_reshape[w_reshape!=-1]
        list_i, list_s, list_w = [], [], []
        for i in np.arange(0.01, 0.31, 0.01):
            p_threshold_s = i
            p_threshold_w = i
            num_s = int(len(s_no_minus1)*p_threshold_s)
            num_w = int(len(w_no_minus1)*p_threshold_w)
            s_thresholds = s_no_minus1[num_s-1]
            w_thresholds = w_no_minus1[num_w-1]
            masked_sCF = set_axes( MV.masked_less(sCF,s_thresholds)*0.+1 )
            masked_wCF = set_axes( MV.masked_less(wCF,w_thresholds)*0.+1 )
            s_avg_tmp = cdutil.averager(masked_sCF*sCF,axis='yx')
            w_avg_tmp = cdutil.averager(masked_wCF*wCF,axis='yx')
            list_i.append( round(i, 2) )
            list_s.append( float(s_avg_tmp) )
            list_w.append( float(w_avg_tmp) )
            print (i, s_avg_tmp, w_avg_tmp) 

        summary_array = np.zeros([3, len(list_i)])
        summary_array[0] = list_i
        summary_array[1] = list_s
        summary_array[2] = list_w
        stop 



def make_grid_cell_selections(scf, wcf, region_mask, land_mask, selection_method, region_name, out_file):
    scf_region = set_axes(scf * region_mask * land_mask)
    wcf_region = set_axes(wcf * region_mask * land_mask)
    s_mask_region, w_mask_region = select_CF(scf_region, wcf_region, selection_method)
    # s_mask_region, w_mask_region = redo_loop(scf_region, wcf_region, selection_method)
    s_mask_region.id = f'smask_{region_name}_mthd{selection_method}'
    w_mask_region.id = f'wmask_{region_name}_mthd{selection_method}'
    out_file.write(s_mask_region)
    out_file.write(w_mask_region)
    return s_mask_region, w_mask_region, scf_region * s_mask_region, wcf_region * w_mask_region




# ------------------------------------------------------------------------
# For US or ISO regions
# LetterCode = ['US']
LetterCode = ['CISO', 'MISO', 'ERCOT', 'ISNE']
outpath = 'create_ISO_files/'

results = {}
for region_name in LetterCode:
    if region_name == 'US':
        outpath = ''

    print(f"REGION: {region_name}")
    fmask=cdms.open(outpath + f'step1p1_selected_masks_{region_name}.nc')
    g=cdms.open(outpath + f'step1p2_selected_{region_name}mask_outfile_{weather_data}.nc','w') 
    mask_region= fmask(f'mask_{region_name}')
    results[region_name] = {}
    for i in [ 1, 3]:
        results[region_name][i] = make_grid_cell_selections(scf, wcf, mask_region, land_mask, i, region_name, g)
print("\nSaving masks to:")
print(g)
g.close()
fmask.close 

