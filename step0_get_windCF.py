import cdms2 as cdms,MV2 as MV, numpy as np,cdutil
import os,sys
import calendar

def get_prefix_name(year):
    if year <= 1991:
        prefix_name = "MERRA2_100.tavg1_2d_slv_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = "MERRA2_200.tavg1_2d_slv_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = "MERRA2_300.tavg1_2d_slv_Nx."
    if year > 2010:
        prefix_name = "MERRA2_400.tavg1_2d_slv_Nx."
    return prefix_name

if len(sys.argv) == 1:
    year = 2016
else:
    year = sys.argv[1]

###################### control variables ###################### 
case_name = get_prefix_name(int(year))+str(year)
isleap = calendar.isleap(int(year))
if isleap == True:
    leap_year = 1
else:
    leap_year = 0
data_path="/lustre/scratch/leiduan/MERRA2_data/Wind/"
lat_num = 361
lon_num = 576
###############################################################

if leap_year == 0:
    hour_in_years=8760
    month_days={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_days_array = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
elif leap_year == 1:
    hour_in_years=8784
    month_days={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_days_array = np.array([31,29,31,30,31,30,31,31,30,31,30,31])

fd_cam=os.listdir(data_path)

u_ci = 3 # cut in speed in m/s
u_r = 12 # rated speed in m/s
u_co = 25 # cut out speed in m/s

wcf = MV.array(np.zeros([hour_in_years,lat_num,lon_num])); wcf.id='wcf'; wcf.units='1'; wcf.missing_value = 1e20
count_num=1
for file in fd_cam:
        if file[:-8] == case_name and file[-4:]=='.nc4':
                print (file, count_num)
                f=cdms.open(data_path+file)
                month = int(file[-8:-6])
                days = int(file[-6:-4])
                if month == 1:
                    position = (0 + days-1) * 24
                else:
                    position = (np.sum(month_days_array[:month-1]) + (days-1)) *24
                print (month, days, position)

                lat = f.getAxis('lat')
                lon = f.getAxis('lon')
                if len(lat) != lat_num or len(lon) != lon_num:
                    print ('lat/lon number error')
                    sys.exit

                u50m_tmp = f('U50M')
                v50m_tmp = f('V50M')
                u10m_tmp = f('U10M')
                v10m_tmp = f('V10M')
                ws10m = np.hypot(u10m_tmp,v10m_tmp)
                ws50m = np.hypot(u50m_tmp,v50m_tmp)
                wsc = (np.log(ws50m)-np.log(ws10m)) / (np.log(50.)-np.log(10.))
                ws100m_tmp = ws10m * (100./10.)**wsc
                ws100m = MV.filled(ws100m_tmp,0.)               
 
                for hr_idx in range(24):
                    # wind_speed < u_ci = 0.
                    # wind_speed > u_co = 0.
                    # wind_speed >= u_ci and wind_speed < u_r = v**3/u_r**2
                    # wind_speed >= u_r and wind_speed <= 1.
                    wcf[position+hr_idx,  ws100m[hr_idx] <  u_ci ] = 0.
                    wcf[position+hr_idx, (ws100m[hr_idx] >= u_ci) & (ws100m[hr_idx] <  u_r)  ] = ws100m[hr_idx, (ws100m[hr_idx] >= u_ci) & (ws100m[hr_idx] < u_r)]**3 / (u_r**3)
                    wcf[position+hr_idx, (ws100m[hr_idx] >= u_r)  & (ws100m[hr_idx] <= u_co) ] = 1.
                    wcf[position+hr_idx,  ws100m[hr_idx] >  u_co ] = 0.
                f.close
                count_num = count_num+1

# use NetCDF3 Classic format
#cdms.setNetcdfShuffleFlag(0)      # netcdf3 classic...
#cdms.setNetcdfDeflateFlag(0)      # netcdf3 classic...
#cdms.setNetcdfDeflateLevelFlag(0) # netcdf3 classic...

fout=cdms.open(case_name+'_wcf100m031225.nc','w')
fout.write(wcf)
fout.close()

wcf_annual = cdutil.averager(wcf,axis=0,weights='equal')
wcf_annual.id='wcf_annual'
gout=cdms.open(case_name+'_wcf100m031225_annual.nc','w')
gout.write(wcf_annual)
gout.close()

