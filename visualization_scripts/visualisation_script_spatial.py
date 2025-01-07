### Imports
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

# TD: make timerange dynamic
REL_PATH_VOLUME = "TIMESERIES_VOLUME/DWS.volume.20000101-20001201.nc"
REL_PATH_AGGREGATES_S = "AGGREGATES/DWS200m.aggregates.S.20000101-20001201.nc"
REL_PATH_AGGREGATES_T = "AGGREGATES/DWS200m.aggregates.T.20000101-20001201.nc"


def xaxes_buttons():
    return dict(
        rangeselector=dict(
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
        ),
    )


def plot_volume(path_root):
    ds_volume = xr.open_dataset(path_root + REL_PATH_VOLUME)

    fig = px.line(ds_volume, y="volume", title="Volume in the DWS")

    layout = dict(
        yaxis=dict(title=dict(text="Volume (m<sup>3</sup>)")),
        xaxis=dict(title=dict(text="Date")),
        hovermode="x",
    )

    xaxes_buts = xaxes_buttons()
    xaxes_temp = dict(rangeslider_visible=True)
    xaxes = {**xaxes_buts, **xaxes_temp}

    return (fig, layout, xaxes)


def plot_temperature(path_root):
    ds_temperature = xr.open_dataset(path_root + REL_PATH_AGGREGATES_T)

    T_mean = ds_temperature["T_mean"].values
    T_std = ds_temperature["T_std"].values
    time = ds_temperature["time"].values

    fig = go.Figure(
        [
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
        ]
    )

    layout = dict(
        yaxis=dict(title=dict(text="Temperature (°C)")),
        xaxis=dict(title=dict(text="Date")),
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

    xaxes_buts = xaxes_buttons()
    xaxes_temp = dict(rangeslider_visible=True)
    xaxes = {**xaxes_buts, **xaxes_temp}

    return (fig, layout, xaxes)


def plot_salinity(path_root):
    ds_salinity = xr.open_dataset(path_root + REL_PATH_AGGREGATES_S)

    S_mean = ds_salinity["S_mean"].values
    S_std = ds_salinity["S_std"].values
    time = ds_salinity["time"].values

    fig = go.Figure(
        [
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
        ]
    )

    layout = dict(
        yaxis=dict(title=dict(text="Salinity (g kg<sup>-1</sup>)")),
        xaxis=dict(title=dict(text="Date")),
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

    xaxes_buts = xaxes_buttons()
    xaxes_temp = dict(rangeslider_visible=True)
    xaxes = {**xaxes_buts, **xaxes_temp}

    return (fig, layout, xaxes)


if __name__ == "main":
    print("Error: Should not print when run from notebook")
