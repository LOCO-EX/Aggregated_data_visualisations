#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import plotly.express as px
import xarray as xr
from plotly.express.colors import qualitative

COLOUR_PALET = qualitative.Dark24
REL_PATH_RIVERS = Path("OUTPUT/rivers_volume_flux.nc")


def xaxes_buttons():
    return dict(
        buttons=list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
            ]
        )
    )


def get_transect_flux(path_root: str, variable: str):
    ds_flux = xr.open_dataset(
        (Path(path_root) / "OUTPUT/TR.volume_salt_flux.nc").resolve()
    )

    fig = px.line(
        x=ds_flux[variable]["time"],
        y=[
            ds_flux[variable].sel(transect=i)
            for i in ds_flux[variable]["transect"].values
        ],
    )

    transect_names = ds_flux["transect_name"].values
    legend_replace = {
        f"wide_variable_{i}": transect_name
        for i, transect_name in enumerate(transect_names)
    }

    fig.for_each_trace(
        lambda t: t.update(
            name=legend_replace[t.name],
            legendgroup=legend_replace[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, legend_replace[t.name]),
        )
    )

    ds_flux.close()

    return fig


def plot_transects_volume_flux(path_root: str):
    fig = get_transect_flux(path_root, "volume_flux")

    layout = dict(
        title="Volume flux in the DWS",
        yaxis=dict(title=dict(text="Volume flux (m<sup>3</sup>s<sup>-1</sup>)")),
        xaxis=dict(title=dict(text="Date"), rangeselector=xaxes_buttons()),
        hovermode="x",
        legend_title_text="Transect",
    )

    fig.update_layout(layout)

    return fig


def plot_transects_salinity_flux(path_root: str):

    fig = get_transect_flux(path_root, "salinity_flux")

    layout = dict(
        title="Salinity flux in the DWS",
        yaxis=dict(
            title=dict(
                text="Salinity flux (10<sup>-3</sup> m<sup>3</sup>s<sup>-1</sup>)"
            )
        ),
        xaxis=dict(title=dict(text="Date"), rangeselector=xaxes_buttons()),
        hovermode="x",
        legend_title_text="Transect",
    )

    fig.update_layout(layout)

    return fig


if __name__ == "main":
    print("Error: Should not print when run from notebook")
