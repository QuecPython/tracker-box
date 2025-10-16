from misc import Power
import net
import utime
from usr.libs import CurrentApp
from usr.libs.threading import Thread
from usr.libs.logging import getLogger
import _thread  
import quecgnss
# KHK, Temporarily
# import gnss_service

logger = getLogger(__name__)

BATTERY_OCV_TABLE = {
    "nix_coy_mnzo2": {
        55: {
            4152: 100, 4083: 95, 4023: 90, 3967: 85, 3915: 80, 3864: 75, 3816: 70, 3773: 65, 3737: 60, 3685: 55,
            3656: 50, 3638: 45, 3625: 40, 3612: 35, 3596: 30, 3564: 25, 3534: 20, 3492: 15, 3457: 10, 3410: 5, 3380: 0,
        },
        20: {
            4143: 100, 4079: 95, 4023: 90, 3972: 85, 3923: 80, 3876: 75, 3831: 70, 3790: 65, 3754: 60, 3720: 55,
            3680: 50, 3652: 45, 3634: 40, 3621: 35, 3608: 30, 3595: 25, 3579: 20, 3548: 15, 3511: 10, 3468: 5, 3430: 0,
        },
        0: {
            4147: 100, 4089: 95, 4038: 90, 3990: 85, 3944: 80, 3899: 75, 3853: 70, 3811: 65, 3774: 60, 3741: 55,
            3708: 50, 3675: 45, 3651: 40, 3633: 35, 3620: 30, 3608: 25, 3597: 20, 3585: 15, 3571: 10, 3550: 5, 3500: 0,
        },
    },
}
class BatteryService(object):
    def __init__(self, app=None):       
        self.interval = 30                
        self.__net = net        
        if app is not None:
            self.init_app(app, battery_ocv="nix_coy_mnzo2")

    def __str__(self):
        return '{}'.format(type(self).__name__)

    def init_app(self, app, battery_ocv="nix_coy_mnzo2"):
        self.gnss_sleep_event = app.gnss_sleep_event
        self.interval = app.config["SLEEP_INTERVAL_SECONDS"]
        self.__energy = 100
        self.__temp = 30
        self.__vbatt_count = 100
        if not BATTERY_OCV_TABLE.get(battery_ocv):
            raise TypeError("Battery OCV %s is not support." % battery_ocv) 
        self.__battery_ocv = battery_ocv
        app.register('battery_service', self)

    def load(self):
        logger.info('loading {} extension, init battery will take some seconds'.format(self))
        Thread(target=self.start_update).start()

    def __get_soc_from_dict(self, key, volt_arg):
        """Get battery energy from map"""
        if BATTERY_OCV_TABLE[self.__battery_ocv].get(key):
            volts = sorted(BATTERY_OCV_TABLE[self.__battery_ocv][key].keys(), reverse=True)            
            pre_volt = 0
            volt_not_under = 0  # Determine whether the voltage is lower than the minimum voltage value of soc.
            for volt in volts:
                if volt_arg > volt:
                    volt_not_under = 1
                    soc1 = BATTERY_OCV_TABLE[self.__battery_ocv][key].get(volt, 0)
                    soc2 = BATTERY_OCV_TABLE[self.__battery_ocv][key].get(pre_volt, 0)
                    break
                else:
                    pre_volt = volt
            if pre_volt == 0:  # Input Voltarg > Highest Voltarg
                return soc1
            elif volt_not_under == 0:
                return 0
            else:
                return soc2 - (soc2 - soc1) * (pre_volt - volt_arg) // (pre_volt - volt)
            
    def __get_soc(self, temp, volt_arg):
        """Get battery energy by temperature and voltage"""
        if temp > 30:
            return self.__get_soc_from_dict(55, volt_arg)
        elif temp < 10:
            return self.__get_soc_from_dict(0, volt_arg)
        else:
            return self.__get_soc_from_dict(20, volt_arg)            

    def __get_power_vbatt(self):
        """Get vbatt from power"""        
        return int(sum([Power.getVbatt() for i in range(self.__vbatt_count)]) / self.__vbatt_count)

    def set_temp(self, temp):
        """Set now temperature."""
        if isinstance(temp, int) or isinstance(temp, float):
            self.__temp = temp
            return True
        return False    
            
    def start_update(self):
        while True:
            if quecgnss.getPriority():            
                self.__energy = self.__get_soc(self.__temp, self.__get_power_vbatt())            
                data = {4: self.__energy}                
                if data:
                    with CurrentApp().qth_client:
                        for _ in range(3):
                            if CurrentApp().qth_client.sendTsl(1, data):
                                logger.debug("send battery data to qth server success") 
                                break                   
                #self.gnss_sleep_event.set()  # Notify GNSS service to wake up
                utime.sleep(self.interval)
            else:
                utime.sleep(0.1)