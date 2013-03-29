'''
After running `fetch_shapefiles.py`, use this script to generate csv
from the extracted data. It will iterate over all directories inside
EXTRACT_DIR to find shapefiles.

Pass an -s argument to limit by state, and pass a -g argument to limit
by geography type.

>> python parse_shapefiles.py
>> python parse_shapefiles.py -s WA
>> python parse_shapefiles.py -g place
>> python parse_shapefiles.py -s WA -g place

You can choose whether the generated csv should include polygon geometries,
which increase the size of the output file significantly. Include geometries
by passing a -p flag.

>> python parse_shapefiles.py -s WA -p

The csv files you generate will be written to `CSV_DIR`. A common set
of headers is pulled from `helpers/csv_helpers.py`, so varying geography
types can be included in the same csv. Methods specific to building a proper
row for each geography type are also found in `csv_helpers`.
'''

import csv, optparse, os, sys, traceback
from operator import itemgetter
from os.path import isdir, join, normpath
from osgeo import ogr

from __init__ import (EXTRACT_DIR, CSV_DIR, STATE_FIPS_DICT, GEO_TYPES_DICT, \
    STATE_ABBREV_LIST, GEO_TYPES_LIST, get_fips_code_for_state)
from helpers import csv_helpers


def get_shapefile_directory_list(state=None, geo_type=None):
    shapefile_directory_list = [
        os.path.join(EXTRACT_DIR, directory) \
        for directory in os.walk(EXTRACT_DIR).next()[1]
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
        if filename.endswith('.shp'):
            return normpath(join(shapefile_directory, filename))


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


def parse_shapefiles(shapefile_directory_list, state=None, geo_type=None):
    data_dicts = []
    for shapefile_directory in shapefile_directory_list:
        _shapefile = _get_shapefile_from_dir(shapefile_directory)
        _geo_type = _get_geo_type_from_file(_shapefile)
        
        print "Parsing: " + _shapefile + " ..."
        _shapefile_data = build_dict_list(_shapefile, state, _geo_type)
        data_dicts.extend(_shapefile_data)
        
    output_geo = geo_type if geo_type else 'all_geographies'
    output_state = '_%s' % state if state else ''
    output_filename = '%s%s.csv' % (output_geo, output_state)
    sorted_data_dicts = sorted(data_dicts, key=itemgetter('FULL_GEOID'))
    
    write_csv(output_filename, sorted_data_dicts)


def build_dict_list(filename, state=None, geo_type=None):
    shapefile = ogr.Open(filename)
    layer = shapefile.GetLayer()
    state_check = get_fips_code_for_state(state) if state else None
    dict_list = []
    
    feature = layer.GetNextFeature()
    while feature:
        item = {}
        if geo_type == 'zcta5':
            # ZCTA shapefiles have different attribute names
            item = csv_helpers.make_zcta5_row(item, feature, geo_type)
        else:
            # All other geo_types share attribute names
            # Filter rows by state if -s arg is passed
            _statefp = feature.GetField("STATEFP")
            if not state_check or (state_check == _statefp):
                _item_options = {
                    'statefp': _statefp,
                    'include_polygon': options.include_polygon,
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


def write_csv(filename, dict_list):
    csvfilename = os.path.basename(filename).replace('.shp', '.csv')
    csvpath = normpath(join(CSV_DIR, csvfilename))
    csvfile = open(csvpath,'wb')
    
    print "Writing: " + csvpath + " ...\n"
    
    csvwriter = csv.DictWriter(
        csvfile,
        csv_helpers.get_fields_for_csv(
            include_polygon=options.include_polygon
        ),
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
        help='specific state file to convert',
        choices=STATE_ABBREV_LIST,
    )
    parser.add_option(
        '-g', '--geo', '--geo_type',
        dest='geo_type',
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
            os.mkdir(path)
    
    state = options.state if options.state else None
    geo_type = options.geo_type if options.geo_type else None

    shapefile_directory_list = get_shapefile_directory_list(
        state = state,
        geo_type = geo_type,
    )

    parse_shapefiles(
        shapefile_directory_list,
        state = state,
        geo_type = geo_type,
    )


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)

