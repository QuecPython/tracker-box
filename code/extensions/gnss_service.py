import utime
import quecgnss
from usr.libs import CurrentApp
from usr.libs.threading import Thread, Event
from usr.libs.logging import getLogger
import _thread
from .import qth_client
try:
    from math import sin, asin, cos, radians, fabs, sqrt
except:
    from cmath import sin as csin, cos as ccos, pi

    def radians(x):
        return x * pi / 180.0
    
    def fabs(x):
        return x if x > 0 else -x

    def sin(x):
        return csin(x).real
    
    def cos(x):
        return ccos(x).real
    
    def asin(x):
        low, high = -1, 1
        while abs(high - low) > 1e-10:  # Precision control
            mid = (low + high) / 2.0
            if sin(mid) < x:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0


logger = getLogger(__name__)


EARTH_RADIUS = 6371  # Earth's average radius is approximately 6371 km
GLOBAL_DISTANCE = 0  # Distance in km


def hav(theta):
    s = sin(theta / 2)
    return s * s


def gps_distance(lat0, lng0, lat1, lng1):
    # Use the haversine formula to calculate the distance between two points on a sphere
    # Convert latitude and longitude to radians
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)
    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(pow(h, 0.5))  # km
    # distance = int(distance * 1000)  # m
    return distance


class NmeaDict(dict):

    @classmethod
    def load(cls, raw):
        items = {}
        for line in raw.split('\r\n'):
            try:
                tail_index = line.rfind('*')
                if tail_index == -1:
                    continue
                head_index = line.rfind('$', 0, tail_index)
                if head_index == -1:
                    continue
                crc = int(line[tail_index + 1:tail_index + 3], 16)
                if cls.checksum(line[head_index + 1:tail_index]) != crc:
                    raise ValueError('CRC check failed')
                cmdlist = line[head_index:tail_index].split(',')
                # print(line[head_index:])
                if cmdlist[0] not in items:
                    items[cmdlist[0]] = []
                items[cmdlist[0]].append(line)
            except Exception as e:
                # logger.debug('parse nmea line error: {}; pass it: {}'.format(e, line))
                continue
        return cls(items)

    @staticmethod
    def checksum(data):
        crc = ord(data[0])
        for one in (ord(_) for _ in data[1:]):
            crc ^= one
        return crc


