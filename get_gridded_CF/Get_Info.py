import calendar

def get_prefix_name(year):
    if year <= 1991:
        prefix_name = ["MERRA2_100.tavg1_2d_slv_Nx."+str(year), "MERRA2_100.tavg1_2d_rad_Nx."+str(year)]
    if year > 1991 and year <= 2000:
        prefix_name = ["MERRA2_200.tavg1_2d_slv_Nx."+str(year), "MERRA2_200.tavg1_2d_rad_Nx."+str(year)]
    if year > 2000 and year <= 2010:
        prefix_name = ["MERRA2_300.tavg1_2d_slv_Nx."+str(year), "MERRA2_300.tavg1_2d_rad_Nx."+str(year)]
    if year > 2010 and year <= 2019:
        prefix_name = ["MERRA2_400.tavg1_2d_slv_Nx."+str(year), "MERRA2_400.tavg1_2d_rad_Nx."+str(year)]
    if year == 2020:
        prefix_name = ["MERRA2_400.tavg1_2d_slv_Nx."+str(year), "MERRA2_400.tavg1_2d_rad_Nx."+str(year), 
                       "MERRA2_401.tavg1_2d_slv_Nx."+str(year), "MERRA2_401.tavg1_2d_rad_Nx."+str(year)]
    return prefix_name

def get_info(source, year):
    info = {}
    if source == "MERRA_2":
        info['data_path_wind'] = "/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/MERRA2_original_data/Wind/"
        info['data_path_solar'] = "/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/MERRA2_original_data/Solar/"
        info['case_name'] = get_prefix_name(int(year))
        info['isleap'] = calendar.isleap(int(year))
        info['lat_num'] = 361
        info['lon_num'] = 576
        info['month_start'] = -8
        info['month_end'] = -6
        info['day_start'] = -6
        info['day_end'] = -4
    if source == "ERA5":
        info['data_path'] = "/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/ERA5/ERA5_original_data/transfer/"
        info['case_name'] = f'ERA5_{year}_'
        info['isleap'] = calendar.isleap(int(year))
        info['lat_num'] = 721
        info['lon_num'] = 1440
        info['month_start'] = -8
        info['month_end'] = -6
        info['day_start'] = -5
        info['day_end'] = -3
    return info

def get_info_water(source, year):
    info = {}
    if source == "ERA5":
        info['data_path'] = "/groups/carnegie_poc/leiduan_memex/lustre_scratch/MERRA2_data/ERA5/ERA5_original_data/transfer/"
        info['case_name'] = f'ERA5_water_{year}_'
        info['isleap'] = calendar.isleap(int(year))
        info['lat_num'] = 721
        info['lon_num'] = 1440
        info['month_start'] = -8
        info['month_end'] = -6
        info['day_start'] = -5
        info['day_end'] = -3
    return info
