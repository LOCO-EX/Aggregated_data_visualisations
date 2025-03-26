#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import plotly.graph_objects as go
import xarray as xr
from plotly_resampler import FigureResampler

REL_PATH_VOLUME = Path("output_files/DWS.volume.nc")
REL_PATH_AGGREGATES_S = Path("output_files/DWS200m.spatial_aggregates.S.nc")
REL_PATH_AGGREGATES_T = Path("output_files/DWS200m.spatial_aggregates.T.nc")


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


def plot_volume(path_root: str | Path):
    ds_volume = xr.open_dataset(path_root / REL_PATH_VOLUME)

    fig = FigureResampler(go.Figure())
    fig.add_trace(
        go.Scattergl(y=ds_volume["volume"].values, x=ds_volume["time"].values)
    )

    layout = dict(
        title="Volume in the DWS",
        yaxis=dict(title=dict(text="Volume (m<sup>3</sup>)")),
        xaxis=dict(
            title=dict(text="Date"),
            rangeselector=xaxes_buttons(),
        ),
        hovermode="x",
    )
    fig.update_layout(layout)

    return fig


def get_fig_spatial(var_name: str, path: Path):
    ds_aggregate = xr.open_dataset(path)

    if var_name == "salinity":
        var_mean = ds_aggregate["S_mean"].values
        var_std = ds_aggregate["S_std"].values
    elif var_name == "temperature":
        var_mean = ds_aggregate["T_mean"].values
        var_std = ds_aggregate["T_std"].values
    else:
        print("Error")
        quit()

    time = ds_aggregate["time"].values

    layout = dict(
        xaxis=dict(
            title=dict(text="Date"),
            rangeslider_visible=True,
            rangeselector=xaxes_buttons(),
        ),
        hovermode="x",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list(
                    [
                        dict(
                            method="restyle",
                            label="Toggle uncertainty",
                            visible=True,
                            args=[{"visible": True}, [1, 2]],
                            args2=[{"visible": "legendonly"}, [1, 2]],
                        ),
                    ]
                ),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=1.08,
                xanchor="center",
                y=0.6,
                yanchor="middle",
            ),
        ],
    )

    fig = go.Figure(
        data=[
            go.Scatter(
                name=f"Average {var_name}",
                x=time,
                y=var_mean,
                mode="lines",
                line=dict(color="rgb(31, 119, 180)"),
            ),
            go.Scatter(
                name="Upper Bound",
                x=time,
                y=var_mean + var_std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Lower Bound",
                x=time,
                y=var_mean - var_std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
                showlegend=False,
            ),
        ],
        layout=layout,
    )

    return fig


def plot_temperature(path_root: str | Path):
    var_name = "temperature"

    fig = get_fig_spatial(var_name, (path_root / REL_PATH_AGGREGATES_T).resolve())
    fig.update_layout({"yaxis": dict(title=dict(text="Temperature (°C)"))})

    return fig


def plot_salinity(path_root: str | Path):
    var_name = "salinity"

    fig = get_fig_spatial(var_name, (path_root / REL_PATH_AGGREGATES_S).resolve())
    fig.update_layout({"yaxis": dict(title=dict(text="Salinity (g kg<sup>-1</sup>)"))})

    return fig


if __name__ == "main":
    print("Error: Should not print when run from notebook")
