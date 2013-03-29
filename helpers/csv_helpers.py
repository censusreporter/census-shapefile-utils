'''
Helper functions for making csv files in parse_shapefiles.py
'''

def get_fields_for_csv(include_polygon=False):
    field_list = [
        'FULL_GEOID',
        'FULL_NAME',
        'SUMLEV',
        'GEO_TYPE',
        'REGION',
        'REGION_NAME',
        'DIVISION',
        'DIVISION_NAME',
        'STATEFP',
        'GEOID',
        'CD112FP',
        'CDSESSN',
        'COUNTYFP',
        'PLACEFP',
        'CLASSFP',
        'SLDLST',
        'SLDUST',
        'ELSDLEA',
        'SCSDLEA',
        'UNSDLEA',
        'PCICBSA',
        'PCINECTA',
        'CSAFP',
        'CBSAFP',
        'METDIVFP',
        'ZCTA5CE10',
        'NAME',
        'NAMELSAD',
        'LSAD',
        'ALAND',
        'INTPTLAT',
        'INTPTLON',
    ]
    if include_polygon:
        field_list.append('GEOMETRY')

    return field_list

def make_basic_row(feature, item, geo_type, item_options):
    # Set up the dict and populate common fields
    item.update({
        'FULL_GEOID': None,
        'FULL_NAME': None,
        'SUMLEV': None,
        'GEO_TYPE': geo_type,
        'REGION': item_options['state_dict']['region'],
        'REGION_NAME': item_options['state_dict']['region_name'],
        'DIVISION': item_options['state_dict']['division'],
        'DIVISION_NAME': item_options['state_dict']['division_name'],
        'STATEFP': item_options['statefp'],
        'GEOID': item_options['geoid'],
        'CD112FP': None,
        'CDSESSN': None,
        'COUNTYFP': None,
        'PLACEFP': None,
        'CLASSFP': None,
        'SLDLST': None,
        'SLDUST': None,
        'ELSDLEA': None,
        'SCSDLEA': None,
        'UNSDLEA': None,
        'PCICBSA': None,
        'PCINECTA': None,
        'CSAFP': None,
        'CBSAFP': None,
        'METDIVFP': None,
        'ZCTA5CE10': None,
        'NAME': None,
        'NAMELSAD': None,
        'LSAD': None,
        'ALAND': feature.GetField("ALAND"),
        'INTPTLAT': feature.GetField("INTPTLAT"),
        'INTPTLON': feature.GetField("INTPTLON"),
    })
    if item_options['include_polygon']:
        _geom = feature.GetGeometryRef()
        item.update({
            'GEOMETRY': str(_geom),
        })
    return item


'''
# the subset of fields that a non-zcta geo_type might update
def make_foo_row(feature, item, item_options):
    _sumlev = ''# each geo_type needs to set this
    _name = ''# each may want to cache this to build FULL_NAME
    _namelsad = ''# or cache this to build FULL_NAME
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': None,
        'SUMLEV': _sumlev,
        'CD112FP': feature.GetField("CD112FP"),
        'CDSESSN': feature.GetField("CDSESSN"),
        'COUNTYFP': feature.GetField("COUNTYFP"),
        'PLACEFP': feature.GetField("PLACEFP"),
        'CLASSFP': feature.GetField("CLASSFP"),
        'SLDLST': feature.GetField("SLDLST"),
        'SLDUST': feature.GetField("SLDUST"),
        'ELSDLEA': feature.GetField("ELSDLEA"),
        'SCSDLEA': feature.GetField("SCSDLEA"),
        'UNSDLEA': feature.GetField("UNSDLEA"),
        'PCICBSA': feature.GetField("PCICBSA"),
        'PCINECTA': feature.GetField("PCINECTA"),
        'CSAFP': feature.GetField("CSAFP"),
        'CBSAFP': feature.GetField("CBSAFP"),
        'METDIVFP': feature.GetField("METDIVFP"),
        'NAME': feature.GetField("NAME"),
        'NAMELSAD': feature.GetField("NAMELSAD"),
        'LSAD': feature.GetField("LSAD"),
    })
'''

def _build_full_geoid(sumlev, item_options):
    return '%s|%s' % (sumlev, item_options['geoid'])

