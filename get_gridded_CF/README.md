# Calculate gridded capacity factors for wind and solar

Change the path in ```Get_Info.py``` to the path of the folder containing the ERA5 or MERRA2 data.
Run the two scripts in this directory to obtain grid cell level capacity factors for wind and solar for a specific year, dataset and month:

```python get_solarCF_updated230822.py 2015 ERA5 1```

```python get_windCF_updated230822.py 2015 ERA5 1```

The first argument is the year, the second is the dataset (ERA5 or MERRA2) and the third is the month.

The output files resulting from this are of the format ```SolarCFs_source_year_month_Org.nc``` and ```WindCFs_source_year_month_Org.nc```. 