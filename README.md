## Aggregated_data_visualisations
This repository contains jupyter notebooks for visualisations of spatial and 15-day aggregations made for the Dutch Wadden Sea (DWS) related variables, and also volume flux of rivers connected to the Dutch Wadden Sea.

*Visualisations can be found in [visualisations.ipynb](https://github.com/LOCO-EX/Aggregated_data_visualisations/blob/main/notebooks/visualisations.ipynb) notebook that include:*
- The volume, average and standard deviation of salinity and temperature variables for the whole area of the Dutch Wadden Sea each hour.
- The 15 days average and standard deviation of salinity and temperature variables for each point of the Dutch Wadden Sea, and the expousure percentage.
- The volume flux of the rivers.

### Data

Visualised data is a product of postprocessing, which can be found in [DWS_data_aggregations](https://github.com/LOCO-EX/DWS_data_aggregations) repository.

The doi to location in https://data.4tu.nl/ will be provided.

### Sofware
The environment employed for the scripts used for the visualisations is based on Python v3.12 and can be found in the file [environment.yml](https://github.com/LOCO-EX/Aggregated_data_visualisations/blob/main/environment.yml).


### Running the Notebooks
All the scripts necessary for reproducing the plots and heatmaps displayed in the notebooks are in the folder [visualisation_scripts](https://github.com/LOCO-EX/Aggregated_data_visualisations/tree/main/visualisation_scripts). [postBuild.sh](https://github.com/LOCO-EX/Aggregated_data_visualisations/blob/main/postBuild.sh) file is used for Binder and can be ignored when running locally or in Google Colab.

These notebooks are located in the folder [notebooks](https://github.com/LOCO-EX/Aggregated_data_visualisations/tree/main/notebooks). They can be run using any of the following instructions:
- Mybinder.org: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LOCO-EX/Aggregated_data_visualisations/main). When running in Binder, *Cancel* build recommendation if it appears with a suggestion *@plotly/dash-jupyterlab needs to be included in build*.
- Google Colab: follow the instructions from the notebook [clone_repo_using_google_colab.ipynb](https://github.com/LOCO-EX/Aggregated_data_visualisations/blob/main/clone_repo_using_google_colab.ipynb).
- Clone or download the repository: install the packages of the file [environment.yml](https://github.com/LOCO-EX/Aggregated_data_visualisations/blob/main/environment.yml) and run the notebooks locally.
