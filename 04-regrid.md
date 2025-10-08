---
title: Regrid
subtitle: Tools for regridding MPAS-A output to regular lat-lon grids
---

# Options

## pyremap

[pyremap](https://mpas-dev.github.io/pyremap/main/remapper/index.html)
simplifies the process of regridding MPAS data to other grids.
It helps you compute weights (using `ESMF_RegridWeightGen` or the MOAB CLI[^mbcli])
and apply them,
and works with global and limited-area meshes.

## NCO

[NCO](https://nco.sourceforge.net/) [ncremap](https://nco.sourceforge.net/nco.html#ncremap-netCDF-Remapper)
provides many facilities for regridding.

- Use `ncremap` to generate weights
  with `ESMF_RegridWeightGen` ("ERWG"),
  the TempestRemap CLI[^trcli],
  the MOAB CLI[^mbcli], or internal routines[^nco-internal]
  - ERWG and MOAB can use multiple processors with `--mpi_nbr=<n>`
- To apply weights:
  - `ncks -m map.nc --rgr`
  - `ncremap -P mpasa -m map.nc in.nc out.nc`
    - `-P mpasa` (not always necessary) was added in NCO v5.2.6 (2024-06-20)
  - `ncremap --pdq=Time,nVertLevels,nIsoLevelsT,nIsoLevelsZ,nCells -m map.nc in.nc out.nc`

[^trcli]:
    `GenerateOverlapMesh` (overlay the source and destination meshes and compute intersections),
    `GenerateOfflineMap` (generate weights)

[^mbcli]:
    `mbconvert` (to the MOAB native format), `mbpart` (partition into pieces for parallel processing),
    `mbtempest` (generate weights using the TempestRemap library)

[^nco-internal]:
    `-a nco_con` (first-order conservative),
    `-a nco_idw` (inverse distance weighting, can extrapolate)

### Examples

```bash
# Automatically generate a 1-degree target grid
# Generate weights with TempestRemap conservative monotone algorithm
ncremap -m map.nc -s mpas_source_grid.nc -g target_grid.nc -G latlon=180,360 -a traave

# Apply weights
ncremap -P mpasa -m map.nc in.nc out.nc
```

### Notes

> In practice, it may make sense to use the default "conservative" algorithm when performing conservative regridding,
> and the "renormalized" algorithm when performing other regridding such as bilinear interpolation or nearest-neighbor.
> Another consideration is whether the fields being regridded are fluxes or state variables.
> For example, temperature (unlike heat) and concentrations (amount per unit volume)
> are not physically conserved quantities under areal-regridding
> so it often makes sense to interpolate them in a non-conservative fashion, to preserve their fine-scale structure.
> Few researchers can digest the unphysical values of temperature
> that the "conservative" option will produce in regions rife with missing values.
> A counter-example is fluxes, which should be physically conserved under areal-regridding.
> One should consider both the type of field and its conservation properties when choosing a regridding strategy.
>
> -- NCO doc, Section 3.26 Regridding

Renormalization is specified using `--rnr=<threshold>` where the threshold ranges from 0 to 1
and indicates the fraction of given destination cell covered by valid (data not missing) source cells.
Cell-times where the threshold is met preserve the mean, while others are set to missing.
[](#pyremap) supports renormalization as well (example uses 0.01).

It may be possible to use NCO RRG mode to generate weights for limited-area meshes,
but it is more involved than using pyremap.
However, you can use NCO to _apply_ pyremap-generated weights.

It is also possible to use [TempestRemap](https://github.com/ClimateGlobalChange/tempestremap)
or [MOAB](https://sigma.mcs.anl.gov/category/moab/) directly instead of through NCO.

## CDO

(convert_mpas)=

## convert_mpas

[convert_mpas](https://github.com/mgduda/convert_mpas)[^cm] provides a simple way
to convert to a 0.5°x0.5° regular lat-lon grid (or other rectangular lat-lon grids).

[^cm]:
    Provided by the MPAS-A lead developer,
    and used in [the official virtual tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/).

### Examples

```bash
# Default 0.5-degree global, one file
convert_mpas x1.10242.init.nc diag.2017-09-20_12.00.00.nc
```

```bash
# 2-degree global, all diag files
convert_mpas x1.10242.init.nc diag.*.nc nlat=90 nlon=180
```

```bash
# CONUS rectangle, all diag files
echo "startlat=25
endlat=50
nlat=25
startlon=-125
endlon=-66
nlon=59
" > target_domain

convert_mpas x1.10242.init.nc diag.*.nc
```

# Recommendations

[](#convert_mpas) for a quick remap, e.g. for checking your data with tools like ncview

Otherwise:

- [](#pyremap) for generating weights
  - Generate both conservative and bilinear weights to be used for different variables
- [](#pyremap) for applying weights
