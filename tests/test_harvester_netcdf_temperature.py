"""
Copyright 2022 NOAA
All rights reserved.

Unit tests for io_utils

"""
import os
import pathlib
import yaml

from rnr_score_hv import harvesters
from rnr_score_hv.harvester_base import harvest


PYTEST_CALLING_DIR = pathlib.Path(__file__).parent.resolve()
NETCDF_HARVESTER_CONFIG__VALID = 'netcdf_harvester_config__valid.yaml'

DATA_DIR = 'data'
CONFIGS_DIR = 'configs'

file_path = os.path.join(
    PYTEST_CALLING_DIR,
    DATA_DIR
)
VALID_CONFIG_DICT = {
    'harvester_name': harvesters.INNOV_TEMPERATURE_NETCDF,
    'file_meta': {
        'filepath': file_path,
        'cycletime_str': '%Y%m%d%H',
        'cycle': '2015120206',
        'filename_str': 'innov_stats.metric.%Y%m%d%H.nc'
    },
    'stats': ['bias', 'count', 'rmsd'],
    'metrics': ['temperature','spechumid','uvwind'],
    'regions': {
        'equatorial': {
            'lat_min': -5.0,
            'lat_max': 5.0
        },
        'global': {
            'lat_min': -90.0,
            'lat_max': 90.0
        },
        'north_hemis': {
            'lat_min': 20.0,
            'lat_max': 60.0
        },
        'tropics': {
            'lat_min': -20.0,
            'lat_max': 20.0
        },
        'south_hemis': {
            'lat_min': -60.0,
            'lat_max': -20.0
        },
        'south_hemis': {
            'lat_min': -60.0,
            'lat_max': -20.0
        }
    }
}

def test_netcdf_harvester_config():
    """
    Test basic harvester configuration
    """
    conf_yaml_fn = os.path.join(
        PYTEST_CALLING_DIR,
        CONFIGS_DIR,
        NETCDF_HARVESTER_CONFIG__VALID
    )

    with open(conf_yaml_fn, 'w') as file:
        documents = yaml.dump(VALID_CONFIG_DICT, file)
        print(f'conf_dict: {VALID_CONFIG_DICT}, documents: {documents}')

    data = harvest(VALID_CONFIG_DICT)
    print(f'harvested {len(data)} records using config: {VALID_CONFIG_DICT}')
