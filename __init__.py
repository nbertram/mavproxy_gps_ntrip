from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module, mp_util


class NTripStation:
    lat: float
    lon: float
    code: str

    def __init__(self, lat: float, lon: float, code: str):
        self.lat = lat
        self.lon = lon
        self.code = code

    def get_distance_to(self, lat: float, long: float) -> float:
        return mp_util.gps_distance(self.lat, self.lon, lat, long)


NTRIP_STATIONS = [
    NTripStation(-41.2, 174.93, "AVLN00NZL0"),
    NTripStation(-40.59, 175.24, "LEVN00NZL0"),
]


class RTKGPSDetection(mp_module.MPModule):
    def __init__(self, mpstate):
        super(RTKGPSDetection, self).__init__(
            mpstate, "gps_ntrip", "GPS NTRIP configurer"
        )
        self.mpstate = mpstate
        self.vehicle = mpstate.master()

        self.gps_detection_done = False

    def gps_raw_int_callback(self, m):
        # Check if the GPS is locked, even roughly
        if m.fix_type >= 2:
            self.gps_detection_done = True
            self.setup_ntrip(m.lat * 1.0e-7, m.lon * 1.0e-7)

    def setup_ntrip(self, lat, lon):
        for station in NTRIP_STATIONS:
            # find station within 50km
            print(
                f"station {station.code} = {station.get_distance_to(lat, lon)} from {lat},{lon}"
            )
            if station.get_distance_to(lat, lon) < 50000:
                print(f"Detected NTrip close to {station.code}, choosing this feed")
                self.mpstate.functions.process_stdin(
                    f"ntrip set mountpoint {station.code}"
                )
                self.mpstate.functions.process_stdin("ntrip start")
                return

    def mavlink_packet(self, m):
        if not self.gps_detection_done:
            if m.get_type() == "GPS_RAW_INT":
                self.gps_raw_int_callback(m)


def init(mpstate):
    return RTKGPSDetection(mpstate)
