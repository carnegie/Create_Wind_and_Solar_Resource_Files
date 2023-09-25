# update info:

# 2019-02-27: 
# (1) Added the "variable total_sunlight_tolerance". This is used to scale the maximum allowable surface radiation; 
# (2) Modify the function "cal_incidence_angles". Panel tilt is now returned to calculet the adjusted diffuse sunlight;
# (3) Add funtions to determine if year_input is a leap year or not;

# 2019-04-25:
# (1) Change the calculation for leap year

# 2019-08-27:
# (1) Change the partitions to direct and diffuse radiation; 
# (2) Change the adjustments of in-panel diffuse radiation;
# (3) Change the calculations of solar declination angle;
# (4) Change the use of Beer's law to limit direct only;
# (5) Read 2m-temperature from wind files as well.

# 2021-05-28
# Modify the code so that it works for ERA5 as well

# 2021-09-14
# Update the form of the code;
# Run the model like: python get_solarCF_updatedXXXXXXXX.py year source month;
# ERA5 has too many grids and you cannot deal with a whole year at the same time;

import cdms2 as cdms
import MV2 as MV
import numpy as np
import cdutil, os, sys, calendar,datetime
from math import degrees as deg, radians as rad
from Get_Info import get_info

if len(sys.argv) == 1:
    print ('Please give the following arguments: year source month')
    sys.exit() 
else:
    year, source, month_list = sys.argv[1], sys.argv[2], [int(sys.argv[3])]

# --------------------------------------------------
# ----- Get useful infomration for each source -----
# --------------------------------------------------
info = get_info(source, year)
if source == "MERRA_2":
    data_path = info['data_path_solar'] 
    data_path2 = info['data_path_wind'] # From here to get surface air temperature
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

###################### control variables ###################### 
max_clearness_index = 1.0
total_sunlight_tolerance = 1.0
tilt_pv_input = 0.  # in units of degree
azim_pv_input = 0.
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
R_TAMB = 20.          # Reference ambient temperature (degC)
R_TMOD = 25.          # Reference module temperature (degC)
R_IRRADIANCE = 1000.  # Reference irradiance (W/m2)
HF_free = 0.035       # Free-standing module, assuming no wind
HF_inte = 0.05        # Building-integrated module

# Assume CSI solar panel here. Numbers are derived directly from Ninja's code
k_1, k_2, k_3, k_4, k_5, k_6 = -0.017162, -0.040289, -0.004681, 0.000148, 0.000169, 0.000005
degree_to_radius = np.pi / 180.
radius_to_degree = 180. / np.pi
F11 = {1:-0.008, 2: 0.130, 3: 0.330, 4: 0.568, 5: 0.873, 6: 1.132, 7: 1.060, 8: 0.678 }
F12 = {1: 0.588, 2: 0.683, 3: 0.487, 4: 0.187, 5:-0.392, 6:-1.237, 7:-1.600, 8:-0.327 }
F13 = {1:-0.062, 2:-0.151, 3:-0.221, 4:-0.295, 5:-0.362, 6:-0.412, 7:-0.359, 8:-0.250 }
F21 = {1:-0.060, 2:-0.019, 3: 0.055, 4: 0.109, 5: 0.226, 6: 0.288, 7: 0.264, 8: 0.156 }
F22 = {1: 0.072, 2: 0.066, 3:-0.064, 4:-0.152, 5:-0.462, 6:-0.823, 7:-1.127, 8:-1.377 }
F23 = {1:-0.022, 2:-0.029, 3:-0.026, 4:-0.014, 5: 0.001, 6: 0.056, 7: 0.131, 8: 0.251 }

