"""Example based off the README file of pymc-marketing."""

import pandas as pd
import xarray as xr

from dagster import (
    asset,
    TimeWindowPartitionsDefinition,
    AssetExecutionContext,
    AssetIn,
)

from pymc_marketing.mmm import (
    GeometricAdstock,
    LogisticSaturation,
    MMM,
)

# [ins] In [5]: query_marketing_data("2030-01-01")["date_week"].max()
# Out[5]: Timestamp('2021-08-30 00:00:00')
#
# [ins] In [6]: query_marketing_data("2030-01-01")["date_week"].min()
# Out[6]: Timestamp('2018-04-02 00:00:00')
partitions_def = TimeWindowPartitionsDefinition(
    cron_schedule="0 0 1 */3 *",
    start="2020-01",
    end="2021-08",
    fmt="%Y-%m",
)


def query_marketing_data(date: str) -> pd.DataFrame:
    """Query the marketing data."""

    data_url = "https://raw.githubusercontent.com/pymc-labs/pymc-marketing/main/data/mmm_example.csv"
    data = pd.read_csv(data_url, parse_dates=["date_week"])

    return data[data["date_week"] <= date]


@asset(partitions_def=partitions_def)
def marketing_data(context: AssetExecutionContext) -> pd.DataFrame:
    date = context.partition_key
    return query_marketing_data(date)


@asset
def mmm() -> MMM:
    return MMM(
        adstock=GeometricAdstock(l_max=8),
        saturation=LogisticSaturation(),
        date_column="date_week",
        channel_columns=["x1", "x2"],
        control_columns=[
            "event_1",
            "event_2",
            "t",
        ],
        yearly_seasonality=2,
        sampler_config=dict(tune=10, draws=10, chains=2),
    )


@asset(partitions_def=partitions_def, io_manager_key="mmm_io_manager")
def fit_mmm(marketing_data: pd.DataFrame, mmm: MMM):
    columns = mmm.channel_columns + mmm.control_columns + [mmm.date_column]
    X = marketing_data.loc[:, columns]
    y = marketing_data["y"]

    mmm.fit(X, y)
    return mmm


@asset(
    partitions_def=partitions_def,
    io_manager_key="netcdf_io_manager",
    ins={
        "fit_mmm": AssetIn(input_manager_key="mmm_io_manager"),
    },
)
def inference_data(fit_mmm: MMM) -> xr.Dataset:
    return fit_mmm.fit_result
