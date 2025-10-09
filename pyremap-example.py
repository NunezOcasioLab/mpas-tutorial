from pathlib import Path

import xarray as xr
from pyremap import Remapper, get_lat_lon_descriptor

HERE = Path(__file__).parent

mesh_id = "x1.2562"
src_path = HERE / f"{mesh_id}.grid.nc"
out_dir = HERE
in_path = HERE / f"{mesh_id}.static.nc"
variables = ["ter"]

ds_in = xr.open_dataset(in_path, decode_times=False)

dst = get_lat_lon_descriptor(
    dlon=0.25,
    dlat=0.25,
    lon_min=-125,
    lon_max=-66,
    lat_min=25,
    lat_max=50,
)
# Note that the min/max lon/lat are cell edges, not centers.

for method in ["bilinear", "conserve"]:
    # Create weights with ESMF_RegridWeightGen
    # (It is also possible to use MOAB)
    map_path = out_dir / f"{mesh_id}_map_{method}.nc"
    remapper = Remapper(map_filename=map_path.as_posix(), method=method, ntasks=1, use_tmp=True)
    remapper.src_from_mpas(filename=src_path.as_posix(), mesh_name=mesh_id)
    remapper.dst_descriptor = dst
    remapper.build_map()

    # Apply weights with NCO ncremap, producing a file
    remapper.ncremap(
        in_filename=(HERE / f"{mesh_id}.static.nc").as_posix(),
        out_filename=(out_dir / f"out_{method[:3]}.nc").as_posix(),
        overwrite=True,
        variable_list=variables,
    )

    # Apply weights with numpy, returning an xarray Dataset
    ds = remapper.remap_numpy(ds_in[variables])
    print(ds)
