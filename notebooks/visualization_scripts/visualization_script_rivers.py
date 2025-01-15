#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

COLOUR_PALET = px.colors.qualitative.Dark24
REL_PATH_RIVERS = Path("TIMESERIES_RIVERS/rivers_volume_flux.nc")


def xaxes_buttons():
    return dict(
        buttons=list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    )


def plot_volume_flux(path_root: str | Path):
    # Open the netCDF file
    ds_flux = xr.open_dataset(path_root / REL_PATH_RIVERS)

    # ds_flux_hourly = ds_flux.where(
    #     ((ds_flux["time"].dt.minute == 0) | (ds_flux["time"].dt.minute == 59)), drop=True
    # )
    ds_flux_hourly = ds_flux.where(
        ((ds_flux["time"].dt.minute == 0) | (ds_flux["time"].dt.minute == 59)), drop=True
    ).where(ds_flux["time"].dt.hour % 12 == 0, drop=True)

    nps_flux_hourly = [ds_flux_hourly.sel(station=i)["volume_flux"].values for i in np.arange(12)]
    np_time_hourly = ds_flux_hourly["time"].values
    np_station_names = ds_flux_hourly["station_name"].values

    # Create Figure data
    figures_data = []
    for i, np_flux in enumerate(nps_flux_hourly):

        fig_data_dict = {
            "name": np_station_names[i],
            "legendgroup": i,
            "line": {"color": COLOUR_PALET[i], "dash": "solid"},
            "marker": {"symbol": "circle"},
            "mode": "lines",
            "showlegend": True,
            "hovertemplate": np_station_names[i]
            + "<br>Date = %{x}<br>Volume flux = %{y} m3 s-1<extra></extra>",
            "x": np_time_hourly,
            "xaxis": "x",
            "y": np_flux,
            "yaxis": "y",
        }

        data_tuple = (go.Scattergl(fig_data_dict),)
        figures_data.append(data_tuple)

    data = sum(figures_data, ())

    # Create Figure layout
    layout = dict(
        title="Volume flux into the Dutch wadden sea from selected inlets",
        yaxis=dict(title=dict(text="Volume flux (m<sup>3</sup> s<sup>-1</sup>)")),
        xaxis=dict(
            title=dict(text="Date"),
            rangeselector=xaxes_buttons(),
            rangeslider={"visible": True},
        ),
        hovermode="closest",
        legend={"title": {"text": "Inlet"}, "tracegroupgap": 0},
        margin={"t": 60},
    )

    return go.Figure(data=data, layout=layout)


if __name__ == "main":
    print("Error: Should not print when run from notebook")