# Careful with the definition of sign
def cal_solar_angles(lat, lon, year, month, days, hr_idx, hr_idx_adjust, days_ord):
    lat_radius = np.array(lat) * degree_to_radius
    lat_use = np.ones([lat_num,lon_num]) * lat_radius[:,None]
    # calculate solar declination using a more accurate way
    # refer to Astronomical Algorithms, Jean Meeus and 
    # https://michelanders.blogspot.com/2010/12/calulating-sunrise-and-sunset-in-python.html
    # https://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html
    # https://github.com/kelvins/sunrisesunset/blob/master/sunrisesunset.go
    day       = datetime.date(year,month,days).toordinal() - (734124-40529) 
    time      = (hr_idx + hr_idx_adjust)/24.
    Jday      = day + 2415018.5 + time
    Jcent     = (Jday-2451545)/36525    
    Manom     = 357.52911+Jcent*(35999.05029-0.0001537*Jcent)  
    Mlong     = 280.46646+Jcent*(36000.76983+Jcent*0.0003032)
    Mobliq    = 23+(26+((21.448-Jcent*(46.815+Jcent*(0.00059-Jcent*0.001813))))/60)/60  
    obliq     = Mobliq+0.00256*np.cos(rad(125.04-1934.136*Jcent))  
    Seqcent   = np.sin(rad(Manom))*(1.914602-Jcent*(0.004817+0.000014*Jcent))+np.sin(rad(2*Manom))*(0.019993-0.000101*Jcent)+np.sin(rad(3*Manom))*0.000289  
    Struelong = Mlong+Seqcent  
    Sapplong  = Struelong-0.00569-0.00478*np.sin(rad(125.04-1934.136*Jcent))  
    sun_decli = np.arcsin(np.sin(rad(obliq))*np.sin(rad(Sapplong)))
    ha_ew     =  np.cos(rad(90.833))/(np.cos(lat_radius)*np.cos(sun_decli)) - np.tan(lat_radius)*np.tan(sun_decli) 
    ha_ew_deg = np.zeros(lat_num)
    ha_ew_deg[ (ha_ew>=-1)&(ha_ew<=1) ] = np.arccos( ha_ew[(ha_ew>=-1)&(ha_ew<=1)] ) * radius_to_degree
    ha_ew_deg[ (ha_ew<-1) ] = 180.
    ha_ew_deg[ (ha_ew >1) ] = 0.
    ha_ew_use_deg = np.ones([lat_num,lon_num]) * ha_ew_deg[:,None] 
    # 0 -> always dark; 180 -> always day; 0-180 -> sunrise or sunset angle;
    
    local_time = np.zeros(lon_num)
    lon_array = np.array(lon)
    local_time[lon_array<0.] = (24. + lon_array[lon_array<0.]/15. + hr_idx) + hr_idx_adjust
    local_time[lon_array>=0.] = (lon_array[lon_array>=0.]/15 + hr_idx) + hr_idx_adjust
    local_time[local_time>24] = local_time[local_time>24]-24.
    ha_deg = (local_time-12.)*(-15.)
    ha_rad = (local_time-12.)*(-15.) * degree_to_radius 
    ha_use_rad = np.ones([lat_num,lon_num]) * ha_rad
    ha_use_deg = np.ones([lat_num,lon_num]) * ha_deg # positive -> before noon; negative -> after noon
    
    cosine_zenith = np.sin(sun_decli) * np.sin(lat_use) + np.cos(sun_decli) * np.cos(lat_use) * np.cos(ha_use_rad)
    zenith_rad = np.arccos( cosine_zenith )
    
    term1 = np.zeros([lat_num,lon_num]) # if 
    term2 = np.zeros([lat_num,lon_num]) # if facing toward the equator
    term3 = np.zeros([lat_num,lon_num]) 
    term0 = np.arcsin( (np.sin(ha_use_rad)*np.cos(sun_decli)) / (np.sin(zenith_rad)) ) # term0>0, before noon and term0<0, after noon
    term1[np.abs(ha_use_deg)<=ha_ew_use_deg] = 1.     # term1 > 0, day and term1 < 0, night
    term1[np.abs(ha_use_deg) >ha_ew_use_deg] = -1.    
    term2[lat_use*(lat_use-sun_decli)>=0] = 1         # term2 > 0, face the sun
    term2[lat_use*(lat_use-sun_decli) <0] = -1
    term3[ha_use_rad>=0] = 1
    term3[ha_use_rad <0] = -1
    solar_azi_rad = term0*term1*term2 + (1-term1*term2)/2.*term3*np.pi
    return zenith_rad, solar_azi_rad, ha_rad

