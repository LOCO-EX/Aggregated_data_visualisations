### Imports
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

### Global variables
BOUNDARIES_DWS = "data/dws_boundaries_contour0.nc"
DATA = "https://opendap.4tu.nl/thredds/dodsC/data2/test/spatial/15_days_avg_std.nc"  # change for your folder with data if run locally
URL_DATA = "https://opendap.4tu.nl/thredds/catalog/data2/test/spatial/catalog.html"
LOCAL = False


### Functions
def read_data_from_opendap_test():
    """
    Read the data from the opendap server.
    """
    # Load the data
    ds = xr.open_dataset(DATA, engine="netcdf4")
    print(f"File from {URL_DATA} opened successfully.")
    print(ds)
    ds.close()


def display_start_end_dates():
    """
    Display the start and end dates of the available data.
    """
    # Load the data
    ds = xr.open_dataset(DATA, engine="netcdf4")

    # Extract the start and end dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(hours=1)  # so as to show the exact period in days
    start_date = pd.to_datetime(pd.to_datetime(ds["time"].values[0]) - delta_left)
    end_date = pd.to_datetime(pd.to_datetime(ds["time"].values[-1]) + delta_right)

    ds.close()

    print(f"The time slots of the simulation are from {start_date} (including) to {end_date} (including).")
    print("Please choose a time period within these dates.")


def display_variable(start_date, end_date, variable_name):
    """
    Display the 15 days average and standard deviation of the chosen variable in the chosen time period.
    The data is displayed in a plotly figure with a slider to navigate through the time steps.

    Parameters:
    start_date : datetime
        The start date of the time period to display.
    end_date : datetime
        The end date of the time period to display.
    variable_name : str
        The name of the variable to display. It should be one of 'S' (salinity) or 'T' (temperature).
    """
    # Load the data
    ds = xr.open_dataset(DATA, engine="netcdf4")
    if LOCAL:
        bound = xr.open_dataset(BOUNDARIES_DWS)

        # Extract boundary points
        boundary_points = bound.bdr_dws.values
        bound.close()

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(hours=1)  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    mask_ind = (time_steps - delta_left >= start_date) & (time_steps + delta_right <= end_date)

    # Extract the data and flip the arrays so that the origin is at the bottom left
    # (y axis is inverted later beacuse of the way plotly displays the data)
    avg = ds["S_avg"].values[mask_ind] if variable_name == "S" else ds["T_avg"].values[mask_ind]
    sd = ds["S_sd"].values[mask_ind] if variable_name == "S" else ds["T_sd"].values[mask_ind]
    # Add border to avg and sd respectively

    time_steps_update = time_steps[mask_ind]
    merged_data = np.stack([avg, sd], axis=1)

    ds.close()

    # Create the figure
    fig = px.imshow(
        merged_data,
        x=ds["xc"].values,
        y=ds["yc"].values,
        facet_col=1,
        animation_frame=0,
        origin="lower",
        title=("Salinity" if variable_name == "S" else "Temperature")
        + " : 15 days average (in facet_col=0) and standard deviation (in facet_col=1)",
    )

    if LOCAL:
        # Add boundary to the first facet
        fig.add_trace(
            go.Scatter(
                x=boundary_points[:, 0],
                y=boundary_points[:, 1],
                mode="lines",
                line=dict(color="black", width=2),
                name="",
                showlegend=False,
            ),
            row=1,  # First facet
            col=1,
        )

        # Add boundary to the second facet
        fig.add_trace(
            go.Scatter(
                x=boundary_points[:, 0],
                y=boundary_points[:, 1],
                mode="lines",
                line=dict(color="black", width=2),
                name="",
                showlegend=False,
            ),
            row=1,  # Second facet
            col=2,
        )

    # Drop animation buttons
    fig["layout"].pop("updatemenus")

    # Modify the colorbar
    fig.update_layout(
        coloraxis=dict(
            cmin=0,
            cmax=int(np.nanmax(merged_data)) + 1,
            colorbar=dict(
                title=("Salinity (g kg<sup>-1</sup>)" if variable_name == "S" else "Temperature (°C)"),
            ),
        )
    )

    # Modify the layout x and y axis
    for i in range(1, merged_data.shape[1]):
        fig.update_layout(
            **{
                f"xaxis{i}": dict(title="xc", tickformat=".1f"),
            },
            **{
                f"yaxis{i}": dict(title="yc", tickformat=".1f"),
            },
        )

    # Add slider
    fig.update_layout(
        sliders=[
            {
                "currentvalue": {
                    "prefix": "15 days time slot: ",
                    "visible": True,
                    "xanchor": "center",
                },
                "len": 0.9,
                "steps": [
                    {
                        "label": f'{(time_steps_update[i]-delta_left).strftime("%d/%m/%Y") }-{(time_steps_update[i]+delta_right).strftime("%d/%m/%Y") }',
                        "method": "animate",
                        "args": [[i], {"frame": {"duration": 500, "redraw": True}}],
                    }
                    for i in range(len(time_steps_update))
                ],
            }
        ],
    )

    fig.show()


