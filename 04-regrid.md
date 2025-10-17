---
title: Regrid
subtitle: Tools for regridding MPAS-A output to regular lat-lon grids
label: page:regrid
---

```{note}
Some of the below examples may be easier to get going on
[Casper](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/casper/)[^casper]
(NCO and CDO are already installed, etc.),
but it also should be doable on your local machine or another HPC.
```

[^casper]: Or Derecho, but Derecho is usually overkill for this kind of task.

# Options

(pyremap)=

## pyremap

[pyremap](https://mpas-dev.github.io/pyremap/main/remapper/index.html)
simplifies the process of regridding MPAS data to other grids.
It helps you compute weights (using `ESMF_RegridWeightGen` or the MOAB CLI[^mbcli])
and apply them,
and works with global and limited-area meshes.

pyremap [is available](https://mpas-dev.github.io/pyremap/2.1.0/quick_start.html#installation) on conda-forge.

In the below example, we use the data we downloaded in {ref}`page:viz`.

```{include} pyremap-example.py
:lang: python

```

(nco)=

## NCO

[NCO](https://nco.sourceforge.net/) [ncremap](https://nco.sourceforge.net/nco.html#ncremap-netCDF-Remapper)
provides many facilities for regridding.

- Use `ncremap` to generate weights
  with `ESMF_RegridWeightGen` ("ERWG"),
  the TempestRemap CLI[^trcli],
  the MOAB CLI[^mbcli], or internal routines[^nco-internal]
  - ERWG and MOAB can use multiple processors with `--mpi_nbr=<n>`
- To apply weights, there are multiple ways, but `ncremap` is the most straightforward:
  - `ncremap -P mpasa -m map.nc in.nc out.nc`
    - `-P mpasa` (not always necessary) was added in NCO v5.2.6 (2024-06-20)
  - `ncremap --pdq=Time,nVertLevels,nIsoLevelsT,nIsoLevelsZ,nCells -m map.nc in.nc out.nc`
  - `ncks -m map.nc --rgr` (a variant of this command gets called by `ncremap`)

[^trcli]:
    `GenerateOverlapMesh` (overlay the source and destination meshes and compute intersections),
    `GenerateOfflineMap` (generate weights)

[^mbcli]:
    `mbconvert` (to the MOAB native format), `mbpart` (partition into pieces for parallel processing),
    `mbtempest` (generate weights using the TempestRemap library)

[^nco-internal]:
    `-a nco_con` (first-order conservative),
    `-a nco_idw` (inverse distance weighting, can extrapolate)

(nco-examples)=

### Examples

On Casper/Derecho:

```bash
module load nco
```

Let's use the grid data we downloaded in {ref}`page:viz`.

```bash
ln -s x1.2562.grid.nc grid.nc
ln -s x1.2562.static.nc static.nc
```

[MPAS-Tools](https://github.com/MPAS-Dev/MPAS-Tools)
provides multiple ways to convert grid specs in the MPAS format to SCRIP format.

`scrip_from_mpas` is available when you install the `mpas_tools` conda-forge package [^cf].

[^cf]: On Casper/Derecho:

    ```bash
    module load conda/latest
    ```

    ```bash
    mamba create -n mpas_tools -c conda-forge mpas_tools
    conda activate mpas_tools
    ```

```bash
# scrip_from_mpas requires [0, 2π) longitudes
# but our grid file has [-π, π) longitudes
PI=3.14159265359
ncap2 -s "where(lonCell < 0) lonCell = lonCell + 2*$PI;
where(lonVertex < 0) lonVertex = lonVertex + 2*$PI;
where(lonEdge < 0) lonEdge = lonEdge + 2*$PI" grid.nc grid_0to2pi.nc

# Create the SCRIP file (scrip.nc by default, use -s to change)
scrip_from_mpas -m grid_0to2pi.nc
```

`mpas2esmf` is not included in the conda-forge package
(you must compile it from within [this directory](https://github.com/MPAS-Dev/MPAS-Tools/tree/master/mesh_tools/mpas2esmf)).
You must supply a grid file with `sphere_radius` 1,
but unlike `scrip_from_mpas`, it's fine with negative longitudes.

```bash
# Create SCRIP file (mpas_scrip.nc) and ESMF grid file (mpas_esmf.nc)
mpas2esmf grid.nc "480-km" "$(date -I)"
```

Note that the results may be a bit different.
For example, `mpas2esmf` seems to set `grid_corners` to the max `nEdgesOnCell` (generally 6),
while the `scrip_from_mpas` SCRIP has `grid_corners` consistent with the original `maxEdges` dim,
and these differences cause NCO to interpret them slightly differently.
The `mpas2esmf` result also includes `rrfac` (regional refinement factor).

```bash
# Automatically generate a 1-degree target grid
# Generate weights with TempestRemap conservative monotone algorithm
ncremap -m map_con.nc -s scrip.nc -g target_grid.nc -G latlon=180,360 -a traave

# Apply weights, selecting a specific variable (terrain height from the static file)
ncremap -P mpasa -m map_con.nc -v ter static.nc out_con.nc
```

```bash
# Use the same target grid and regrid using ESMF bilinear interpolation
ncremap -m map_bil.nc -s scrip.nc -g target_grid.nc -a bilinear
ncremap -P mpasa -m map_bil.nc -v ter static.nc out_bil.nc
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

On Casper/Derecho:

```bash
module load cdo
```

Global regridding with CDO is straightforward.
As in the [NCO example](#nco-examples), we can use the data from {ref}`page:viz`,
aliased to `grid.nc` and `static.nc`.

```bash
# Generate weights for a 0.25-degree regular lat-lon grid (SCRIP format)
# (lon centers 0--359.75; lat centers -89.875--89.875)
cdo gencon,r1440x720 -setgrid,mpas:grid.nc -selgrid,1 grid.nc map_con.nc

# Apply weights
cdo remap,r1440x720,map_con.nc -selvar,ter -setgrid,mpas:grid.nc static.nc out_con.nc
```

`genbil` (bilinear) doesn't support unstructured grids.
But `gennn` (nearest neighbor) does.

(convert_mpas)=

## convert_mpas

[convert_mpas](https://github.com/mgduda/convert_mpas)[^cm] provides a simple way
to convert to a 0.5°x0.5° regular lat-lon grid (or other rectangular lat-lon grids).

[^cm]:
    Provided by the MPAS-A lead developer,
    and used in [the official virtual tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/).

To obtain it:

```bash
git clone https://github.com/mgduda/convert_mpas
cd convert_mpas
make
export PATH="$PWD:$PATH"
```

On Casper/Derecho this should _just work_. Now we can use the `convert_mpas` command[^rc].

[^rc]: For the current shell session. Add an `export` line to your `.bashrc` to make it permanent.

### Examples

Here we use the data from our global run in {ref}`page:run`.

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

Note that the start/end points are cell edges, not centers.

# Recommendations

[](#convert_mpas) for a quick remap, e.g. for checking your data with tools like ncview

Otherwise:

- [](#pyremap) for generating weights
  - Generate both conservative and bilinear weights to be used for different variables,
    nearest-neighbor can be useful as well
- [](#pyremap) for applying weights
