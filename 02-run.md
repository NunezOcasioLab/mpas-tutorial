---
title: Run
subtitle: Running MPAS on NSF NCAR Derecho
---

# Global

We will use the quasi-uniform 240-km mesh (10242 cells),
as in the [official virtual tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/)
(Section 1.3).

## Run directory

First we build out our run directory.

```{code} bash
cd $SCRATCH
mkdir mpas-global-240km
cd $_

ln -s /glade/campaign/mmm/wmr/mpas_tutorial/meshes/x1.10242.grid.nc .

ln -s /glade/campaign/mmm/wmr/mpas_tutorial/meshes/x1.10242.graph.info.part.32 .
ln -s ~/MPAS-Model_v8.3/init_atmosphere_model .
cp ~/MPAS-Model_v8.3/namelist.init_atmosphere .
cp ~/MPAS-Model_v8.3/streams.init_atmosphere .

ln -s /glade/campaign/mmm/wmr/mpas_tutorial/meshes/x1.10242.graph.info.part.128 .
ln -s ~/MPAS-Model_v8.3/atmosphere_model .
cp ~/MPAS-Model_v8.3/namelist.atmosphere .
cp ~/MPAS-Model_v8.3/streams.atmosphere .
cp ~/MPAS-Model_v8.3/stream_list.atmosphere.*
cp ~/MPAS-Model_v8.3/src/core_atmosphere/physics/physics_wrf/files/* .
```

## Static file

Now we edit the `init_atmosphere` config files to set up for generating the static file.

Update `namelist.init_atmosphere` with these settings:

| parameter                                       | value                                    |
| ----------------------------------------------- | ---------------------------------------- |
| `nhyd_model.config_init_case`                   | `7` [^init-case7]                        |
| `data_sources.geog_data_path`                   | `'/glade/work/wrfhelp/WPS_GEOG/'` [^gdp] |
| `preproc_stages.config_static_interp`           | `true`                                   |
| `preproc_stages.config_native_gwd_static`       | `true`                                   |
| `preproc_stages.config_native_gwd_gsl_static`   | `false`                                  |
| `preproc_stages.config_vertical_grid`           | `false`                                  |
| `preproc_stages.config_met_interp`              | `false`                                  |
| `preproc_stages.config_input_sst`               | `false`                                  |
| `preproc_stages.config_frac_seaice`             | `false`                                  |
| `decomposition.config_block_decomp_file_prefix` | `'x1.10242.graph.info.part.'`            |

[^init-case7]: Case 7 is the "real-data initialization" case.

[^gdp]: Another geog data path option is `/glade/campaign/mmm/wmr/mpas_tutorial/mpas_static/`.

Then, in `streams.init_atmosphere`, set the input file name template to `x1.10242.grid.nc`,
and the output file name template to `x1.10242.static.nc`.

Create a job script to run the model initialization program.

```{code} bash
:filename: init_real.pbs

#!/usr/bin/env bash
# Based on /glade/campaign/mmm/wmr/mpas_tutorial/job_scripts/init_real.pbs

#
# For more information on submitting jobs to Derecho, see this documentation:
# https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/job-scripts/
#

#--- Give our job a reasonable name
#PBS -N init_real

#--- Run in the main queue
#PBS -q main
#PBS -l job_priority=regular

#--- Set the project under which the job will run
#PBS -A UTAM0025

#--- Specify wallclock limit and resources
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=128:mpiprocs=32:mem=235gb

source ~/mpas-modules-intel.sh

mpiexec ./init_atmosphere_model
```

Submit the job.

```bash
qsub init_real.pbs
```

:::{tip}
:open: false

Get info about your running jobs:

```bash
qstat -u $USER
```

Watch it:

```bash
watch -n1 qstat -u $USER
```

See more:

```bash
qstat -u $USER -f -w
```

:::

## Initial conditions

**20 September 2017, 00 UTC**, the day when Hurricane Maria made landfall in Puerto Rico.

