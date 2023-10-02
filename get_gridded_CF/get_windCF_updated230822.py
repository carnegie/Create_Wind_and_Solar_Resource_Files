# Updated by Lei Duan on May 27th to add ERA5 comparisons
# --------
# Updated by Lei Duan on April 14th and adding a temperature limit;
# Wind turbine shuts down under temperature of -30 degree C;
# This assumption assumes wind turbine equipped with cold weather kit;
# Without cold weather kit, wind turbine can normally work untill -20 degree C.
# --------
# Updated by Lei Duan on Sep 14th to add back the temperature limit;


import cdms2 as cdms,MV2 as MV, numpy as np, cdutil
import os,sys, calendar
from Get_Info import get_info

if len(sys.argv) == 1:
    print ('Please give the following arguments: year source')
    sys.exit() 
else:
    year = sys.argv[1]
    source = sys.argv[2]

# --------------------------------------------------
# ----- Get useful infomration for each source -----
# --------------------------------------------------
info = get_info(source, year)
if source == "MERRA_2":
    data_path = info['data_path_wind']
elif source == "ERA5":
    data_path = info['data_path']
case_name = info['case_name']
isleap = info['isleap']; leap_year = 1 if isleap == True else 0
month_start = info['month_start']
month_end = info['month_end']
day_start = info['day_start']
day_end = info['day_end']
# --------------------------------------------------
if source == "MERRA_2":
    fmask = cdms.open('./SWGDN.nc')
    lsm = fmask('SWGDN', squeeze=1)
    lat = fmask.getAxis('lat')
    lon = fmask.getAxis('lon')
    lat_num = len(lat[:])
    lon_num = len(lon[:])
elif source == "ERA5":
    fmask = cdms.open('../example_ERA5/data/ERA5_landsea_mask.nc')
    lsm = fmask('lsm', squeeze=1)
    lat = fmask.getAxis('latitude')
    lon = fmask.getAxis('longitude')
    lat_num = len(lat[:])
    lon_num = len(lon[:])
# --------------------------------------------------
if leap_year == 0:
    hour_in_years=8760
    month_days={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
elif leap_year == 1:
    hour_in_years=8784
    month_days={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
fd_cam=os.listdir(data_path)
u_ci, u_r, u_co = 3, 12, 25 # cut in speed in m/s, rated speed in m/s, cut out speed in m/s

for monthly_sub_idx in np.arange(1, 13, 1):
    count_num=0
    hours_in_month = 24 * month_days[monthly_sub_idx]
    wcf = MV.array(np.zeros([hours_in_month,lat_num,lon_num])); wcf.id='wcf'; wcf.units='1'; wcf.missing_value=1e20

    for file in fd_cam:
        month = int(file[month_start:month_end]) if file[:-8] in case_name and file[-3:] in ['nc4', '.nc'] else -1
        if month == monthly_sub_idx:
            f=cdms.open(data_path+file)
            days = int(file[day_start:day_end])
            position = (days-1) * 24

            if source == "MERRA_2":
                lat = f.getAxis('lat')
                lon = f.getAxis('lon')
                u50m_tmp, v50m_tmp = f('U50M', squeeze=1), f('V50M', squeeze=1)
                u10m_tmp, v10m_tmp = f('U10M', squeeze=1), f('V10M', squeeze=1)
                ws10m = np.hypot(u10m_tmp,v10m_tmp)
                ws50m = np.hypot(u50m_tmp,v50m_tmp)
                wsc = (np.log(ws50m)-np.log(ws10m)) / (np.log(50.)-np.log(10.))
                ws100m_tmp = ws10m * (100./10.)**wsc
                ws100m = MV.filled(ws100m_tmp,0.)
                t = f('T2M',squeeze=1)-273.15-0.6
            if source == "ERA5":
                lat = f.getAxis('latitude')
                lon = f.getAxis('longitude')
                u100m_tmp, v100m_tmp = f('u100', squeeze=1), f('v100', squeeze=1)
                ws100m = MV.array(np.hypot(u100m_tmp,v100m_tmp))
                ws100m.setAxis(1, lat)
                ws100m.setAxis(2, lon)
                t = f('t2m',squeeze=1)-273.15-0.6

            ws100m[t <= -30.0] = 0  # Addational constraints
            for hr_idx in range(24):
                wcf[position+hr_idx] = ws100m[hr_idx]**3 / (u_r**3)
                wcf[position+hr_idx,  ws100m[hr_idx] <  u_ci ] = 0.
                wcf[position+hr_idx, (ws100m[hr_idx] >= u_r)  & (ws100m[hr_idx] <= u_co) ] = 1.
                wcf[position+hr_idx,  ws100m[hr_idx] >  u_co ] = 0.
            f.close
            count_num = count_num+1  
        
    if count_num == month_days[monthly_sub_idx]:
        fout=cdms.open(f'WindCFs_{str(source)}_{str(year)}_{str(monthly_sub_idx)}_Org.nc','w')
        fout.write(wcf)
        fout.close()
    else:
        print ('Days in month not match')
        sys.exit()
fmask.close()