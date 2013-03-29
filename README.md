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
from the extracted data. It will search all directories inside `EXTRACT_DIR`
to find shapefiles.

Pass an -s argument to limit by state, and pass a -g argument to limit
by geography type.

    >> python parse_shapefiles.py
    >> python parse_shapefiles.py -s WA
    >> python parse_shapefiles.py -g place
    >> python parse_shapefiles.py -s WA -g place

You can choose whether the generated csv should include polygon geometries,
which increases the size of the output file significantly. Include geometries
by passing a -p flag.

    >> python parse_shapefiles.py -s WA -p