def display_expousure(start_date, end_date):
    """
    Display the expousure for 15 days in the chosen time period.
    The data is displayed in a plotly figure with a slider to navigate through the time steps.

    Parameters:
    start_date : datetime
        The start date of the time period to display.
    end_date : datetime
        The end date of the time period to display.
    """
    # Load the data
    ds = xr.open_dataset(DATA, engine="netcdf4")
    if LOCAL:
        bound = xr.open_dataset(BOUNDARIES_DWS)

        # Extract boundary points
        boundary_points = np.flip(bound.bdr_dws.values, axis=0)
        bound.close()

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(hours=1)  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    mask_ind = (time_steps - delta_left >= start_date) & (time_steps + delta_right <= end_date)

    # Extract the data and flip the arrays so that the origin is at the bottom left
    # (y axis is inverted later beacuse of the way plotly displays the data)
    data = ds["exp_pct"].values[mask_ind]

    time_steps_update = time_steps[mask_ind]

    ds.close()

    # Create the figure
    fig = px.imshow(
        data,
        x=ds["xc"].values,
        y=ds["yc"].values,
        animation_frame=0,
        origin="lower",
        title="Expousure percentage : for each point expousure percentage for 15 days",
        width=800,
        height=500,
    )

    if LOCAL:
        # Add boundary to the facet
        fig.add_trace(
            go.Scatter(
                x=boundary_points[:, 0],
                y=boundary_points[:, 1],
                mode="lines",
                line=dict(color="black", width=2),
                name="",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    # Drop animation buttons
    fig["layout"].pop("updatemenus")

    # Modify the colorbar
    fig.update_layout(
        coloraxis=dict(
            cmin=0,
            cmax=int(np.nanmax(data)) + 1,
            colorbar=dict(title="Expousure (%)"),
        )
    )

    # Modify the layout x and y axis
    fig.update_layout(
        xaxis=dict(title="xc", tickformat=".1f"),
        yaxis=dict(
            title="yc",
            tickformat=".1f",
        ),
    )

    # Add slider
    fig.update_layout(
        sliders=[
            {
                "currentvalue": {
                    "prefix": "15 days time slot: ",
                    "visible": True,
                    "xanchor": "center",
                },
                "len": 0.9,
                "steps": [
                    {
                        "label": f'{(time_steps_update[i]-delta_left).strftime("%d/%m/%Y") }-{(time_steps_update[i]+delta_right).strftime("%d/%m/%Y") }',
                        "method": "animate",
                        "args": [[i], {"frame": {"duration": 500, "redraw": True}}],
                    }
                    for i in range(len(time_steps_update))
                ],
            }
        ],
    )

    fig.show()


if __name__ == "main":
    print("Error: Should not print when run from notebook")
