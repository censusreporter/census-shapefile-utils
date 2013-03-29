census-shapefile-utils
======================

Tools for fetching shapefiles from the Census FTP site, then extracting
data from them.

### fetch_shapefiles.py ###

This script will download TIGER data shapefiles from the Census FTP site.
It can be used to download a set of geographies defined in `GEO_TYPES_LIST`,
or can be used to fetch files for a single state and/or single geography type.

    >> python fetch_shapefiles.py
    >> python fetch_shapefiles.py -s WA
    >> python fetch_shapefiles.py -g place
    >> python fetch_shapefiles.py -s WA -g place

The script will create `DOWNLOAD_DIR` and `EXTRACT_DIR` directories
if necessary, fetch a zipfile or set of zipfiles from the Census website,
then extract the shapefiles from each zipfile retrieved.

`DISABLE_AUTO_DOWNLOADS` will prevent certain geography types from being
automatically downloaded if no -g argument is passed to `fetch_shapefiles.py`.
This may be useful because certain files, such as those for Zip Code
Tabulation Areas, are extremely large. You can still target any geography
in `GEO_TYPES_LIST` specifically, however. So to fetch the ZCTA data:

    >> python fetch_shapefiles.py -g zcta5


### parse_shapefiles.py ###

After running `fetch_shapefiles.py`, you can use this script to generate csv
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
Pass an -s argument to limit by state, and pass a -g argument to limit
to a single geography type.

    >> python parse_shapefiles.py
    >> python parse_shapefiles.py -s WA
    >> python parse_shapefiles.py -g place
    >> python parse_shapefiles.py -s WA -g place

You can choose whether the generated csv should include polygon geometries,
which can significantly increase the size of the output file. Include
geometries by passing a -p flag.

    >> python parse_shapefiles.py -s WA -p

Geometry data for certain geography types can be *very* large. The `zcta5`
geometries, for instance, will add about 1.1 Gb of data to your csv.

The csv files you generate will be written to `CSV_DIR`. The set of normalized
headers is pulled from `helpers/csv_helpers.py`. Methods specific to building
a proper row for each geography type are also found in `csv_helpers`.
