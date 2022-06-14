"""
Copyright 2022 NOAA
All rights reserved.

Collection of methods to facilitate file/object retrieval

"""
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
import netCDF4

from score_hv.config_base import ConfigInterface
from score_hv import file_utils

valid_metrics = [
    'temperature',
    'spechumid',
    'uvwind'
]

VALID_STATS = [
    'bias',
    'count',
    'rmsd'
]

MIN_CYCLE_DATETIME = datetime(1988, 1, 1)
MAX_CYCLE_DATETIME = datetime.utcnow()
PLEV_PRESURE_UNIT = 'mb'

MIN_LONG = -180
MAX_LONG = 180


@dataclass
class Region:
    ''' region object storing region name and min/max latitude bounds '''
    name: str
    min_lat: float
    max_lat: float
    grid: str = field(default_factory=str, init=False)

    def __post_init__(self):
        if not isinstance(self.name, str):
            msg = f'name must be a string - name {self.name}'
            raise ValueError(msg)
        if (not isinstance(self.min_lat, float) or
            not isinstance(self.max_lat, float)):
            msg = f'min and max lat must be floats - min lat: {self.min_lat}' \
                f', max lat: {self.max_lat}'
            raise ValueError(msg)
        if self.min_lat > self.max_lat:
            msg = f'min_lat must be less than max_lat - ' \
                f'min_lat: {self.min_lat}, max_lat: {self.max_lat}'
            raise ValueError(msg)
        if self.max_lat < self.min_lat:
            msg = f'min_lat must be greater than min_lat - min_lat: {self.min_lat}, '\
                f'max_lat: {self.max_lat}'
            raise ValueError(msg)

        if abs(self.min_lat) > 90 or abs(self.max_lat) > 90:
            msg = f'min_lat or max_lat is out of allowed range, must be greater' \
                f' than -90 and let than 90 - min_lat: {self.min_lat}, ' \
                f'max_lat: {self.max_lat}'
            raise ValueError(msg)

        grid = '('
        grid += f'({MIN_LONG},{self.max_lat}),'
        grid += f'({MAX_LONG},{self.max_lat}),'
        grid += f'({MAX_LONG},{self.min_lat}),'
        grid += f'({MIN_LONG},{self.min_lat}),'
        grid += f'({MIN_LONG},{self.max_lat})'
        grid += ')'
        

DEFAULT_REGIONS = [
    Region('equatorial', -5.0, 5.0),
    Region('global', -90.0, 90.0),
    Region('north_hemis', 20.0, 60.0),
    Region('tropics', -20.0, 20.0),
    Region('south_hemis', -60.0, -20.0)
]


@dataclass
class MetricMeta:
    """
    Information pertaining to where a particular measurement type
    file can be found.

    Parameters:
    -----------
    name: str - metric name (temperature, uvwind, or spechumid)
    file_meta: dict - filename meta data containing file path
               filename format, and cycle time
    filename: str - configured full filename and absolute path
    cycletime: datetime - for reference, the relevant cycle time
               for the measurements
    """
    name: str
    file_meta: dict
    filename: str = field(default_factory=str, init=False)
    cycletime: datetime = field(init=False)

    def __post_init__(self):
        try:
            # build filename from the config meta data
            file_path = self.file_meta.get('filepath')
            cycle = self.file_meta.get('cycle')

            self.cycletime = datetime.strptime(
                cycle,
                self.file_meta.get('cycletime_str')
            )

            if (self.cycletime > MAX_CYCLE_DATETIME or
                self.cycletime < MIN_CYCLE_DATETIME):

                msg = f'cycle time {self.cycletime} is out of range, must ' \
                    f'be earlier than {MAX_CYCLE_DATETIME} and later than ' \
                    f'{MIN_CYCLE_DATETIME}.'
                raise ValueError(msg) from err

            filename_str = self.file_meta.get('filename_str')

            new_fn = filename_str.replace('metric', self.name)

            self.filename = file_path
            self.filename += '/' + self.cycletime.strftime(new_fn)
            file_utils.is_valid_readable_file(self.filename)

        except Exception as err:
            msg = f'Netcdf file could not be found or is empty' \
                f', file_meta: {self.file_meta} - err: {err}'
            raise ValueError(msg) from err


