"""
Copyright 2022 NOAA
All rights reserved.

Collection of methods to facilitate file/object retrieval

"""
from collections import namedtuple
from rnr_score_hv.innov_netcdf import InnovStatsConfig, InnovStatsHarvester


INNOV_TEMPERATURE_NETCDF = 'innov_temperature_netcdf'


Harvester = namedtuple(
    'Harvester',
    [
        'name',
        'config_handler',
        'data_parser'
    ],
)

harvester_registry = {
    'innov_temperature_netcdf': Harvester(
        'innovation statistics temperature (netcdf)',
        InnovStatsConfig,
        InnovStatsHarvester
    )
}