First we need [WPS intermediate files](https://www2.mmm.ucar.edu/wrf/OnLineTutorial/Basics/IM_files/).

The [era5_to_int](https://github.com/NCAR/era5_to_int) tool
can be used to create intermediate files from the NSF NCAR RDA ERA5 netCDF files on GLADE.
But here, to simplify things, we will use an intermediate file that we have already created.

```bash
ln -s /glade/u/home/zmoon/mpas-tutorial/FILE:2017-09-20_00 .
```

:::{tip}
:open: false

You can see what's inside an intermediate file using the `rd_intermediate` tool from WPS.
On Derecho, this tool is available at

```
/glade/u/home/wrfhelp/derecho_pre_compiled_code/wpsv4.5/util/rd_intermediate.exe
```

(and for other WPS versions as well).
:::

Update `namelist.init_atmosphere` with these settings:

| parameter                                       | value                         |
| ----------------------------------------------- | ----------------------------- |
| `nhyd_model.config_init_case`                   | `7`                           |
| `nhyd_model.config_start_time`                  | `'2017-09-20_00:00:00'`       |
| `data_sources.config_met_prefix`                | `'FILE'`                      |
| `preproc_stages.config_static_interp`           | `false`                       |
| `preproc_stages.config_native_gwd_static`       | `false`                       |
| `preproc_stages.config_native_gwd_gsl_static`   | `false`                       |
| `preproc_stages.config_vertical_grid`           | `true`                        |
| `preproc_stages.config_met_interp`              | `true`                        |
| `preproc_stages.config_input_sst`               | `false`                       |
| `preproc_stages.config_frac_seaice`             | `true`                        |
| `decomposition.config_block_decomp_file_prefix` | `'x1.10242.graph.info.part.'` |

Then, in `streams.init_atmosphere`, set the input file name template to `x1.10242.static.nc`
(the static file we just created),
and the output file name template to `x1.10242.init.nc`.

Submit the job.

```bash
qsub init_real.pbs
```

```{note}
For simulations longer than a few days,
you would likely want to also create SST and sea-ice update files.
This uses init case 8, the "surface field initialization" case.
See Section 3.2 in the [official virtual tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/).
```

## Run the model

Update `namelist.atmosphere` with these settings:

| parameter                                       | value                         |
| ----------------------------------------------- | ----------------------------- |
| `nhyd_model.config_dt`                          | `1200.0`                      |
| `nhyd_model.config_start_time`                  | `'2017-09-20_00:00:00'`       |
| `nhyd_model.config_run_duration`                | `'3_00:00:00'`                |
| `nhyd_model.config_radtlw_interval`             | `'01:00:00'`                  |
| `nhyd_model.config_radtsw_interval`             | `'01:00:00'`                  |
| `decomposition.config_block_decomp_file_prefix` | `'x1.10242.graph.info.part.'` |

Then, in `streams.atmosphere`, set the input file name template to `x1.10242.init.nc`
(the initial conditions file we just created).

Create a job script to run the model.

```{code} bash
:filename: run_model.pbs

#!/usr/bin/env bash
# Based on /glade/campaign/mmm/wmr/mpas_tutorial/job_scripts/run_model.pbs

#
# For more information on submitting jobs to Derecho, see this documentation:
# https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/job-scripts/
#

#--- Give our job a reasonable name
#PBS -N run_model

#--- Run in the main queue
#PBS -q main
#PBS -l job_priority=regular

#--- Set the project under which the job will run
#PBS -A UTAM0025

#--- Specify wallclock limit and resources
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=128:mpiprocs=128:mem=235gb

source ~/mpas-modules-intel.sh

mpiexec ./atmosphere_model
```

Submit the job.

```bash
qsub run_model.pbs
```

The main model log is `log.atmosphere.0000.out`.
To follow the updates:

```bash
tail -f log.atmosphere.0000.out
```

A successful run will produce various model output files:

- `diag.*.nc` (mostly 2-d diagnostic fields; specified in `stream_list.atmosphere.diagnostics`)
- `history.*.nc` (2- and 3-d prognostic and diagnostic fields; specified in `stream_list.atmosphere.output`)
- `restart.*.nc` (checkpoints of the model state that we can use for a warm start)

# Regional

We will use the limited-area domain as in:

- https://doi.org/10.1029/2023MS004070
- https://doi.org/10.1029/2024GL112341
- https://doi.org/10.1029/2025MS005146
- https://doi.org/10.22541/essoar.174547944.43729039/v1

created by rotating, moving, and cropping the `x5.8060930` global 15–3-km elliptical refinement mesh.

## Boundary conditions