@dataclass
class HarvestConfig:
    """
    harvest configuration which dictates what metrics and stats
    to extract from the specified netcdf files
    """
    config_data: dict
    metrics: list = field(default_factory=list, init=False)
    stats: list = field(default_factory=list, init=False)
    regions: list = field(default_factory=list, init=False)
    metrics_meta: list = field(default_factory=list, init=False)

    def __post_init__(self):

        self.set_stats()
        self.set_regions()
        self.set_metrics_meta()

    def set_metrics_meta(self):
        """
        set the metric meta data specified by the config dict.  the
        metric meta data helps define the metric file location
        """
        try:
            self.metrics = self.config_data.get('metrics')
        except Exception as err:
            msg = f'\'metrics\' key missing, must be one of ' \
                f'({valid_metrics}) - err: {err}'
            raise KeyError(msg) from err

        print(f'config_data: {self.config_data}')
        file_meta = self.config_data.get('file_meta')
        print(f'file_meta: {file_meta}')
        for metric in self.metrics:
            try:

                metric_meta = MetricMeta(
                    metric,
                    file_meta
                )

                self.metrics_meta.append(metric_meta)
            except Exception as err:
                msg = f'Problem creating metrics_meta dataclass - err {err}'
                raise ValueError(msg) from err

        print(f'metrics_meta: {self.metrics_meta}')

    def set_stats(self):
        """
        set the metric meta data specified by the config dict.  the
        metric meta data helps define the metric file location
        """
        try:
            self.stats = self.config_data.get('stats')
            for stat in self.stats:
                if stat not in VALID_STATS:
                    msg = f'Invalid stat, must be one of \'{VALID_STATS}\''
                    raise KeyError(msg)
        except Exception as err:
            msg = f'\'stats\' key missing, must be one of ' \
                f'({VALID_STATS}) - err: {err}'
            raise KeyError(msg) from err


    def set_regions(self):
        """
        Configure region names and latitude bounds. Use default
        regions if none are specified.
        """
        try:
            regions = self.config_data.get('regions')
            if regions is not None:

                for name, region in regions.items():

                    lat_min = float(region.get('lat_min'))
                    lat_max = float(region.get('lat_max'))
                    self.regions.append(Region(name, lat_min, lat_max))
            else:
                self.regions = DEFAULT_REGIONS

        except Exception as err:
            msg = f'Problem parsing regions: {regions} - err: {err}'
            raise ValueError(msg) from err


@dataclass
class InnovStatsCfg(ConfigInterface):
    """
    Dataclass to hold and provide configuration information
    pertaining how the harvester should read netcdf information

    Parameters:
    -----------
    config_data: dict - contains configuration data parsed from
                 either an input yaml file or input dict

    file_meta: FileMeta - parsed configuration data
    """

    config_data: dict = field(default_factory=dict)
    harvest_config: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.harvest_config = self.set_config()

    def set_config(self):
        ''' initialize HarvestConfig from config_data dict '''
        return HarvestConfig(self.config_data)

    def get_metrics_meta(self):
        ''' return all configured MetricsMeta objects '''
        return self.harvest_config.metrics_meta

    def get_stats(self):
        ''' return list of all stat types based on harvest_config '''
        return self.harvest_config.stats

    def get_regions(self):
        ''' return list of region  '''
        return self.harvest_config.regions


HarvestedData = namedtuple(
    'HarvestedData',
    [
        'cycletime',
        'region_name',
        'region_bounds',
        'elevation',
        'elevation_units',
        'metric',
        'stat',
        'value'
    ],
)


@dataclass
class InnovStatsHv:
    """
    Harvester dataclass class used to parse innovation stats data stored in
    netcdf files

    Parameters:
    -----------
    config: InnovStatsCfg object containing information used to determine
            how to parse the dimensions plev and variable info store in the
            specified netcdf file/files

    Methods:
    --------

    get_data: parses statistics data in netcdf files based on input config
              file, returns a list of tuples containing specified data

    """
    config: InnovStatsCfg = field(default_factory=InnovStatsCfg)

    def get_data(self):
        """
        Harvests innovation statistics (bias, count, and rmsd) of
        temperature, specific humidity, and uv wind data.  Data resides
        in netcdf files and is grouped by region.  Metric types include
        temperature, specific humidity, and uv wind
        files.

        Returns
        -------
        harvested_data: list of HarvestedData tuples each consisting of
                        cycletime, region_name, region_min_lat,
                        region_max_lat, plev, metric type, stat type,
                        and value

        """

        # get list of MetricMeta data objects which define where the netcdf
        # file is located and what variables to read for each file.
        metrics = self.config.get_metrics_meta()
        harvested_data = []
        for metric in metrics:

            ncfile = netCDF4.Dataset(metric.filename)
            try:

                plevs = ncfile.variables['plevs'][...]
                regions = self.config.get_regions()
                stats = self.config.get_stats()

                for region in regions:

                    for stat in stats:

                        nc_varname = f'{stat}_{region.name}'
                        nc_vardata = ncfile.variables[nc_varname][...]
                        vardata_len = len(nc_vardata)

                        for idx in range(len(nc_vardata)):
                            item = HarvestedData(
                                metric.cycletime,
                                region.name,
                                region.grid,
                                plevs[idx],
                                PLEV_PRESURE_UNIT,
                                metric.name,
                                stat,
                                nc_vardata[idx]
                            )

                            harvested_data.append(item)

            except Exception as err:
                msg = f'problem parsing netcdf file {metric.filename} - ' \
                    f'err: {err}'
                raise ValueError(msg) from err

            ncfile.close()

        # could convert the list of named tuples to a pandas dataframe
        # df = pd.DataFrame(harvested_data), columns=harvested_data.fields)

        return harvested_data
