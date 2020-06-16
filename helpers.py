

# This returns the prefix to the file name based on the MERRA2
# conventions.  See full file list this refers to in dir:
# /lustre/scratch/leiduan/MERRA2_data/
def get_prefix_name(year, is_solar=True):
    mid = 'rad' if is_solar else 'slv'
    if year <= 1991:
        prefix_name = f"MERRA2_100.tavg1_2d_{mid}_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = f"MERRA2_200.tavg1_2d_{mid}_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = f"MERRA2_300.tavg1_2d_{mid}_Nx."
    if year > 2010:
        prefix_name = f"MERRA2_400.tavg1_2d_{mid}_Nx."
    return prefix_name

