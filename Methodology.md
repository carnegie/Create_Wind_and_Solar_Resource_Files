# Methodology


## Calculation of wind resource capacity facators

### Power law extrapolation

MERRA-2 provides wind speeds at 10m and 50m. We model a 100m hub height by using a power law extrapolation of the 10m and 50m wind speeds, see https://en.wikipedia.org/wiki/Wind_profile_power_law

### Power output

This follows the same method used in Shaner et al. (2018).

The three wind turbine parameters for cut in speed, max output speed, and cut out speed are also based on Table 1 for GE1.6-100 in:
 * Clack et al. "Demonstrating the effect of vertical and directional shear for resource mapping of wind power"  https://doi.org/10.1002/we.1944

Also see:
 * Bett, P. E., & Thornton, H. E. (2016). The climatological relationships between wind and solar energy supply in Britain. Renewable Energy, 87, 96-110.
 * Sedaghat et al. Determination of rated wind speed for maximum annual energy production of variable speed wind turbines https://doi.org/10.1016/j.apenergy.2017.08.079


