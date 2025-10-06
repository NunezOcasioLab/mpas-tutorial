# Intro

_MPAS_ stands for Model for Prediction Across Scales.
It is a "collaborative project" for building earth system model components that can be run at multiple scales.
_MPAS-A_ is the atmospheric component of MPAS.
Often, at least in our circles, "MPAS" means the standalone version of MPAS-A.
But it's important to remember that there are other MPAS component models[^a],
and MPAS-A has also been used in larger modeling systems,
e.g. as the atmosphere component[^b]
or as the dynamical core only[^c].

[^a]: including ocean and sea-ice, used [in E3SM](https://docs.e3sm.org/E3SM/MPAS-Ocean/)

[^b]:
    e.g. [MPAS-CMAQ](https://doi.org/10.5194/gmd-17-7855-2024),
    MPAS-Hydro ([in development](https://ral.ucar.edu/news/coming-soon-mpas-hydro)),
    NOAA GSL MPAS for smoke and dust

[^c]:
    e.g. [in CESM](https://sima.ucar.edu/applications/v0/mpas-cesm),
    part of the [StormSPEED](https://sites.google.com/umich.edu/nsf-stormspeed)
    CSEM/CAM [dynamical cores comparison](https://sites.google.com/umich.edu/dcmip-2025/models) project,
    and [planned](https://ufs.epic.noaa.gov/wp-content/uploads/2024/03/Integration-of-MPAS-Dycore-into-UFS.pdf)
    for UFS as an alternative to FV3

## History

https://doi.org/10.1175/MWR-D-10-05056.1
https://doi.org/10.1175/MWR-D-11-00215.1

## Meshes

```{image} https://mpas-dev.github.io/atmosphere/MPAS-var-res_mesh.png
:alt: Global variable-resolution mesh
:width: 300px
```

What makes MPAS special is its use of unstructured Voronoi meshes on the sphere (SCVT),
including C-grid staggering.

Horizontal velocity components are defined normal to the cell edges,
and vertical velocity is defined at cell vertices.

There is a _primal_ mesh (usually mostly hexagons, as above) that most variables are defined on,
and a _dual_ mesh made up of triangles formed by connecting the primal mesh cell centers.
In the [model outputs](https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/appD_fields.html),
vorticity is an example of a dual mesh variable.

## Links

- MPAS project website: <https://mpas-dev.github.io/>
- MPAS-A landing page: <https://www2.mmm.ucar.edu/projects/mpas/site/index.html>
- MPAS mesh spec document: <https://mpas-dev.github.io/files/documents/MPAS-MeshSpec.pdf>
- MPAS-A tech note (in development): <https://www2.mmm.ucar.edu/projects/mpas/mpas_website_linked_files/MPAS-A_tech_note.pdf>
- HTML user guide quick start: <https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/quick_start.html>
- PDF user guide: <https://www2.mmm.ucar.edu/projects/mpas/mpas_atmosphere_users_guide_8.3.0.pdf>
- MPAS official virtual tutorial material: <https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/>
- WRF/MPAS workshop talks: <https://www.mmm.ucar.edu/events/133265/agenda> (2025)
