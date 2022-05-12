"""
Copyright 2022 NOAA
All rights reserved.

Unit tests for io_utils

"""
import os
import pathlib
import pytest
import yaml

from rnr_score_hv import harvesters
from rnr_score_hv.harvester_base import harvest
from rnr_score_hv.yaml_utils import YamlLoader
from rnr_score_hv.innov_netcdf import Region, InnovStatsConfig


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
        },
    },'output_format': harvesters.PANDAS_DATAFRAME
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
        print(f'conf_dict: {conf_yaml_fn}, documents: {documents}')

    data1 = harvest(VALID_CONFIG_DICT)
    harvest_dict = YamlLoader(conf_yaml_fn).load()[0]
    data2 = harvest(conf_yaml_fn)

    assert len(data1) == len(data2)

    print(f'dataframe column names: {data2.columns.values.tolist()}')

    print(f'harvested {len(data1)} records using config: {VALID_CONFIG_DICT}')
    print(f'harvested {len(data2)} records using config: {harvest_dict}')
    print(f'harvested data type: {type(data2)}')
    print(f'harvested data: {data2}')

def test_netcdf_harvester_region_config():
    """
    Test region class
    """

    region = Region('test_region', -10.0, 10.0)
    with pytest.raises(ValueError):
        region = Region(5, -10, 10)
    with pytest.raises(ValueError):
        region = Region({}, -10, 10)
    with pytest.raises(ValueError):
        region = Region([], -10, 10)
    with pytest.raises(ValueError):
        region = Region('test_region', -10, 10)
    with pytest.raises(ValueError):
        region = Region('test_region', -10, [])
    with pytest.raises(ValueError):
        region = Region('test_region', -10, {})