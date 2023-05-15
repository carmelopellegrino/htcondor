from typing import Optional

from .htcondor2_impl import _handle as handle_t

from .htcondor2_impl import _collector_init
from .htcondor2_impl import _collector_query
from .htcondor2_impl import _collector_locate_local
from .htcondor2_impl import _collector_advertise

# Only necessary for typehints, which we may prefer to use docstrings for,
# so that the names are the externally-visible ones in the documentation.
from ._ad_type import AdType
from ._daemon_type import DaemonType


def _ad_type_from_daemon_type(daemon_type: DaemonType):
    map = {
        DaemonType.Master: AdType.Master,
        DaemonType.Startd: AdType.Startd,
        DaemonType.Schedd: AdType.Schedd,
        DaemonType.Negotiator: AdType.Negotiator,
        DaemonType.Generic: AdType.Generic,
        DaemonType.HAD: AdType.HAD,
        DaemonType.Credd: AdType.Credd,
    }
    # FIXME: Should raise HTCondorEnumError.
    return map.get(daemon_type, None)


class Collector():

    def __init__(self, pool: Optional[str] = None):
        self._handle = handle_t()
        _collector_init(self, self._handle, pool)


    # FIXME: In version 1, `constraint` could also be an ExprTree.
    def query(self,
      ad_type: AdType = AdType.Any,
      constraint: Optional[str] = None,
      projection: Optional[list[str]] = None,
      statistics: Optional[list[str]] = None,
    ):
        # str(None) is "None", which is a valid ClassAd expression (a bare
        # attribute reference), so convert to the empty string, instead.
        # We don't pass `constraint` through unmodified because we'll want
        # the str() conversions for all of the other data types we care
        # about to work anyway, and it's easier to do/handle the conversion
        # in Python.
        if constraint is None:
            constraint = ""
        return _collector_query(self._handle, int(ad_type), str(constraint), projection, statistics, None)


    def directQuery(self,
        daemon_type,
        name: Optional[str] = None,
        projection: Optional[list[str]] = None,
        statistics: Optional[list[str]] = None,
    ):
        daemon_ad = self.locate(daemon_type, name)
        return _collector_query(self._handle, int(daemon_type), daemon_ad, projection, statistics, None)


    _for_location = ["MyAddress", "MyAddressV1", "CondorVersion", "CondorPlatform", "Name", "Machine"]


    def locate(self,
        daemon_type: DaemonType,
        name: Optional[str] = None,
    ):
        if name is None:
            return _collector_locate_local(self, _handle, int(daemon_type))
        else:
            ad_type = _ad_type_from_daemon_type(daemon_type)
            constraint = f'stricmp(Name, "{name}") == 0'
            return _collector_query(self._handle, int(ad_type), constraint, Collector._for_location, None, name)


    def locateAll(self,
        daemon_type: DaemonType,
    ):
        ad_type = _ad_type_from_daemon_type(daemon_type)
        projection = ["MyAddress", "MyAddressV1", "CondorVersion", "CondorPlatform", "Name", "Machine"]
        return self.query(ad_type, projection=Collector._for_location)


    def advertise(self,
        ad_list,
        command: str = "UPDATE_AD_GENERIC",
        use_tcp: bool = True,
    ):
        return _collector_advertise(self._handle, ad_list, command, use_tcp)