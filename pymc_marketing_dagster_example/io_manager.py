"""Storage for the MMM object.

Reference
---------
- https://docs.dagster.io/concepts/io-management/io-managers#defining-an-io-manager

"""

import os
from dagster import ConfigurableIOManager, InputContext, OutputContext

import xarray as xr

from pymc_marketing.mmm import MMM


class IOManager(ConfigurableIOManager):
    path_prefix: list[str] = []

    def _get_path(self, context: OutputContext | InputContext) -> str:
        dagster_home = os.getenv("DAGSTER_HOME", "")
        parts = [dagster_home, "storage", *context.asset_key.path]

        if context.has_partition_key:
            parts.append(context.asset_partition_key)

        return "/".join(parts)


class MMMIOManager(IOManager):
    def handle_output(self, context: OutputContext, obj: MMM):
        context.log.info(f"obj: {obj}")
        path: str = self._get_path(context)
        context.log.info(f"Recieved MMM object to save to {path}")
        obj.save(fname=path)
        context.log.info(f"MMM object saved to {path}")

    def load_input(self, context: InputContext):
        context.log.info("Trying to load an MMM object")
        file_path = self._get_path(context)
        context.log.info(f"Loading MMM object from {file_path}")
        return MMM.load(fname=file_path)


class XArrayIOManager(IOManager):
    def handle_output(self, context: OutputContext, obj: xr.Dataset):
        path: str = self._get_path(context)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        context.log.info(f"obj: {obj}")
        obj.to_netcdf(path)

    def load_input(self, context: InputContext):
        return xr.open_dataset(self._get_path(context))
