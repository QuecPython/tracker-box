import net
import utime
from usr.libs import CurrentApp
from usr.libs.threading import Thread
from usr.libs.logging import getLogger
import _thread  

logger = getLogger(__name__)


class LbsService(object):

    def __init__(self, app=None):
        self.__net = net
        if app is not None:
            self.init_app(app)

    def __str__(self):
        return '{}'.format(type(self).__name__)
    

    def init_app(self, app):
        self.event = app.event
        app.register('lbs_service', self)

    def load(self):
        logger.info('loading {} extension, init lbs will take some seconds'.format(self))
        Thread(target=self.start_update).start()

    def read(self):
        cell_info = net.getCellInfo()
        if cell_info != -1 and cell_info[2]:
            first_tuple = cell_info[2]
            mcc_decimal = first_tuple[0][2]  # Retrieve the decimal MCC (e.g., 1120)
            #mcc_hex = "{:x}".format(mcc_decimal).upper()  # Convert to hexadecimal (e.g., '460')

            lbs_data = "$LBS,{},{},{},{},{},0*69;".format(
                mcc_decimal,
                first_tuple[0][3],
                first_tuple[0][5],
                first_tuple[0][1],
                first_tuple[0][7]
            )
            return lbs_data

    def start_update(self):
        while True:
            if self.event.is_set():
                lbs_data = self.read()
                if lbs_data is None:
                    utime.sleep(2)
                    continue

                for _ in range(3):
                    with CurrentApp().qth_client:
                        if CurrentApp().qth_client.sendLbs(lbs_data):
                            break
                else:
                    logger.debug("send lbs data to qth server fail, next report will be after 2 seconds")
                    utime.sleep(2)
                    continue
                
                logger.debug("send lbs data to qth server success, next report will be after 300 seconds")
                utime.sleep(300)
            else:
                utime.sleep(0.1)
            
    def put_lbs(self):
            while True:
                lbs_data = self.read()
                if lbs_data is None:
                    utime.sleep(2)
                    continue

                for _ in range(3):
                    with CurrentApp().qth_client:
                        if CurrentApp().qth_client.sendLbs(lbs_data):
                            break
                else:
                    logger.debug("send lbs data to qth server fail, next report will be after 2 seconds")
                    utime.sleep(2)
                    continue
                
                logger.debug("send LBS data to qth server success")
                break
            

                
