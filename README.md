census-shapefile-utils
======================

Tools for fetching shapefiles from the Census FTP site, then extracting
data from them.

### Installation ###

1. Clone this repository: `git@github.com:censusreporter/census-shapefile-utils.git`
2. Enter the `census-shapefile-utils` directory.
3. *If using `parse_shapefiles.py`*, then install dependencies: `pip install -r requirements.txt`
    * Note: package `gdal` requires non-Python library, `libgdal`. Follow OS-specific installation to obtain this library.


### fetch_shapefiles.py ###

This script will download TIGER data shapefiles from the Census FTP site.
It can be used to download a set of geographies defined in `GEO_TYPES_LIST`,
or can be used to fetch files for a single state and/or single geography type.

    >> python fetch_shapefiles.py
    >> python fetch_shapefiles.py -s WA
    >> python fetch_shapefiles.py -g place
    >> python fetch_shapefiles.py -s WA -g place

If you use the -s argument to fetch files for a single state, the script
will also download the national county, state and congressional district
files that include data for your chosen state.

The script will create `DOWNLOAD_DIR` and `EXTRACT_DIR` directories
if necessary, fetch a zipfile or set of zipfiles from the Census website,
then extract the shapefiles from each zipfile retrieved.

`DISABLE_AUTO_DOWNLOADS` will prevent certain geography types from being
automatically downloaded if no -g argument is passed to `fetch_shapefiles.py`.
This may be useful because certain files, such as those for Zip Code
Tabulation Areas, are extremely large. You can still target any geography
in `GEO_TYPES_LIST` specifically, however. So to fetch the ZCTA data:

    >> python fetch_shapefiles.py -g zcta5

The `FTP_HOME` setting at the top of `fetch_shapefiles.py` assumes you want
data from the TIGER2012 directory. If you want a different set of shapefiles,
adjust this accordingly.


### parse_shapefiles.py ###

After you run `fetch_shapefiles.py`, this script will generate a csv file
from the extracted data. These files will have a normalized set of headers,
so varying geography types can be included in the same csv. Each row also gets
some useful additional fields not directly found in the shapefiles, Including:

* `FULL_GEOID`: Concatenated Census summary level code and Census GEOID
* `FULL_NAME`: Human-friendly name for the geography. So city names,
for instance, also include the state name, e.g. "Spokane, Washington"
* `SUMLEV`: Census summary level code
* `GEO_TYPE`: Name of the geography type, e.g. "state"
* `REGION`: Where applicable, a Census Region code. Shapefiles for states
include this code; this script infers the value based on state for other
geography types.
* `REGION_NAME`: Name of the Census Region, e.g. "West"
* `DIVISION`: Where applicable, a Census Division code. Shapefiles for states
include this code; this script infers the value based on state for other
geography types.
* `DIVISION_NAME`: Name of the Census Division, e.g. "Pacific"

This script will search all directories inside `EXTRACT_DIR` for shapefiles.
Pass an -s argument to limit by state, and/or pass a -g argument to limit
to a single geography type.

    >> python parse_shapefiles.py
    >> python parse_shapefiles.py -s WA
    >> python parse_shapefiles.py -g place
    >> python parse_shapefiles.py -s WA -g place
    
This script will generate a single csv file with your chosen data, and write
it to `CSV_DIR`. Headers are pulled from `helpers/csv_helpers.py`. The methods
for building rows specific to each geography type are also in `csv_helpers`.

You can choose whether the generated csv should include polygon geometries,
which can significantly increase the size of the output file. Include
geometries by passing a -p flag.

    >> python parse_shapefiles.py -s WA -p

Geometry data for certain geography types can be *very* large. The `zcta5`
geometries, for instance, will add about 1.1 Gb of data to your csv.

### Examples ###

These assume you have already used `fetch_shapefiles.py` to download
the shapefiles you want to get data from.

`>> python parse_shapefiles.py -g place` will make `place.csv`, which includes
data from all records at the Census place level.

`>> python parse_shapefiles.py -s WA` will make `all_geographies_WA.csv`,
which includes all geographies in Washington state, from the state record
all the way down to cities (places) and school districts. It will not include
polygon geometries.

`>> python parse_shapefiles.py -s WA -g county -p` will make `county_WA.csv`,
which includes data from all counties in Washington state. Because the -p flag
was passed, it will also include polygon geometries for each record.

`>> python parse_shapefiles.py` will make `all_geographies.csv`, which
includes data from all geography levels and all states. If you've downloaded
shapefiles for all levels, including for Zip Code Tabulation Areas, the csv
file should be about 19 Mb.

`>> python parse_shapefiles.py -p` will make the same file as above, but
including geometries. This file takes about 17 minutes to build locally on my
Macbook Air, and is about 2.45 Gb.
