### Imports
from datetime import timedelta

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr
from pyproj import Transformer

### Global variables
REL_PATH_BOUNDARIES_DWS = "OUTPUT//DWS200m.boundary_area.nc"
REL_PATH = (
    "OUTPUT//15day.aggregates.rt.nc"  # change for your folder with data if run locally
)


def display_start_end_dates(path_root: str | Path):
    """
    Display the start and end dates of the available data.
    """
    # Load the data
    ds = xr.open_dataset(path_root + REL_PATH, engine="netcdf4")

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


def display_variable(start_date, end_date, variable_name, path_root: str | Path):
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
    ds = xr.open_dataset(path_root + REL_PATH, engine="netcdf4")
    dws_b = xr.open_dataset(path_root + REL_PATH_BOUNDARIES_DWS)

    # Extract boundary points
    boundary_points = dws_b.bdr_dws.values

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=1
    )  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    mask_ind = (time_steps - delta_left >= start_date) & (
        time_steps + delta_right <= end_date
    )
    time_steps_update = time_steps[mask_ind]

    # Extract the data
    avg = (
        ds["S_avg"].values[mask_ind]
        if variable_name == "S"
        else ds["T_avg"].values[mask_ind]
    )
    sd = (
        ds["S_sd"].values[mask_ind]
        if variable_name == "S"
        else ds["T_sd"].values[mask_ind]
    )
    ## start - this part of code is the same for three functions
    #### rotations of x and y coordinates
    # from epgs:4326(LatLon with WGS84) to epgs:28992(DWS)
    inproj = Transformer.from_crs("epsg:4326", "epsg:28992", always_xy=True)
    xct = dws_b.lonc.values
    yct = dws_b.latc.values  # lon,lat units #to change later for reading from dws_b
    xctp, yctp, z = inproj.transform(xct, yct, xct * 0.0)
    xctp = (xctp) / 1e2
    yctp = (yctp) / 1e2
    # first projected point to correct the coordinates of model local meter units
    xctp0 = xctp[0, 0]
    yctp0 = yctp[0, 0]

    # matrix rotation -17degrees-----
    ang = -17 * np.pi / 180
    angs = np.ones((2, 2))
    angs[0, 0] = np.cos(ang)
    angs[0, 1] = np.sin(ang)
    angs[1, 0] = -np.sin(ang)
    angs[1, 1] = np.cos(ang)

    # original topo points in meter
    xct2, yct2 = np.meshgrid(dws_b.xc.values, dws_b.yc.values)
    xy = np.array([xct2.flatten(), yct2.flatten()]).T
    # rotate
    xyp = np.matmul(angs, xy.T).T / 1e2
    xyp0 = xyp[0, :]  # the first point in the bathy data in local meter units=0,0

    # rotate DWS area
    values = dws_b.mask_dws.values
    xc = dws_b.xc
    yc = dws_b.yc
    y_idx, x_idx = np.where(values)  # True values
    x_true = xc[x_idx]
    y_true = yc[y_idx]
    points = np.column_stack((x_true, y_true))

    # rotate values
    points_rot = np.matmul(angs, points.T).T / 1e2
    points_rot = points_rot - xyp0
    points_rot[:, 0] = points_rot[:, 0] + xctp0
    points_rot[:, 1] = points_rot[:, 1] + yctp0

    ##### rotate contour of DWS data
    # contour of DWS------
    bdr_dws0p = np.full((boundary_points.shape[0], 2), np.nan)
    # rotate
    bdr_dws0p = np.matmul(angs, boundary_points.T).T / 1e2
    # correct model units:
    # 1)substact the first model local point of the topo file, but give tha same as xyp0=[0,0]
    # 2)use the first projected point of the case (lon,lat model units to meter)
    bdr_dws0p = bdr_dws0p - xyp0
    bdr_dws0p[:, 0] = bdr_dws0p[:, 0] + xctp0 - 1000
    bdr_dws0p[:, 1] = bdr_dws0p[:, 1] + yctp0 - 5400

    ##### rotate bathymetry data
    # Land area
    values_ = ds.h.values
    y_idx_, x_idx_ = np.where(np.isnan(values_))
    x_true_ = xc[x_idx_]
    y_true_ = yc[y_idx_]
    points_ = np.column_stack((x_true_, y_true_))

    # rotate values
    points_rot_ = np.matmul(angs, points_.T).T / 1e2
    points_rot_ = points_rot_ - xyp0
    points_rot_[:, 0] = points_rot_[:, 0] + xctp0
    points_rot_[:, 1] = points_rot_[:, 1] + yctp0
    data_h = np.full((6400, 6400), np.nan)

    for idx in range(0, len(x_idx_)):
        data_h[
            int(points_rot_[idx][1]) - 1 : int(points_rot_[idx][1]) + 2,
            int(points_rot_[idx][0]) - 1 : int(points_rot_[idx][0]) + 2,
        ] = 1

    data_h = data_h[5400:6200, 1000:2200]
    data_h[0:300, 280:1200] = 1  # add land area
    ## end of - this part of code is the same for three functions

    ##### rotations of data
    avg_data_ = np.full((avg.shape[0], 6400, 6400), np.nan)

    for idx0 in range(0, avg.shape[0]):
        for idx in range(0, len(x_idx)):
            avg_data_[
                idx0,
                int(points_rot[idx][1]) - 1 : int(points_rot[idx][1]) + 2,
                int(points_rot[idx][0]) - 1 : int(points_rot[idx][0]) + 2,
            ] = avg[idx0, y_idx[idx], x_idx[idx]]

    avg_data_ = avg_data_[:, 5400:6200, 1000:2200]

    sd_data_ = np.full((sd.shape[0], 6400, 6400), np.nan)

    for idx0 in range(0, sd.shape[0]):
        for idx in range(0, len(x_idx)):
            sd_data_[
                idx0,
                int(points_rot[idx][1]) - 1 : int(points_rot[idx][1]) + 2,
                int(points_rot[idx][0]) - 1 : int(points_rot[idx][0]) + 2,
            ] = sd[idx0, y_idx[idx], x_idx[idx]]

    sd_data_ = sd_data_[:, 5400:6200, 1000:2200]

    # Replace DWS area with nan
    data_h[~np.isnan(avg_data_[0])] = np.nan

    merged_data = np.stack([avg_data_, sd_data_], axis=1)

    ds.close()
    dws_b.close()

    yticks = np.arange(0, 800)
    xticks = np.arange(0, 1200)

    # Create the figure
    fig = px.imshow(
        merged_data,
        x=xticks,
        y=yticks,
        facet_col=1,
        animation_frame=0,
        origin="lower",
        title=("Salinity" if variable_name == "S" else "Temperature")
        + " : 15 days average (in facet_col=0) and standard deviation (in facet_col=1)",
    )

    # Add boundary to the first facet
    fig.add_trace(
        go.Scatter(
            x=bdr_dws0p[:, 0],
            y=bdr_dws0p[:, 1],
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
            x=bdr_dws0p[:, 0],
            y=bdr_dws0p[:, 1],
            mode="lines",
            line=dict(color="black", width=2),
            name="",
            showlegend=False,
        ),
        row=1,  # Second facet
        col=2,
    )
    fig.add_trace(
        go.Heatmap(z=data_h, colorscale=[[0, "white"], [1, "gray"]], showscale=False),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(z=data_h, colorscale=[[0, "white"], [1, "gray"]], showscale=False),
        row=1,
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
                title=(
                    "Salinity (g kg<sup>-1</sup>)"
                    if variable_name == "S"
                    else "Temperature (°C)"
                ),
            ),
        )
    )

    # Modify the layout x and y axis
    for i in range(1, merged_data.shape[1] + 1):
        fig.update_layout(
            **{
                f"xaxis{i}": dict(
                    title="Easting (km)",
                    tickvals=[0, 200, 400, 600, 800, 1000, 1200],  # Locations of ticks
                    ticktext=[0, 20, 40, 60, 80, 100, 120],
                ),
            },
            **{
                f"yaxis{i}": dict(
                    title="Northing (km)",
                    tickvals=[0, 200, 400, 600, 800],  # Locations of ticks
                    ticktext=[0, 20, 40, 60, 80],
                ),
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


def display_exposure(start_date, end_date, path_root: str | Path):
    """
    Display the exposure for 15 days in the chosen time period.
    The data is displayed in a plotly figure with a slider to navigate through the time steps.

    Parameters:
    start_date : datetime
        The start date of the time period to display.
    end_date : datetime
        The end date of the time period to display.
    """
    # Load the data
    ds = xr.open_dataset(path_root + REL_PATH, engine="netcdf4")
    dws_b = xr.open_dataset(path_root + REL_PATH_BOUNDARIES_DWS)

    # Extract boundary points
    boundary_points = np.flip(dws_b.bdr_dws.values, axis=0)

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=1
    )  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    mask_ind = (time_steps - delta_left >= start_date) & (
        time_steps + delta_right <= end_date
    )
    time_steps_update = time_steps[mask_ind]

    # Extract the data
    data = ds["exp_pct"].values[mask_ind]

    ## start - this part of code is the same for three functions
    #### rotations of x and y coordinates
    # from epgs:4326(LatLon with WGS84) to epgs:28992(DWS)
    inproj = Transformer.from_crs("epsg:4326", "epsg:28992", always_xy=True)
    xct = dws_b.lonc.values
    yct = dws_b.latc.values  # lon,lat units #to change later for reading from dws_b
    xctp, yctp, z = inproj.transform(xct, yct, xct * 0.0)
    xctp = (xctp) / 1e2
    yctp = (yctp) / 1e2
    # first projected point to correct the coordinates of model local meter units
    xctp0 = xctp[0, 0]
    yctp0 = yctp[0, 0]

    # matrix rotation -17degrees-----
    ang = -17 * np.pi / 180
    angs = np.ones((2, 2))
    angs[0, 0] = np.cos(ang)
    angs[0, 1] = np.sin(ang)
    angs[1, 0] = -np.sin(ang)
    angs[1, 1] = np.cos(ang)

    # original topo points in meter
    xct2, yct2 = np.meshgrid(dws_b.xc.values, dws_b.yc.values)
    xy = np.array([xct2.flatten(), yct2.flatten()]).T
    # rotate
    xyp = np.matmul(angs, xy.T).T / 1e2
    xyp0 = xyp[0, :]  # the first point in the bathy data in local meter units=0,0

    # rotate DWS area
    values = dws_b.mask_dws.values
    xc = dws_b.xc
    yc = dws_b.yc
    y_idx, x_idx = np.where(values)  # True values
    x_true = xc[x_idx]
    y_true = yc[y_idx]
    points = np.column_stack((x_true, y_true))

    # rotate values
    points_rot = np.matmul(angs, points.T).T / 1e2
    points_rot = points_rot - xyp0
    points_rot[:, 0] = points_rot[:, 0] + xctp0
    points_rot[:, 1] = points_rot[:, 1] + yctp0

    ##### rotate contour of DWS data
    # contour of DWS------
    bdr_dws0p = np.full((boundary_points.shape[0], 2), np.nan)
    # rotate
    bdr_dws0p = np.matmul(angs, boundary_points.T).T / 1e2
    # correct model units:
    # 1)substact the first model local point of the topo file, but give tha same as xyp0=[0,0]
    # 2)use the first projected point of the case (lon,lat model units to meter)
    bdr_dws0p = bdr_dws0p - xyp0
    bdr_dws0p[:, 0] = bdr_dws0p[:, 0] + xctp0 - 1000
    bdr_dws0p[:, 1] = bdr_dws0p[:, 1] + yctp0 - 5400

    ##### rotate bathymetry data
    # Land area
    values_ = ds.h.values
    y_idx_, x_idx_ = np.where(np.isnan(values_))
    x_true_ = xc[x_idx_]
    y_true_ = yc[y_idx_]
    points_ = np.column_stack((x_true_, y_true_))

    # rotate values
    points_rot_ = np.matmul(angs, points_.T).T / 1e2
    points_rot_ = points_rot_ - xyp0
    points_rot_[:, 0] = points_rot_[:, 0] + xctp0
    points_rot_[:, 1] = points_rot_[:, 1] + yctp0
    data_h = np.full((6400, 6400), np.nan)

    for idx in range(0, len(x_idx_)):
        data_h[
            int(points_rot_[idx][1]) - 1 : int(points_rot_[idx][1]) + 2,
            int(points_rot_[idx][0]) - 1 : int(points_rot_[idx][0]) + 2,
        ] = 1

    data_h = data_h[5400:6200, 1000:2200]
    data_h[0:300, 280:1200] = 1  # add land area
    ## end of - this part of code is the same for three functions

    ##### rotations of data
    data_ = np.full((data.shape[0], 6400, 6400), np.nan)

    for idx0 in range(0, data.shape[0]):
        for idx in range(0, len(x_idx)):
            data_[
                idx0,
                int(points_rot[idx][1]) - 1 : int(points_rot[idx][1]) + 2,
                int(points_rot[idx][0]) - 1 : int(points_rot[idx][0]) + 2,
            ] = data[idx0, y_idx[idx], x_idx[idx]]

    data_ = data_[:, 5400:6200, 1000:2200]

    # Replace DWS area with nan
    data_h[~np.isnan(data_[0])] = np.nan

    # Close the datasets
    ds.close()
    dws_b.close()

    yticks = np.arange(0, 800)
    xticks = np.arange(0, 1200)

    # Create the figure
    fig = px.imshow(
        data_,
        x=xticks,
        y=yticks,
        animation_frame=0,
        origin="lower",
        title="Exposure rate : exposure rate for 15 days",
        width=800,
        height=500,
    )

    # Add boundary to the facet
    fig.add_trace(
        go.Scatter(
            x=bdr_dws0p[:, 0],
            y=bdr_dws0p[:, 1],
            mode="lines",
            line=dict(color="black", width=2),
            name="",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(z=data_h, colorscale=[[0, "white"], [1, "gray"]], showscale=False),
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
            colorbar=dict(title="Exposure (%)"),
        )
    )

    # Modify the layout x and y axis
    fig.update_layout(
        xaxis=dict(
            title="Easting (km)",
            tickvals=[0, 200, 400, 600, 800, 1000, 1200],  # Locations of ticks
            ticktext=[0, 20, 40, 60, 80, 100, 120],
        ),
        yaxis=dict(
            title="Northing (km)",
            tickvals=[0, 200, 400, 600, 800],  # Locations of ticks
            ticktext=[0, 20, 40, 60, 80],
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


def display_rt(start_date, end_date, path_root: str | Path):
    """
    Display the resisende time for 15 days in the chosen time period.
    The data is displayed in a plotly figure with a slider to navigate through the time steps.

    Parameters:
    start_date : datetime
        The start date of the time period to display.
    end_date : datetime
        The end date of the time period to display.
    """
    # Load the data
    ds = xr.open_dataset(path_root + REL_PATH, engine="netcdf4")
    dws_b = xr.open_dataset(path_root + REL_PATH_BOUNDARIES_DWS)

    # Extract boundary points
    boundary_points = np.flip(dws_b.bdr_dws.values, axis=0)

    # Find the indices of the time steps that correspond to the chosen dates
    delta_left = timedelta(days=7.5)
    delta_right = timedelta(days=7.5) - timedelta(
        hours=1
    )  # so as to show the exact period
    time_steps = ds["time"].values
    time_steps = pd.to_datetime(time_steps)
    mask_ind = (time_steps - delta_left >= start_date) & (
        time_steps + delta_right <= end_date
    )
    time_steps_update = time_steps[mask_ind]

    # Extract the data
    data = ds["Rt_mean"].values[mask_ind]

    ## start - this part of code is the same for three functions
    #### rotations of x and y coordinates
    # from epgs:4326(LatLon with WGS84) to epgs:28992(DWS)
    inproj = Transformer.from_crs("epsg:4326", "epsg:28992", always_xy=True)
    xct = dws_b.lonc.values
    yct = dws_b.latc.values  # lon,lat units #to change later for reading from dws_b
    xctp, yctp, z = inproj.transform(xct, yct, xct * 0.0)
    xctp = (xctp) / 1e2
    yctp = (yctp) / 1e2
    # first projected point to correct the coordinates of model local meter units
    xctp0 = xctp[0, 0]
    yctp0 = yctp[0, 0]

    # matrix rotation -17degrees-----
    ang = -17 * np.pi / 180
    angs = np.ones((2, 2))
    angs[0, 0] = np.cos(ang)
    angs[0, 1] = np.sin(ang)
    angs[1, 0] = -np.sin(ang)
    angs[1, 1] = np.cos(ang)

    # original topo points in meter
    xct2, yct2 = np.meshgrid(dws_b.xc.values, dws_b.yc.values)
    xy = np.array([xct2.flatten(), yct2.flatten()]).T
    # rotate
    xyp = np.matmul(angs, xy.T).T / 1e2
    xyp0 = xyp[0, :]  # the first point in the bathy data in local meter units=0,0

    # rotate DWS area
    values = dws_b.mask_dws.values
    xc = dws_b.xc
    yc = dws_b.yc
    y_idx, x_idx = np.where(values)  # True values
    x_true = xc[x_idx]
    y_true = yc[y_idx]
    points = np.column_stack((x_true, y_true))

    # rotate values
    points_rot = np.matmul(angs, points.T).T / 1e2
    points_rot = points_rot - xyp0
    points_rot[:, 0] = points_rot[:, 0] + xctp0
    points_rot[:, 1] = points_rot[:, 1] + yctp0

    ##### rotate contour of DWS data
    # contour of DWS------
    bdr_dws0p = np.full((boundary_points.shape[0], 2), np.nan)
    # rotate
    bdr_dws0p = np.matmul(angs, boundary_points.T).T / 1e2
    # correct model units:
    # 1)substact the first model local point of the topo file, but give tha same as xyp0=[0,0]
    # 2)use the first projected point of the case (lon,lat model units to meter)
    bdr_dws0p = bdr_dws0p - xyp0
    bdr_dws0p[:, 0] = bdr_dws0p[:, 0] + xctp0 - 1000
    bdr_dws0p[:, 1] = bdr_dws0p[:, 1] + yctp0 - 5400

    ##### rotate bathymetry data
    # Land area
    values_ = ds.h.values
    y_idx_, x_idx_ = np.where(np.isnan(values_))
    x_true_ = xc[x_idx_]
    y_true_ = yc[y_idx_]
    points_ = np.column_stack((x_true_, y_true_))

    # rotate values
    points_rot_ = np.matmul(angs, points_.T).T / 1e2
    points_rot_ = points_rot_ - xyp0
    points_rot_[:, 0] = points_rot_[:, 0] + xctp0
    points_rot_[:, 1] = points_rot_[:, 1] + yctp0
    data_h = np.full((6400, 6400), np.nan)

    for idx in range(0, len(x_idx_)):
        data_h[
            int(points_rot_[idx][1]) - 1 : int(points_rot_[idx][1]) + 2,
            int(points_rot_[idx][0]) - 1 : int(points_rot_[idx][0]) + 2,
        ] = 1

    data_h = data_h[5400:6200, 1000:2200]
    data_h[0:300, 280:1200] = 1  # add land area
    ## end of - this part of code is the same for three functions

    ##### rotations of data
    data_ = np.full((data.shape[0], 800, 1200), np.nan)
    xrr = ((ds.xr.values - 116.7) * 10).astype(int)
    yr = ((ds.yr.values - 543.3) * 10).astype(int)

    data_ = np.full((data.shape[0], 800, 1200), np.nan)

    for idx0 in range(0, data.shape[0]):
        for idx_x in range(0, data.shape[2]):
            for idx_y in range(0, data.shape[1]):
                data_[
                    idx0,
                    yr[idx_y, idx_x]
                    - 2
                    + 34 : yr[idx_y, idx_x]
                    + 3
                    + 34,  # the values of shift could be different
                    xrr[idx_y, idx_x]
                    - 2
                    + 165 : xrr[idx_y, idx_x]
                    + 3
                    + 165,  # the values of shift could be different
                ] = data[idx0, idx_y, idx_x]

    # Replace DWS area with nan
    data_h[~np.isnan(data_[0])] = np.nan

    # Close the datasets
    ds.close()
    dws_b.close()

    yticks = np.arange(0, 800)
    xticks = np.arange(0, 1200)

    # Create the figure
    fig = px.imshow(
        data_,
        x=xticks,
        y=yticks,
        animation_frame=0,
        origin="lower",
        title="Residence time : mean residence time for 15 days",
        width=800,
        height=500,
    )

    # Add boundary to the facet
    fig.add_trace(
        go.Scatter(
            x=bdr_dws0p[:, 0],
            y=bdr_dws0p[:, 1],
            mode="lines",
            line=dict(color="black", width=2),
            name="",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(z=data_h, colorscale=[[0, "white"], [1, "gray"]], showscale=False),
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
            colorbar=dict(title="Residence time (days)"),
        )
    )

    # Modify the layout x and y axis
    fig.update_layout(
        xaxis=dict(
            title="Easting (km)",
            tickvals=[0, 200, 400, 600, 800, 1000, 1200],  # Locations of ticks
            ticktext=[0, 20, 40, 60, 80, 100, 120],
        ),
        yaxis=dict(
            title="Northing (km)",
            tickvals=[0, 200, 400, 600, 800],  # Locations of ticks
            ticktext=[0, 20, 40, 60, 80],
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
