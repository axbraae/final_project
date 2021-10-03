# Final Project

An end-to-end data project for the final CodeClan and PDA Data Science project. Written in Python in Jupyter notebooks.

For this project, the project brief was written for the "client" Newark Liberty International Airport to investigate flight departure delays.

The following approach was taken:

- Source additional weather data
- Clean data (pandas)
- Exploratory data analysis (seaborn, matplotlib, folium, geopandas)
- Model departure delay (Random Forest classifier, scikit learn)
- Deliver business insights

Highlights:

- Geospatial data to visualise flight departure delays per destination airport

      * Width of flight path indicates total flights to destination airport
      * Colour of airport indicates percentage of flights which departed with delay
![Destination delay plot](/documentation/screenshots/dest_delay_plot_fig.png)

- Exploratory data analysis of different weather metrics for flights which departed on time and for those which were delayed. 

      * Wind direction is shown as an example.
![Wind_direction plot](/documentation/screenshots/wind_dir_plot_fig.png)

- Random forest modelling of flight departure delays

      * Top ten features important for the Random Forest Classifier after permutation
![model_feature_importance plot](/documentation/screenshots/model_importance_plot_fig.png)
