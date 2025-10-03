---
title: Run
subtitle: Running MPAS on NSF NCAR Derecho
---

# Global

We will use the quasi-uniform 240-km mesh (10242 cells),
as in the [official virtual tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/)
(section 1.3).

First we build out our run directory.

```{code} bash
cd $SCRATCH
mkdir mpas-global-240km
cd $_
ln -s /glade/campaign/mmm/wmr/mpas_tutorial/meshes/x1.10242.grid.nc .
ln -s /glade/campaign/mmm/wmr/mpas_tutorial/meshes/x1.10242.graph.info.part.16 .
cp /glade/campaign/mmm/wmr/mpas_tutorial/job_scripts/init_real.pbs .
```

TODO: above job script is for GNU, gotta update

```bash
qsub init_real.pbs -A UTAM0025
```

:::{tip}

Get info about running jobs.

```bash
qstat -u $USER
```

See more:

```bash
qstat -u $USER -f -w
```

:::

# Regional

We will use the limited-area domain as in:

- https://doi.org/10.1029/2023MS004070
- https://doi.org/10.1029/2024GL112341
- https://doi.org/10.22541/essoar.174547926.68665522/v1
- https://doi.org/10.22541/essoar.174547944.43729039/v1
- https://github.com/knubez/MPAS-Model/tree/isolevels-v8

created by rotating, moving, and cropping the `x5.8060930` global 15--3-km elliptical refinement mesh.

## Creating LBCs
