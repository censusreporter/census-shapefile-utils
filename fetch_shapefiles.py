'''
This script will download TIGER data shapefiles from the Census FTP site.
It can be used to download a set of geographies defined in GEO_TYPES_LIST,
or can be used to fetch files for a single state and/or single geography type.

>> python fetch_shapefiles.py
>> python fetch_shapefiles.py -s WA
>> python fetch_shapefiles.py -g place
>> python fetch_shapefiles.py -s WA -g place

This will create DOWNLOAD_DIR and EXTRACT_DIR if necessary, fetch a zipfile
or set of zipfiles from the Census website, then extract the shapefiles from
each zipfile retrieved.

`DISABLE_AUTO_DOWNLOADS` will prevent certain geography types from being
automatically downloaded if no -g argument is passed to `fetch_shapefiles.py`.
This may be useful because certain files, such as those for Zip Code
Tabulation Areas, are extremely large. You can still target any geography
in `GEO_TYPES_LIST` specifically, however. So to fetch the ZCTA data:

>> python fetch_shapefiles.py -g zcta5

The `FTP_HOME` setting assumes you want data from the TIGER2012 directory.
If you want a different set of shapefiles, adjust this accordingly.
'''

import sys, optparse, os, traceback, urllib2, zipfile
from os.path import isdir, join, normpath, split

from __init__ import (DOWNLOAD_DIR, EXTRACT_DIR, STATE_ABBREV_LIST, \
    GEO_TYPES_LIST, DISABLE_AUTO_DOWNLOADS, get_fips_code_for_state)

FTP_HOME = 'ftp://ftp2.census.gov/geo/tiger/TIGER2012/'


def get_filename_list_from_ftp(target, state):
    target_files = urllib2.urlopen(target).read().splitlines()
    filename_list = []

    for line in target_files:
        filename = '%s%s' % (target, line.split()[-1])
        filename_list.append(filename)

    if state:
        state_check = '_%s_' % get_fips_code_for_state(state)
        filename_list = filter(
            lambda filename: state_check in filename \
            or ('_us_' in filename and '_us_zcta5' not in filename),
            filename_list
        )

    return filename_list


def download_files_in_list(filename_list):
    downloaded_filename_list = []
    for file_location in filename_list:
        filename = '%s/%s' % (DOWNLOAD_DIR, file_location.split('/')[-1])
        u = urllib2.urlopen(file_location)
        f = open(filename, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])

        print "Downloading: %s Bytes: %s" % (filename, file_size)
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()
        downloaded_filename_list.append(filename)
    
    return downloaded_filename_list
    

def extract_downloaded_file(filename):
    zipped = zipfile.ZipFile(filename, 'r')
    zip_dir = filename.replace('.zip','').split('/')[-1]
    target_dir = normpath(join(EXTRACT_DIR, zip_dir))

    print "Extracting: " + filename + " ..."
    zipped.extractall(target_dir)
    zipped.close()


def get_one_geo_type(geo_type, state=None):
    target = '%s%s/' % (FTP_HOME, geo_type.upper())

    print "Finding files in: " + target + " ..."
    filename_list = get_filename_list_from_ftp(target, state)
    downloaded_filename_list = download_files_in_list(filename_list)

    for filename in downloaded_filename_list:
        extract_downloaded_file(filename)


def get_all_geo_types(state=None):
    AUTO_DOWNLOADS = filter(
        lambda geo_type: geo_type not in DISABLE_AUTO_DOWNLOADS,
        GEO_TYPES_LIST
    )
    for geo_type in AUTO_DOWNLOADS:
        get_one_geo_type(geo_type, state)


def process_options(arglist=None):
    global options, args
    parser = optparse.OptionParser()
    parser.add_option(
        '-s', '--state',
        dest='state',
        help='specific state to download',
        choices=STATE_ABBREV_LIST
    )
    parser.add_option(
        '-g', '--geo', '--geo_type',
        dest='geo_type',
        help='specific geographic type to download',
        choices=GEO_TYPES_LIST
    )
    
    options, args = parser.parse_args(arglist)
    return options, args


def main(args=None):
    """
    >> python fetch_shapefiles.py
    >> python fetch_shapefiles.py -s WA
    >> python fetch_shapefiles.py -g place
    >> python fetch_shapefiles.py -s WA -g place
    """
    if args is None:
        args = sys.argv[1:]
    options, args = process_options(args)
    
    # make sure we have the expected directories
    for path in [DOWNLOAD_DIR, EXTRACT_DIR]:
        if not isdir(path):
            os.mkdir(path)

    state = options.state if options.state else None
    geo_type = options.geo_type if options.geo_type else None
    
    # get one geo_type or all geo_types
    if geo_type:
        get_one_geo_type(
            geo_type = geo_type,
            state = state,
        )
    else:
        get_all_geo_types(
            state = state,
        )


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)

