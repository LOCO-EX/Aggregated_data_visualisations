#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import plotly.graph_objects as go
import xarray as xr
from plotly_resampler import FigureResampler

REL_PATH_VOLUME = Path("TIMESERIES_VOLUME/DWS.volume.20000101-20001201.nc")
REL_PATH_AGGREGATES_S = Path("AGGREGATES/DWS200m.aggregates.S.20000101-20001201.nc")
REL_PATH_AGGREGATES_T = Path("AGGREGATES/DWS200m.aggregates.T.20000101-20001201.nc")


def xaxes_buttons():
    return dict(
        buttons=list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                # dict(step="all"),  # Doesn't work with resampler
            ]
        )
    )


def plot_volume(path_root: str | Path):
    ds_volume = xr.open_dataset(path_root / REL_PATH_VOLUME)

    fig = FigureResampler(go.Figure())
    fig.add_trace(go.Scattergl(y=ds_volume["volume"].values, x=ds_volume["time"].values))

    layout = dict(
        title="Volume in the DWS",
        yaxis=dict(title=dict(text="Volume (m<sup>3</sup>)")),
        xaxis=dict(title=dict(text="Date"), rangeslider_visible=True, rangeselector=xaxes_buttons()),
        hovermode="x",
    )
    fig.update_layout(layout)

    return fig


def plot_temperature(path_root: str | Path):
    ds_temperature = xr.open_dataset(path_root / REL_PATH_AGGREGATES_T)

    T_mean = ds_temperature["T_mean"].values
    T_std = ds_temperature["T_std"].values
    time = ds_temperature["time"].values

    layout = dict(
        yaxis=dict(title=dict(text="Temperature (°C)")),
        xaxis=dict(title=dict(text="Date"), rangeslider_visible=True, rangeselector=xaxes_buttons()),
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
                name="Average temperature",
                x=time,
                y=T_mean,
                mode="lines",
                line=dict(color="rgb(31, 119, 180)"),
            ),
            go.Scatter(
                name="Upper Bound",
                x=time,
                y=T_mean + T_std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Lower Bound",
                x=time,
                y=T_mean - T_std,
                marker=dict(color="#444"),
                line=dict(width=0),
                mode="lines",
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
                showlegend=False,
            ),
        ],
        layout=layout,
    )

    return fig


def plot_salinity(path_root: str | Path):
    ds_salinity = xr.open_dataset(path_root / REL_PATH_AGGREGATES_S)

    S_mean = ds_salinity["S_mean"].values
    S_std = ds_salinity["S_std"].values
    time = ds_salinity["time"].values

    layout = dict(
        yaxis=dict(title=dict(text="Salinity (g kg<sup>-1</sup>)")),
        xaxis=dict(title=dict(text="Date"), rangeslider_visible=True, rangeselector=xaxes_buttons()),
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
                name="Average salinity",
                x=time,
                y=S_mean,
                mode="lines",
                line=dict(color="rgb(31, 119, 180)"),
            ),
            go.Scatter(
                name="Upper Bound",
                x=time,
                y=S_mean + S_std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Lower Bound",
                x=time,
                y=S_mean - S_std,
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


if __name__ == "main":
    print("Error: Should not print when run from notebook")