def cal_incidence_angles(zenith, solar_azi, tilt_pv, azim_pv, pv_type):
    max_azim_angle = 360.*degree_to_radius         # for 1-axis vertical PV
    max_turn_angle = 45. *degree_to_radius         # for 1-axis horizontal (with and without tilt)
    incidence_rad = np.zeros([lat_num,lon_num])
    if pv_type == 'f':
        print ('Using fixed tilt and azim solar panel')
        incidence_rad = np.arccos(np.cos(zenith)*np.cos(tilt_pv) + np.sin(zenith)*np.sin(tilt_pv)*np.cos(solar_azi-azim_pv))
        panel_tilt = tilt_pv
    elif pv_type == 'v':
        print ('Using 1-axis tracking panel, with vertical axis')
        incidence_rad = np.where( (solar_azi<=max_azim_angle)&(zenith<=tilt_pv)&(solar_azi>=0.), tilt_pv - zenith, incidence_rad) 
        incidence_rad = np.where( (solar_azi>=(-1)*max_azim_angle)&(zenith<=tilt_pv)&(solar_azi<=0.), tilt_pv - zenith, incidence_rad)
        incidence_rad = np.where( (solar_azi<=max_azim_angle)&(zenith>tilt_pv)&(solar_azi>=0.), zenith - tilt_pv, incidence_rad) 
        incidence_rad = np.where( (solar_azi>=(-1)*max_azim_angle)&(zenith>tilt_pv)&(solar_azi<=0.), zenith - tilt_pv, incidence_rad)
        incidence_rad = np.where( (solar_azi>max_azim_angle), np.arccos(np.cos(zenith)*np.cos(tilt_pv)+np.sin(zenith)*np.sin(tilt_pv)*np.cos(solar_azi-max_azim_angle)), incidence_rad )
        incidence_rad = np.where( (solar_azi<(-1)*max_azim_angle), np.arccos(np.cos(zenith)*np.cos(tilt_pv)+np.sin(zenith)*np.sin(tilt_pv)*np.cos(solar_azi-max_azim_angle)), incidence_rad )
        panel_tilt = tilt_pv  ### is this correct?
    elif pv_type == 'h':
        print ('Using 1-axis tracking panel, with horizontal axis, no tilt, horizontal axis')
        # adjusted tilt is the tilt after the panel rotated on its axis 
        # the tilt is the angle between surface normal and panel surface normal
        adjusted_azim = np.zeros([lat_num,lon_num])
        adjusted_azim[ (solar_azi-azim_pv)>=0. ] = azim_pv[ (solar_azi-azim_pv)>=0. ] + np.pi/2.
        adjusted_azim[ (solar_azi-azim_pv) <0. ] = azim_pv[ (solar_azi-azim_pv) <0. ] - np.pi/2.
        adjusted_tilt = np.arctan(np.tan(zenith)*np.cos(adjusted_azim-solar_azi))
        adjusted_tilt[adjusted_tilt<0.] = adjusted_tilt[adjusted_tilt<0.]+np.pi
        adjusted_tilt[adjusted_tilt>max_turn_angle] = max_turn_angle
        adjusted_tilt[adjusted_tilt<max_turn_angle*(-1)] = max_turn_angle * (-1)
        incidence_rad = np.arccos(np.cos(zenith)*np.cos(adjusted_tilt) + np.sin(zenith)*np.sin(adjusted_tilt)*np.cos(solar_azi-adjusted_azim))
        panel_tilt = adjusted_tilt
    elif pv_type == 'ht':
        print ('Using 1-axis tracking panel, with horizontal axis, with tilt')
        incidence_rad_tmp = np.arccos(np.cos(zenith)*np.cos(tilt_pv) + np.sin(zenith)*np.sin(tilt_pv)*np.cos(solar_azi-azim_pv))
        term1 = np.zeros([lat_num,lon_num])
        term2 = np.zeros([lat_num,lon_num])
        term0 = azim_pv + np.arctan( np.sin(zenith)*np.sin(solar_azi-azim_pv)/np.cos(incidence_rad_tmp)/np.sin(tilt_pv) )
        term1[(term0-azim_pv)*(solar_azi-azim_pv)>=0.] = 0.
        term1[(term0-azim_pv)*(solar_azi-azim_pv) <0.] = 1.
        term2[(solar_azi-azim_pv)>=0.] = 1.
        term2[(solar_azi-azim_pv) <0.] = -1.
        adjusted_azim = term0 + term1*term2*np.pi
        term00 = np.arctan(np.tan(tilt_pv)/np.cos(term0-azim_pv))
        term11 = np.zeros([lat_num,lon_num])
        term11[term00>=0] = 0.
        term11[term00 <0] = 1.
        adjusted_tilt = term00+term11*np.pi 
        incidence_rad = np.arccos(np.cos(zenith)*np.cos(adjusted_tilt) + np.sin(zenith)*np.sin(adjusted_tilt)*np.cos(solar_azi-adjusted_azim))
        panel_tilt = adjusted_tilt
    elif pv_type == '2a':
        print ('Using 2-axis tracking panela')
        incidence_rad = 0.
        panel_tilt = zenith
    #incidence_deg = incidence_rad * radius_to_degree
    return incidence_rad, panel_tilt

