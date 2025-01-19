### Imports
import numpy as np
import xarray as xr
from datetime import timedelta
import plotly.express as px
import pandas as pd

### Constants
REL_PATH_AVERAGES = "data/15_days_avg_std.nc"


### Functions
def display_start_end_dates():
    """
    Display the start and end dates of the available data.
    """
    # Load the data
    ds = xr.open_dataset(REL_PATH_AVERAGES)

    # Extract the start and end dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=1
    )  # so as to show the exact period in days
    start_date = pd.to_datetime(pd.to_datetime(ds["time"].values[0]) - delta_left)
    end_date = pd.to_datetime(pd.to_datetime(ds["time"].values[-1]) + delta_right)

    ds.close()

    print(
        f"The time slots of the simulation are from {start_date} (including) to {end_date} (including)."
    )
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
    ds = xr.open_dataset(REL_PATH_AVERAGES)

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=2
    )  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    st_index = np.argmax(
        time_steps - delta_left >= start_date
    )  # inlcude the start date
    end_index = np.argmin(time_steps + delta_right <= end_date)  # include the end date

    # Extract the data and flip the arrays so that the origin is at the bottom left
    # (y axis is inverted later beacuse of the way plotly displays the data)
    avg = (
        np.flip(ds["S_avg"].values[st_index : end_index + 1], axis=1)
        if variable_name == "S"
        else np.flip(ds["T_avg"].values[st_index : end_index + 1], axis=1)
    )
    sd = (
        np.flip(ds["S_sd"].values[st_index : end_index + 1], axis=1)
        if variable_name == "S"
        else np.flip(ds["T_sd"].values[st_index : end_index + 1], axis=1)
    )

    time_steps_update = time_steps[st_index:end_index]
    merged_data = np.stack([avg, sd], axis=1)

    ds.close()

    # Create the figure
    fig = px.imshow(
        merged_data,
        x=ds["xc"].values,
        y=ds["yc"].values,
        facet_col=1,
        animation_frame=0,
        title=("Salinity" if variable_name == "S" else "Temperature")
        + " : 15 days average (in facet_col=0) and standard deviation (in facet_col=1)",
    )

    # Drop animation buttons
    fig["layout"].pop("updatemenus")

    # Modify the colorbar
    fig.update_layout(
        coloraxis=dict(
            cmin=0,
            cmax=np.max(merged_data),
            colorbar=dict(
                title=(
                    "Salinity (g kg<sup>-1</sup>)"
                    if variable_name == "S"
                    else "Temperature (°C)"
                )
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
                f"yaxis{i}": dict(title="yc", autorange="reversed", tickformat=".1f"),
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
    ds = xr.open_dataset(REL_PATH_AVERAGES)

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=2
    )  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    st_index = np.argmax(
        time_steps - delta_left >= start_date
    )  # inlcude the start date
    end_index = np.argmin(time_steps + delta_right <= end_date)  # include the end date

    # Extract the data and flip the arrays so that the origin is at the bottom left
    # (y axis is inverted later beacuse of the way plotly displays the data)
    data = np.flip(ds["exp_pct"].values[st_index : end_index + 1], axis=1)

    time_steps_update = time_steps[st_index:end_index]

    ds.close()

    # Create the figure
    fig = px.imshow(
        data,
        x=ds["xc"].values,
        y=ds["yc"].values,
        animation_frame=0,
        title="Expousure percentage : for each point expousure percentage for 15 days",
        width=800,
        height=500,
    )

    # Drop animation buttons
    fig["layout"].pop("updatemenus")

    # Modify the colorbar
    fig.update_layout(
        coloraxis=dict(
            cmin=0,
            cmax=np.max(data),
            colorbar=dict(title="Expousure (%)"),
        )
    )

    # Modify the layout x and y axis
    fig.update_layout(
        xaxis=dict(title="xc", tickformat=".1f"),
        yaxis=dict(
            title="yc",
            tickformat=".1f",
            autorange="reversed",
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
