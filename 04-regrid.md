---
title: Regrid
subtitle: Tools for regridding MPAS-A output to regular lat-lon grids
---

# pyremap

[pyremap](https://mpas-dev.github.io/pyremap/main/remapper/index.html)
simplifies the process of regridding MPAS data to other grids.
It helps you compute weights (using ESMF or MOAB) and apply them,
and works with global and limited-area meshes.

# Global

For global files, commonly used regridding tools should work
(i.e., they have implemented support for MPAS meshes):

- NCO `ncremap`
- CDO
- TempestRemap

# Limited-area

- Kelly has a tool that allows CDO to work with limited-area meshes.