def make_cd_row(feature, item, item_options):
    _sumlev = '500'
    _namelsad = feature.GetField("NAMELSAD")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s %s' % (item_options['state_dict']['name'], _namelsad),
        'SUMLEV': _sumlev,
        'CD112FP': feature.GetField("CD112FP"),
        'CDSESSN': feature.GetField("CDSESSN"),
        'NAMELSAD': _namelsad,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_county_row(feature, item, item_options):
    _sumlev = '050'
    _namelsad = feature.GetField("NAMELSAD")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s, %s' % (_namelsad, item_options['state_dict']['name']),
        'SUMLEV': _sumlev,
        'COUNTYFP': feature.GetField("COUNTYFP"),
        'CLASSFP': feature.GetField("CLASSFP"),
        'CSAFP': feature.GetField("CSAFP"),
        'CBSAFP': feature.GetField("CBSAFP"),
        'METDIVFP': feature.GetField("METDIVFP"),
        'NAME': feature.GetField("NAME"),
        'NAMELSAD': _namelsad,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_elsd_row(feature, item, item_options):
    _sumlev = '950'
    _name = feature.GetField("NAME")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s, %s' % (_name, item_options['state_dict']['name']),
        'SUMLEV': _sumlev,
        'ELSDLEA': feature.GetField("ELSDLEA"),
        'NAME': _name,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_scsd_row(feature, item, item_options):
    _sumlev = '960'
    _name = feature.GetField("NAME")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s, %s' % (_name, item_options['state_dict']['name']),
        'SUMLEV': _sumlev,
        'SCSDLEA': feature.GetField("SCSDLEA"),
        'NAME': _name,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_unsd_row(feature, item, item_options):
    _sumlev = '970'
    _name = feature.GetField("NAME")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s, %s' % (_name, item_options['state_dict']['name']),
        'SUMLEV': _sumlev,
        'UNSDLEA': feature.GetField("UNSDLEA"),
        'NAME': _name,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_sldu_row(feature, item, item_options):
    _sumlev = '610'
    _namelsad = feature.GetField("NAMELSAD")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s %s' % (item_options['state_dict']['name'], _namelsad),
        'SUMLEV': _sumlev,
        'SLDUST': feature.GetField("SLDUST"),
        'NAMELSAD': _namelsad,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_sldl_row(feature, item, item_options):
    _sumlev = '620'
    _namelsad = feature.GetField("NAMELSAD")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s %s' % (item_options['state_dict']['name'], _namelsad),
        'SUMLEV': _sumlev,
        'SLDLST': feature.GetField("SLDLST"),
        'NAMELSAD': _namelsad,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_place_row(feature, item, item_options):
    _sumlev = '160'
    _name = feature.GetField("NAME")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': '%s, %s' % (_name, item_options['state_dict']['name']),
        'SUMLEV': _sumlev,
        'PLACEFP': feature.GetField("PLACEFP"),
        'CLASSFP': feature.GetField("CLASSFP"),
        'PCICBSA': feature.GetField("PCICBSA"),
        'PCINECTA': feature.GetField("PCINECTA"),
        'NAME': feature.GetField("NAME"),
        'NAMELSAD': feature.GetField("NAMELSAD"),
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_state_row(feature, item, item_options):
    _sumlev = '040'
    _name = feature.GetField("NAME")
    item.update({
        'FULL_GEOID': _build_full_geoid(_sumlev, item_options),
        'FULL_NAME': _name,
        'SUMLEV': _sumlev,
        'NAME': _name,
        'LSAD': feature.GetField("LSAD"),
    })
    return item

def make_zcta5_row(feature, item, geo_type, item_options):
    # Zip Code Tabulation Area shapefiles have attrs named differently
    _sumlev = '860'
    _geoid = feature.GetField("GEOID10")
    _name = feature.GetField("ZCTA5CE10")
    item.update({
        'FULL_GEOID': '%s|%s' % (_sumlev, _geoid),
        'FULL_NAME': 'ZIP Code: %s' % _name,
        'SUMLEV': _sumlev,
        'GEO_TYPE': geo_type,
        'GEOID': _geoid,
        'CLASSFP': feature.GetField("CLASSFP10"),
        'ZCTA5CE10': _name,
        'ALAND': feature.GetField("ALAND10"),
        'INTPTLAT': feature.GetField("INTPTLAT10"),
        'INTPTLON': feature.GetField("INTPTLON10"),
    })
    if item_options['include_polygon']:
        _geom = feature.GetGeometryRef()
        item.update({
            'GEOMETRY': str(_geom),
        })
    return item

