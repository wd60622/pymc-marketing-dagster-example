from dagster import (
    Definitions,
    io_manager,
    load_assets_from_modules,
)

from pymc_marketing_dagster_example import assets
from pymc_marketing_dagster_example.io_manager import MMMIOManager, XArrayIOManager

all_assets = load_assets_from_modules([assets])


@io_manager
def mmm_io_manager():
    return MMMIOManager()


@io_manager
def xarray_io_manager():
    return XArrayIOManager()


defs = Definitions(
    assets=all_assets,
    resources={
        "mmm_io_manager": mmm_io_manager,
        "netcdf_io_manager": xarray_io_manager,
    },
)
