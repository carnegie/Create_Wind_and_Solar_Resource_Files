# Methodology

Capacity factors associated with solar and wind technologies represent the electricity generation potential per unit nameplate capacity at each time step. Capacity factors are normally estimated from real-world or modelled weather data. In our most recent studies, we have used the reanalysis dataset ERA5 published by the European Centre for Medium-Range Weather Forecasts (ECMWF). 

The code is designed to work for the Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2) as well, since some of the prevous works are done with MERRA-2 derived capacity factors. 

Our calculations of solar- and wind-capacity factor represent a first-order estimation of renewable resources and do not consider changes in the underlying surface layer properties. 

ERA5 data can be downloaded here: https://cds.climate.copernicus.eu/cdsapp#!/home 
MERRA-2 data can be downloaded here: https://www.earthdata.nasa.gov/ 

## Calculation of wind resource capacity facators

We first calculate the capacity factor for each grid cell of the reanalysis dataset. For the wind turbine, we assume a wind turbine hub height of 100 m. ERA5 has provided us the 100-m wind speed by default, while for MERRA-2, wind speed at corresponding height is interpolated based on values at 10 m and 50 m by employing a power law. The wind capacity factor calculation adopts a piecewise function consisting of four parts:

(1) below a cut-in speed (𝑢ci) of 3 m s−1, the capacity factor is zero; 
(2) between the cut-in speed of 3 m s−1 and rated speed (𝑢r) of 12 m s−1, the capacity factor is 𝑢3ci/𝑢3r; 
(3) between the rated speed of 12 m s−1 and the cut-out speed (𝑢co) of 25 m s−1, the capacity factor is 1.0, 
and (4) above the cut-out speed of 25 m s−1, the capacity factor is zero.

The corrsponding code to do this can be found under get_gridded_CF folder: get_windCF_updated230822.py

Citations related to the wind power generation referred to are:

* Shaner, M. R., Davis, S. J., Lewis, N. S. & Caldeira, K. Geophysical constraints on the reliability of solar and wind power in the United States. Energy Environ. Sci. 11, 914–925 (2018).
* Bett, P. E. & Thornton, H. E. The climatological relationships between wind and solar energy supply in Britain. Renew. Energy 87, 96–110 (2016).
* Clack, C. T. M., Alexander, A., Choukulkar, A. & MacDonald, A. E. Demonstrating the effect of vertical and directional shear for resource mapping of wind power: demonstrating the effect of vertical and directional shear for resource mapping of wind power. Wind Energy 19, 1687–1697 (2016).
* Sedaghat, A., Hassanzadeh, A., Jamali, J., Mostafaeipour, A. & Chen, W.-H. Determination of rated wind speed for maximum annual energy production of variable speed wind turbines. Appl. Energy 205, 781–789 (2017).


## Calculation of solar resource capacity facators

For solar PV, the solar zenith angle is calculated based on the geographic location and local time of that grid cell, and then the solar incidence angle is estimated assuming a single-axis tracking solar panel system (north–south direction) with a tilt of the solar panel to be 0° and a maximum tuning angle of 45°. The in-panel solar radiation is then calculated based on the solar incidence angle and incoming solar radiation at both the surface and top of the atmosphere, separating the direct and diffuse radiation components based on an empirical piecewise model. Conversions from solar radiation in combination with surrounding panel temperature to capacity factor are based on the performance model described by Huld et al. and Pfenninger and Staffell. 

The corrsponding code to do this can be found under get_gridded_CF folder: get_solarCF_updated230822.py

Citations related to the solar power generation referred to are:

* Braun, J. E. & Mitchell, J. C. Solar geometry for fixed and tracking surfaces. Solar Energy 31, 439–444 (1983).
* Meeus, J. H. Astronomical Algorithms (Willmann-Bell, 1991).
* Reindl, D. T., Beckman, W. A. & Duffie, J. A. Diffuse fraction correlations. Solar Energy 45, 1–7 (1990).
* Huld, T., Gottschalg, R., Beyer, H. G. & Topič, M. Mapping the performance of PV modules, effects of module type and data averaging. Solar Energy 84, 324–338 (2010).
* Pfenninger, S. & Staffell, I. Long-term patterns of European PV output using 30 years of validated hourly reanalysis and satellite data. Energy 114, 1251–1265 (2016).


## Integration across grid cells

As mentioned above, capacity factors are first calculated on each grid cell of the reanalysis dataset. For each study or simulation that focused on electricity system of a specific region, we aggregate grid cells within that region by doing an area-weighted average calculation. There are a few different ways we normally do:

(1) Consider only the top X% (some threshold number depending on the region) of grid cells within that region that ave the largest capacity factor values; 
(2) Consider only grid cells that have a capacity factor larger than X (some threshold number depending on the region) within that region;
(3) Consider all grid cells within that region. 

We have done mostly (1) and (3) in the past for different studies. The current default inputs for the US analysis is using the first approach with a 25% capacity factor threshold. 