class GnssService(object):

    def __init__(self, app=None):
        self.__gnss = quecgnss
        if app is not None:
            self.init_app(app)

    def __str__(self):
        return '{}'.format(type(self).__name__)

    def init_app(self, app):
        self.event = app.event
        app.register('gnss_service', self)

    def load(self):
        logger.info('loading {} extension, init quecgnss will take some seconds'.format(self))
        result = self.init()
        logger.info('{} init gnss res: {}'.format(self, result))
        if result:
            Thread(target=self.start_update).start()

    def init(self):  
        if self.__gnss.init() != 0:
            logger.warn('{} gnss init FAILED'.format(self))
            return False
        return True

    def status(self):
        # 0    int    GNSS module is in the off state
        # 1    int    GNSS module firmware is being upgraded
        # 2    int    GNSS module is positioning. In this mode, GNSS positioning data can be read, but whether the positioning data is valid needs to be determined by the user after parsing the corresponding sentence, for example, by checking if the status of the GNRMC sentence is A or V. A indicates valid positioning, while V indicates invalid positioning.
        return self.__gnss.get_state()

    def enable(self, flag=True):
        return self.__gnss.gnssEnable(bool(flag)) == 0

    def read(self, size=4096):
        raw = self.__gnss.read(size)
        if raw != -1:
            size, data = raw
            # logger.debug('gnss read raw {} bytes data:\n{}'.format(size, data))
            return NmeaDict.load(data)
        
    def check_gnss_signal(self, nmea_dict):
        
        snr_threshold = 15
        min_sats = 3
        has_3d_fix = False
        if "$GNGSA" in nmea_dict:
            for line in nmea_dict["$GNGSA"]:
                parts = line.split(",")
                if len(parts) > 2 and (parts[2] == "3" or parts[2] == "2"):
                    has_3d_fix = True
                    break

        if not has_3d_fix:
            return False

        snrs = []

        def extract_snrs(lines):
            for line in lines:
                parts = line.split(",")
                i = 4
                while i + 3 < len(parts):
                    snr_str = parts[i + 3]
                    if snr_str.isdigit():
                        snrs.append(int(snr_str))
                    i += 4

        if "$GPGSV" in nmea_dict:
            extract_snrs(nmea_dict["$GPGSV"])

        if "$GBGSV" in nmea_dict:
            extract_snrs(nmea_dict["$GBGSV"])

        if "$GAGSV" in nmea_dict:
            extract_snrs(nmea_dict["$GAGSV"])

        # count satelites with SNR > 15
        count = 0
        for snr in snrs:
            if snr > snr_threshold:
                count += 1
                if count >= min_sats:
                    return True

        return False

        
    def start_update(self):
        prev_lat_and_lng = None

        while True:
            nmea_dict = self.read()
            if nmea_dict is None or not self.check_gnss_signal(nmea_dict):
                #set the event so lbs can start
                self.event.set()
                utime.sleep(3)
                continue
            else:
                #clear the event; only gnss works
                self.event.clear()
                

            nmea_data = None

            if nmea_data is None:
                if "$GNRMC" in nmea_dict:
                    for temp in nmea_dict["$GNRMC"]:
                        nmea_tuple = temp.split(",")
                        if nmea_tuple[2] == "A":
                            nmea_data = temp

                            lat_string = nmea_tuple[3]
                            lat_high = float(lat_string[:2])
                            lat_low = float(lat_string[2:]) / 60
                            lat = lat_high + lat_low
                            if nmea_tuple[4] == "S":
                                lat = -lat
                            
                            lng_string = nmea_tuple[5]  # 11755.787896484374 (unit: minutes)
                            lng_high = float(lng_string[:3])
                            lng_low = float(lng_string[3:]) / 60
                            lng = lng_high + lng_low
                            if nmea_tuple[6] == "W":
                                lng = -lng

                            break

            if nmea_data is None:
                if "$GNGGA" in nmea_dict:
                    for temp in nmea_dict["$GNGGA"]:
                        nmea_tuple = temp.split(",")
                        if nmea_tuple[6] != "0":
                            nmea_data = temp

                            lat_string = nmea_tuple[2]
                            lat_high = float(lat_string[:2])
                            lat_low = float(lat_string[2:]) / 60
                            lat = lat_high + lat_low
                            if nmea_tuple[3] == "S":
                                lat = -lat

                            lng_string = nmea_tuple[4]  # 11755.787896484374 (unit: minutes)
                            lng_high = float(lng_string[:3])
                            lng_low = float(lng_string[3:]) / 60
                            lng = lng_high + lng_low
                            if nmea_tuple[5] == "W":
                                lng = -lng                               
                            break

            logger.debug("data: {}".format(nmea_data))
            logger.debug("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

            #sending gnss data to the server only if its the data from the first measurement or if distance displacement from the last measurement is bigger then 50m
            if nmea_data is not None:
                # logger.debug("GPS data: {}".format(nmea_data))
                # logger.debug("prev_lat_and_lng: {}".format(prev_lat_and_lng))
                logger.debug("lat_and_lng: {}".format((lat, lng)))
                if prev_lat_and_lng is None:
                    # First positioning
                    for _ in range(3):
                        with CurrentApp().qth_client:
                            if CurrentApp().qth_client.sendGnss(nmea_data):
                                prev_lat_and_lng = (lat, lng)
                                logger.error("send gnss to qth server success")
                                break
                            else:
                                logger.error("send gnss to qth server fail")
                else:
                    # Or if the displacement exceeds 50m, report it
                    distance = gps_distance(prev_lat_and_lng[0], prev_lat_and_lng[1], lat, lng)
                    logger.debug('distance delta: {:f}'.format(distance))
                    if distance >= 0.05:
                        for _ in range(3):
                            with CurrentApp().qth_client:
                                if CurrentApp().qth_client.sendGnss(nmea_data):
                                    prev_lat_and_lng = (lat, lng)
                                    logger.error("send gnss to qth server success")
                                    break
                        else:
                            logger.error("send gnss to qth server fail")
            utime.sleep(3)