def replace_nan(var):
    whereisNan = np.isnan(var)
    var[whereisNan] = 0.
    return var

def replace_inf(var):
    whereisinf = np.isinf(var)
    var[whereisinf] = 0.
    return var


# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# ---------------------------------- main function starts here ----------------------------------
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
tilt_pv = np.zeros([lat_num,lon_num]) + tilt_pv_input * degree_to_radius
azim_pv = np.zeros([lat_num,lon_num]) + azim_pv_input * degree_to_radius
df = np.zeros([lat_num,lon_num])

for monthly_sub_idx in month_list:
    count_num = 0                                        # Count days in a month
    hours_in_month = 24 * month_days[monthly_sub_idx]    # Total hours in a month
    scf = MV.array(np.zeros([hours_in_month,lat_num,lon_num])); scf.id='scf'; scf.units='1'; scf.missing_value=1e20
    
    # For both MERRA2 and ERA5, the original input data is daily (24 hours) each file;
    # "case_name" include that all months in that year
    # For the new code, ouput monthly CFs instead of yearly;
    for file in fd_cam:  
        month = int(file[month_start:month_end]) if file[:-8] in case_name and file[-3:] in ['nc4', '.nc'] else -1
        if month == monthly_sub_idx:
            f=cdms.open(data_path+file)
            days = int(file[day_start:day_end])
            days_ord = days if month == 1 else (np.sum(month_days_array[:month-1]) + days)
            position = (days-1) * 24

            # MERRA2 data starts from 00:30 for the first hour
            # ERA5 data starts from 00:00 for the first hour
            # Use "hr_idx_adjust" to account for this difference and adjust the angle calculations
            if source == "MERRA_2":
                hr_idx_adjust = 0.5 
                lat = f.getAxis('lat')
                lon = f.getAxis('lon')
                swgdn_tmp = MV.filled(f('SWGDN',squeeze=1),0.)
                swtdn_tmp = MV.filled(f('SWTDN',squeeze=1),0.)
                file2 = file[:20]+'slv'+file[-16:]
                fwind = cdms.open(data_path2+file2)
                t = fwind('T2M',squeeze=1)-273.15
                fwind.close()
            if source == "ERA5":
                hr_idx_adjust = 0.0 
                lat_tmp = f.getAxis('latitude')
                lon_tmp = f.getAxis('longitude')
                swgdn_tmp = MV.filled(f('ssrd',squeeze=1)/3600.,0.) # Convert from J/m2 to W/m2
                swtdn_tmp = MV.filled(f('tisr',squeeze=1)/3600.,0.)
                t = f('t2m',squeeze=1)-273.15

            kt = np.zeros([24, lat_num, lon_num])
            kt[swtdn_tmp != 0.] = ( swgdn_tmp[swtdn_tmp != 0.]/swtdn_tmp[swtdn_tmp != 0.] )
            kt[kt < 0.] = 0.

            for hr_idx in range(24):
                zenith, solar_azi, ha = cal_solar_angles(lat, lon, int(year), month, days, hr_idx, hr_idx_adjust, days_ord)
                incidence_rad, panel_tilt_rad = cal_incidence_angles(zenith, solar_azi, tilt_pv, azim_pv, 'h')
                mask1 = MV.filled(MV.masked_equal(swtdn_tmp[hr_idx]   ,0)*0+1,0)
                mask2 = MV.filled(MV.masked_greater_equal(zenith,np.pi/2)*0+1,0)
                cosine_zenith = np.cos(zenith)*mask1*mask2
                #cosine_zenith[(cosine_zenith>0)&(cosine_zenith<0.087)] = 0.087 ### do we want it here?
                cosine_incide = np.cos(incidence_rad) * mask1*mask2
                adjust_factor_dni = replace_inf(replace_nan(cosine_incide / cosine_zenith))
                adjust_factor_dni[(adjust_factor_dni<1.)]=1.
                
                maximum_index = np.argwhere( swgdn_tmp[hr_idx]== np.max(swgdn_tmp[hr_idx]) )
                base = swgdn_tmp[hr_idx][maximum_index[0,0]][maximum_index[0,1]]/swtdn_tmp[hr_idx][maximum_index[0,0]][maximum_index[0,1]]
                cons = swtdn_tmp[hr_idx][maximum_index[0,0]][maximum_index[0,1]]
                potential_max_solar = np.zeros([lat_num,lon_num])
                potential_max_solar = np.where(cosine_zenith!=0., cons*base**(1/cosine_zenith), potential_max_solar) 
                
                kt2 = kt[hr_idx]
                df = np.zeros([lat_num,lon_num])
                df = np.where( kt2 <= 0.30, 1.020 - 0.254 * kt2 + 0.0123 * cosine_zenith, df)
                df = np.where( (kt2 > 0.30) & (kt2 < 0.78), 1.4 - 1.749 * kt2 + 0.0177 * cosine_zenith, df)
                df = np.where( kt2 >= 0.78, 0.486 * kt2 - 0.182 * cosine_zenith, df)
                df = np.where( kt2> 1.0, 1.0, df)
                dhi = df * swgdn_tmp[hr_idx]
                dni = (swgdn_tmp[hr_idx] - dhi)

                # Corrections for direct/diffuse radiation
                z = zenith  #in radius
                kappa   = 1.041
                airmass = replace_inf(replace_nan(1./cosine_zenith))
                delta   = dhi * airmass / cons
                eps     = replace_inf(replace_nan(swgdn_tmp[hr_idx] / dhi + kappa * (z ** 3)) / (1 + kappa * (z ** 3)))
                F1 = np.zeros([lat_num,lon_num])
                F1[(1.000<eps)&(eps<=1.065)] = F11[1] + F12[1] * delta[(1.000<eps)&(eps<=1.065)] + F13[1]*z[(1.000<eps)&(eps<=1.065)]
                F1[(1.065<eps)&(eps<=1.230)] = F11[2] + F12[2] * delta[(1.065<eps)&(eps<=1.230)] + F13[2]*z[(1.065<eps)&(eps<=1.230)]
                F1[(1.230<eps)&(eps<=1.500)] = F11[3] + F12[3] * delta[(1.230<eps)&(eps<=1.500)] + F13[3]*z[(1.230<eps)&(eps<=1.500)]
                F1[(1.500<eps)&(eps<=1.950)] = F11[4] + F12[4] * delta[(1.500<eps)&(eps<=1.950)] + F13[4]*z[(1.500<eps)&(eps<=1.950)]
                F1[(1.950<eps)&(eps<=2.800)] = F11[5] + F12[5] * delta[(1.950<eps)&(eps<=2.800)] + F13[5]*z[(1.950<eps)&(eps<=2.800)]
                F1[(2.800<eps)&(eps<=4.500)] = F11[6] + F12[6] * delta[(2.800<eps)&(eps<=4.500)] + F13[6]*z[(2.800<eps)&(eps<=4.500)]
                F1[(4.500<eps)&(eps<=6.200)] = F11[7] + F12[7] * delta[(4.500<eps)&(eps<=6.200)] + F13[7]*z[(4.500<eps)&(eps<=6.200)]
                F1[(6.200<eps)]              = F11[8] + F12[8] * delta[(6.200<eps)]              + F13[8]*z[(6.200<eps)] 
                F2 = np.zeros([lat_num,lon_num])
                F2[(1.000<eps)&(eps<=1.065)] = F21[1] + F22[1] * delta[(1.000<eps)&(eps<=1.065)] + F23[1]*z[(1.000<eps)&(eps<=1.065)]
                F2[(1.065<eps)&(eps<=1.230)] = F21[2] + F22[2] * delta[(1.065<eps)&(eps<=1.230)] + F23[2]*z[(1.065<eps)&(eps<=1.230)]
                F2[(1.230<eps)&(eps<=1.500)] = F21[3] + F22[3] * delta[(1.230<eps)&(eps<=1.500)] + F23[3]*z[(1.230<eps)&(eps<=1.500)]
                F2[(1.500<eps)&(eps<=1.950)] = F21[4] + F22[4] * delta[(1.500<eps)&(eps<=1.950)] + F23[4]*z[(1.500<eps)&(eps<=1.950)]
                F2[(1.950<eps)&(eps<=2.800)] = F21[5] + F22[5] * delta[(1.950<eps)&(eps<=2.800)] + F23[5]*z[(1.950<eps)&(eps<=2.800)]
                F2[(2.800<eps)&(eps<=4.500)] = F21[6] + F22[6] * delta[(2.800<eps)&(eps<=4.500)] + F23[6]*z[(2.800<eps)&(eps<=4.500)]
                F2[(4.500<eps)&(eps<=6.200)] = F21[7] + F22[7] * delta[(4.500<eps)&(eps<=6.200)] + F23[7]*z[(4.500<eps)&(eps<=6.200)]
                F2[(6.200<eps)]              = F21[8] + F22[8] * delta[(6.200<eps)]              + F23[8]*z[(6.200<eps)] 
                dni_adjust  = dni * adjust_factor_dni  
                dhi_adjust  = dhi * ( (1-F1)*(1+np.cos(panel_tilt_rad))/2 + F2*np.sin(panel_tilt_rad) )
                dhi_adjust2 = dhi * F1 * adjust_factor_dni
                dni_adjust2 = np.minimum(dni_adjust+dhi_adjust2, potential_max_solar * total_sunlight_tolerance)
                rad_adjust  = replace_nan(dni_adjust2 + dhi_adjust)

                # Now calculate solar capacity factor
                # Huld, T. et al., 2010. Mapping the performance of PV modules, effects of module type and data averaging. Solar Energy, 84(2), p.324-338. DOI: 10.1016/j.solener.2009.12.002
                T_ = np.array((1*t[hr_idx] + HF_free * rad_adjust) - R_TMOD )
                G_ = np.array(rad_adjust / R_IRRADIANCE)
                index = int(position+hr_idx)
                scf[index,G_==0.] = 0.
                scf[index,G_ >0.] = G_[G_>0.] * (1+k_1*np.log(G_[G_>0.])+k_2*(np.log(G_[G_>0.]))**2 + T_[G_>0.]*(k_3+k_4*(np.log(G_[G_>0.]))+k_5*(np.log(G_[G_>0.]))**2) + k_6*(T_[G_>0.]**2))
            f.close()
            count_num = count_num + 1 

    if count_num == month_days[monthly_sub_idx]:
        # Total days match days in month
        fout=cdms.open(f'SolarCFs_{str(source)}_{str(year)}_{str(monthly_sub_idx)}_Org.nc','w')
        fout.write(scf)
        fout.close()
    else:
        print ('Days in month not match')
        sys.exit()

    del(scf)
    del(swgdn_tmp)
    del(swtdn_tmp)
    del(t)
    
fmask.close()