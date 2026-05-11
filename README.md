# Spreewasser-N

- Postgres Version 14.5
- Postgis Version 3.3
- import shapefile from https://github.com/Rodrigo-NH/django-shapefileimport
- swn/data/monica_net_cdf is not on the github because of the size of the contained files
- Thredds: Unidata https://www.unidata.ucar.edu/community/index.html#acknowledge


## Installation
### 1. Install git
```shell
sudo apt-get install git
```

### 2. Install docker on your system/ server
https://docs.docker.com/engine/install/ubuntu/


### 3. Get repo and run the docker build
cd into the directory where the application is supposed to be built (user directory).
Then clone the git repo into that folder:
```shell
git clone https://github.com/ColjaK/Spreewasser-N.git
```
Get the necessary data and paste the folder app_data into the directory Spreewasser-N.
Get the database data and paste its folder into Spreewasser-N.

```shell
sudo chmod -R 777 ./app_data
```

Copy the .env to Spreewasser-N/.env or create that file:
```shell
touch Spreewasser-N/.env
nano .env
```

In nano add the passwords for
DJANGO_SECRET_KEY=9???

DJANGO_ALLOWED_HOSTS=???


DB_NAME=postgis
DB_USER=???
DB_PASS=???

GEOSERVER_USER=??
GEOSERVER_PASS=???

DWD_HOST=???
DWD_USERNAME=??
DWD_PASSWORD=??
DWD_PORT=??


CLIM4CAST_FTP_SERVER=???
CLIM4CAST_SFTP_USER=???
CLIM4CAST_SFTP_PORT=??
CLIM4CAST_SFTP_PASSWORD=???
    
Copy the app_data folder to Spreewasser-n/. app_data contains the raster data for toolbox and monica as well as the geoip2 db and the location for klim4cast.

Then check for development setups and change the variable accordingly:
```shell
nano docker-compose.prod.yml
```
set DEV="false" for production and save.
set DJANGO_DEBUG: 0 for production, 1 for debugging. 

```shell
cd Spreewasser-N
```

For development
```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml build 
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

For production (you may have to run with sudo)
```shell
docker compose -f docker-compose.yml -f docker-compose.prod.yml build 
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```


### 3. Start containers
### 4. Database
First you have to setup the django database. Open the terminal in the django container:
```shell
docker exec -it swn_geo_django bash
```
!! If you want to transfer Monica project data, you have to do a dump via postgres. Create the new db via postgres and finally do a 'python manage.py migrate --fake-initial' !!

In dev mode:
If you transfer Monica projects, it will cause problems due to a GenericForeignKey in the class MonicaSite. 
Now the database is set up - you can connect to it from your localhost on port 5432.
To import the database, point the management command to the folder holding the database as json files by:
```shell
python manage.py db_to_disk --import-dir path/to/db_files
```

For production copy the files into the directory app/model_imports.
change the permissions of the model.jsons:
```shell
sudo docker exec -it swn_geo_django bash
```
inside the container do
```shell
chmod -R 777 app/model_imports
```
Then import the models
```shell
python manage.py db_to_disk --import-dir model_imports/
```


### 5. Run management commands 
For the manual import of data run
for chechglobe 
```shell
python manage.py update_chech_globe_data
```
for monica's weather data
```shell
python manage.py import_all_hindcast_data
python manage.py import_forecast_data
```
to register the rasterfiles used in the Toolbox
```shell
python manage.py register_geoserver_files
```

### 5. Thredds Server
The Thredds server is used to store and serve NetCDF data.

### 6. Geoserver
The Geoserver is used as Tileserver for large geodatasets. It is necessary for the display of raster data.

### 7.Run the django apps
To start the django server open the commandline in the django-container
```shell
docker exec -it swn_geo_django bash
```

To expose the website on port 8000
```shell
python manage.py runserver 0.0.0.0:8000
```



### Apps

### buek
This app provides an API for soil data of Germany. The data is based on the [Buek200 by the BGR](https://www.bgr.bund.de/DE/Themen/Boden/Produkte/produkte_node.html). 
The data is modified, so that the most common soil profile for the actual landuse from the [CLC 2018 map](https://land.copernicus.eu/en/products/corine-land-cover/clc2018) can easily be retrieved.

### utilities
Utilities is a helper django-app. It hosts management commands relevant for all applications.

### klim4cast
Application for publishing drought data from Chechglobe.

### monica
Application that provides access through a GUI to the model MONICA. It accesses automatically weatherdata from the DWD and soil data from the modified buek.


## Management commands
To run management commands, you have to be in a bash shell within the django container. To get there run
```shell
docker exec -it swn_geo_django bash
```

### klim4cast
To manually update the klim4cast data run
```shell
python manage.py update_chech_globe_data
```

### monica
#### Import forecast data
Imports the seasonal weatherforecast for Germany
```shell
python manage.py import_forecast_data
```
If this command fails, the DWD has likely moved the location of the forecast data on their server.

### Import hindcast data
Imports the measured weatherdata that is not yet present in the system
```shell
python manage.py import_hindcast_data
```

### toolbox
#### Update or create monthly and yearly averages of the waterleveldata

This commend creates new monthly or yearly averages or - if they already exist - updates them
```shell
python manage.py update_monthly_and_yearly_levels
```
This aggregates only the monthly values (yearly accordingly)
```shell
python manage.py your_command_name --type monthly
```

This aggregates the yearly values only for the stations with the id 1, 3, and 5
```shell
python manage.py your_command_name --type yearly --station 1 3 5
```

### utilities
#### Import/export database: db_to_disk
To export all models (including those of auth, celery etc.) as one json-file per model 

Arguments:
--import-dir 
string defining the folder to be imported. This arguments sets the import mode.
```shell
python manage.py db_to_disk --import-dir directory
```

```shell
python manage.py db_to_disk --models appname.ModelName
```

--no-today
Exports, but does not create a date folder

--apps
List of model class names to export (space-separated)

export users app
```shell
python manage.py db_to_disk --apps users

```
Export only the UserProfile model from any app:
```shell
python manage.py db_to_disk --models UserProfile

```
Export multiple apps and models at once:
```shell
python manage.py db_to_disk --apps users toolbox --models UserProfile MapLabel


```