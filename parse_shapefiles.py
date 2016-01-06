'''
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
'''

import csv, optparse, os, sys, traceback
import glob
from operator import itemgetter
from os.path import isdir, join, normpath
from osgeo import ogr

from __init__ import (EXTRACT_DIR, CSV_DIR, STATE_FIPS_DICT, GEO_TYPES_DICT, \
    STATE_ABBREV_LIST, GEO_TYPES_LIST, get_fips_code_for_state)
from helpers import csv_helpers


def get_shapefile_directory_list(state=None, geo_type=None):
    _, directories, _ = next(os.walk(EXTRACT_DIR))
    shapefile_directory_list = [
        os.path.join(EXTRACT_DIR, directory)
        for directory in directories
        if len(glob.glob(os.path.join(EXTRACT_DIR, directory, '*.shp'))) > 0
    ]

    if geo_type:
        # handle cd112, cd113, zcta5, etc.
        if geo_type in ['cd','zcta5']:
            geo_type_check = '_us_%s' % geo_type
            shapefile_directory_list = filter(
                lambda directory: geo_type_check in directory,
                shapefile_directory_list
            )
        else:
            geo_type_check = '_%s' % geo_type.lower()
            shapefile_directory_list = filter(
                lambda directory: directory.endswith(geo_type_check),
                shapefile_directory_list
            )
    
    if state:
        state_check = '_%s_' % get_fips_code_for_state(state)
        shapefile_directory_list = filter(
            lambda directory: state_check in directory \
            or ('_us_' in directory and '_us_zcta5' not in directory),
            shapefile_directory_list
        )

    return shapefile_directory_list


def _get_shapefile_from_dir(shapefile_directory):
    for filename in os.listdir(shapefile_directory):
        if filename.lower().endswith('.shp'):
            return normpath(join(shapefile_directory, filename))
    raise Exception('No .shp file found in %s' % shapefile_directory)


def _get_geo_type_from_file(filename):
    basename = filename.split('.')[0]
    geo_type = basename.split('_')[-1]
    # handle cd112, cd113, etc.
    if geo_type.startswith('cd'):
        return 'cd'
    # handle zip code tabulation areas
    if geo_type.startswith('zcta5'):
        return 'zcta5'
    return geo_type


def parse_shapefiles(shapefile_directory_list, state=None, geo_type=None,
                     include_polygon=False):
    data_dicts = []
    for shapefile_directory in shapefile_directory_list:
        _shapefile = _get_shapefile_from_dir(shapefile_directory)
        _geo_type = _get_geo_type_from_file(_shapefile)
        
        print "Parsing: " + _shapefile + " ..."
        _shapefile_data = build_dict_list(
            _shapefile, state=state, geo_type=_geo_type,
            include_polygon=include_polygon)
        data_dicts.extend(_shapefile_data)
        
    output_geo = geo_type if geo_type else 'all_geographies'
    output_state = '_%s' % state if state else ''
    output_filename = '%s%s.csv' % (output_geo, output_state)
    sorted_data_dicts = sorted(data_dicts, key=itemgetter('FULL_GEOID'))

    write_csv(output_filename, sorted_data_dicts,
              include_polygon=include_polygon)


def build_dict_list(filename, state=None, geo_type=None,
                    include_polygon=False):
    shapefile = ogr.Open(filename)
    layer = shapefile.GetLayer()
    state_check = get_fips_code_for_state(state) if state else None
    dict_list = []

    feature = layer.GetNextFeature()
    while feature:
        item = {}
        if geo_type == 'zcta5':
            # ZCTA shapefiles have different attribute names
            _item_options = {
                'include_polygon': include_polygon,
            }
            item = csv_helpers.make_zcta5_row(feature, item, geo_type, _item_options)
        else:
            # All other geo_types share attribute names
            # Filter rows by state if -s arg is passed
            _statefp = feature.GetField("STATEFP")
            if not state_check or (state_check == _statefp):
                _item_options = {
                    'statefp': _statefp,
                    'include_polygon': include_polygon,
                    'geoid': feature.GetField("GEOID"),
                    'state_dict': STATE_FIPS_DICT[str(_statefp)],
                }
                
                item = csv_helpers.make_basic_row(feature, item, geo_type, _item_options)
                if geo_type:
                    row_builder = getattr(csv_helpers, 'make_%s_row' % geo_type)
                    item = row_builder(feature, item, _item_options)

        if item:
            dict_list.append(item)
        feature.Destroy()
        feature = layer.GetNextFeature()
        
    shapefile.Destroy()

    return dict_list


def write_csv(filename, dict_list, include_polygon=False):
    csvfilename = os.path.basename(filename).replace('.shp', '.csv')
    csvpath = normpath(join(CSV_DIR, csvfilename))
    csvfile = open(csvpath,'wb')
    
    print "Writing: " + csvpath + " ...\n"
    
    csvwriter = csv.DictWriter(
        csvfile,
        csv_helpers.get_fields_for_csv(include_polygon=include_polygon),
        quoting=csv.QUOTE_ALL
    )
    csvwriter.writeheader()
    for item in dict_list:
        csvwriter.writerow(item)
    csvfile.close()


def process_options(arglist=None):
    global options, args
    parser = optparse.OptionParser()
    parser.add_option(
        '-s', '--state',
        dest='state',
        default=None,
        help='specific state file to convert',
        choices=STATE_ABBREV_LIST,
    )
    parser.add_option(
        '-g', '--geo', '--geo_type',
        dest='geo_type',
        default=None,
        help='specific geographic type to convert',
        choices=GEO_TYPES_LIST
    )
    parser.add_option(
        '-p', '--poly',
        action='store_true',
        dest='include_polygon',
        help='include polygon geometry in output csv'
    )
    options, args = parser.parse_args(arglist)
    return options, args


def main(args=None):
    """
    >> python parse_shapefiles.py
    >> python parse_shapefiles.py -s WA
    >> python parse_shapefiles.py -g place
    >> python parse_shapefiles.py -s WA -g place
    >> python parse_shapefiles.py -s WA -g place -p
    """
    if args is None:
        args = sys.argv[1:]
    options, args = process_options(args)

    # make sure we have the expected directories
    for path in [CSV_DIR,]:
        if not isdir(path):
            os.makedirs(path)

    shapefile_directory_list = get_shapefile_directory_list(
        state=options.state,
        geo_type=options.geo_type,
    )

    parse_shapefiles(
        shapefile_directory_list,
        state=options.state,
        geo_type=options.geo_type,
        include_polygon=options.include_polygon
    )


if __name__ == '__main__':
    main()
