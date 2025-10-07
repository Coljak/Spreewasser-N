# Spreewasser-N

- Postgres Version 14.5
- Postgis Version 3.3
- import shapefile from https://github.com/Rodrigo-NH/django-shapefileimport
- swn/data/monica_net_cdf is not on the github because of the size of the contained files
- Thredds: Unidata https://www.unidata.ucar.edu/community/index.html#acknowledge


## Installation
### 1. Install docker on your system/ server
### 2. Run the docker build
```shell
cd into/folder_of/docker-compose
docker-compose build 
```
### 3. Start containers
### 4. Database
First you have to setup the django database. Open commandline in the django container:
```shell
docker exec -it swn_geo_django bash
```
Then in the open bash run the django migrations:
```shell
python manage.py makemigrations
python manage.py migrate
```
Now the database is set up - you can connect to it from your localhost on port 5432.
To import the database, point the management command to the folder holding the database as json files by:
```shell
python manage.py db_to_disk --import-dir path/to/db_files
```
### 5.Run the django apps
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

### utils
Utils is a helper django-app. It hosts management commands relevant for all applications.

### klim4cast
Application for publishing drought data from Chechglobe.

### monica
Application that provides access through a GUI to the model MONICA. It accesses automatically weatherdata from the DWD and soil data from the modified buek.


## Management commands
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

This aggregates the yearly values only for the stations with the id 1, 2, and 3
```shell
python manage.py your_command_name --type yearly --station 1 3 5
```

### utils
#### Import/export database: db_to_disk
To export all models (including those of auth, celery etc.) as one json-file per model 

Arguments:
--import-dir 
string defining the folder to be imported. This arguments sets the import mode.
```shell
python manage.py db_to_disk --models UserProfile

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