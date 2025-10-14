---
title: Build
subtitle: Building MPAS on NSF NCAR Derecho
label: page:build
---

First we need to clone the model repository.
We will use Kelly's fork, which adds additional vertical levels (based on ERA5)
and isobaric diagnostics.

```{code} bash
cd $HOME
git clone https://github.com/knubez/MPAS-Model.git MPAS-Model_v8.3
cd $_
git switch isolevels-v8
```

(p:interactive-job)=

It's good practice to compile the model in an interactive job,
to avoid stressing the login nodes, which are a shared resource,
_and_ to ensure that the CPU resources detected at build time are the same as those used at run time[^derecho-nodes].

[^derecho-nodes]:
    On Derecho, the login nodes have the
    [same processors](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/derecho/#derecho-hardware)
    as the compute nodes, but this is not always the case on other systems.

```bash
qsub -I -l walltime=3600 -l select=1:ncpus=4:mem=80gb -A UTAM0025 -q develop
```

```{tip}
:open: false

NCAR also [provides](https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/)
`qcmd` and `qinteractive` shortcut commands that you can use,
but the above `qsub` should work on other PBS-based systems as well.

The [`develop` queue](https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/charging/#derecho-queues)
has a 6-hour walltime limit and is intended for testing and development.
Above we have requested 3600 seconds (1 hour).
```

After our session starts, we need to load some modules.

::::{tab-set}

:::{tab-item} Intel 2023

```{code} bash
:filename: modules-intel-2023.sh
:caption: These are the modules we've used for the referenced papers.

# NCAR Derecho modules for MPAS-A
# `source` or `.` this file to use

module --force purge
module load ncarenv/23.06
module load intel/2023.0.0
module load cray-mpich/8.1.25
module load parallel-netcdf/1.12.3

# Hack to get pnetcdf working again
export LD_LIBRARY_PATH="/glade/u/apps/derecho/23.06/spack/opt/spack/parallel-netcdf/1.12.3/cray-mpich/8.1.25/oneapi/2023.0.0/blyr/lib:$LD_LIBRARY_PATH"
```

:::

:::{tab-item} Intel 2025

```{code} bash
:filename: modules-intel-2025.sh
:caption: Updated modules, using `ifx` instead of `ifort`.

# NCAR Derecho modules for MPAS-A
# `source` or `.` this file to use

module --force purge
module load ncarenv/24.12
module load intel/2025.1.0
module load cray-mpich/8.1.29
module load parallel-netcdf/1.14.0

# Hack to get pnetcdf working again
export LD_LIBRARY_PATH="/glade/u/apps/derecho/24.12/spack/opt/spack/parallel-netcdf/1.14.0/cray-mpich/8.1.29/oneapi/2025.1.0/vrc7/lib:$LD_LIBRARY_PATH"

# Tell mpifort to use ifx
export MPICH_FC=ifx
```

:::

::::

Select one of the above module sets and save it to a file:
`~/mpas-modules-intel.sh`.
Then, load the modules.

```bash
source ~/mpas-modules-intel.sh
```

Run `module list` to verify that the correct modules are loaded.

First we build the model initialization program.
This is what we use to generate initial conditions and such.

```bash
make -j4 intel CORE=init_atmosphere
```

Now, assuming the `init_atmosphere_model` executable was built successfully,
we can build the main program.

```bash
make -j4 intel CORE=atmosphere
```

If this completes successfully, we should have an `atmosphere_model` executable
(and `build_tables`)
and we can leave our interactive job.

```bash
exit
```
