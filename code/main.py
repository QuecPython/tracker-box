import pm
import utime
import dataCall
from umqtt import MQTTClient
try:
    from libs.logging import getLogger
    from libs import Application
    from extensions import (
    qth_client,
    gnss_service,
    lbs_service,
    battery_service,
    #sensor_service,
)
except ImportError:
    from usr.libs.logging import getLogger
    from usr.libs import Application
    from usr.extensions import (
    qth_client,
    gnss_service,
    lbs_service,
    battery_service,
    #sensor_service,
    )

WAIT_NETWORK_READY_S = 30   # 30s

logger = getLogger(__name__)


def create_app(name="SimpliKit", version="1.0.0", config_path="/usr/config.json"):
    _app = Application(name, version)
    _app.config.init(config_path)

    qth_client.init_app(_app)
    #lbs_service.init_app(_app)
    gnss_service.init_app(_app) 
    battery_service.init_app(_app)
    #sensor_service.init_app(_app)

    return _app


def wait_network_ready():
    wait_cnt = WAIT_NETWORK_READY_S / 5
    is_ready = False

    while wait_cnt:        
        lte = dataCall.getInfo(1, 0)
        if lte[2][0] == 1:
            is_ready = True                        
            break

        utime.sleep(5)
        wait_cnt -= 1    
    
    return is_ready


if __name__ == "__main__":
    while True:
        if wait_network_ready():
            pm.set_psm_time(0)
            #pm.set_psm_time(0, 1, 0, 2) # Set T3412 to 10 minutes, T3324 to 4 seconds            
            #pm.set_psm_time(0, 2, 0, 2) # Set T3412 to 20 minutes, T3324 to 4 seconds            
            #pm.set_psm_time(0, 3, 0, 2) # Set T3412 to 30 minutes, T3324 to 4 seconds            
            #pm.set_psm_time(1, 4, 0, 2) # Set T3412 to 4 hours (1 hours X 4), T3324 to 4 seconds            
            #pm.set_psm_time(1, 8, 0, 2) # Set T3412 to 8 hours (1 hours X 4), T3324 to 4 seconds            
            psm_enabled = pm.get_psm_time()    
            logger.debug('psm time set parameter NO1 : ', psm_enabled)        
            pm.autosleep(1)
            logger.debug('Set autosleep ...')
            logger.debug('lte network normal')
            break
        logger.debug('wait lte network normal...')        

        #ret=dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)
        ret=dataCall.setPDPContext(1, 2, 'quectel.tn.std', '', '', 0)
        ret2=dataCall.activate(1)
        while not ret and ret2:
            #ret=dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0)  # 激活之前，应该先配置APN，这里配置第1路的APN
            #ret=dataCall.setPDPContext(1, 2, 'KT.pilot.ip.ktnbiot', '', '', 0) # KT APN            
            ret=dataCall.setPDPContext(1, 2, 'quectel.tn.std', '', '', 0) # Quectel APN
            ret2=dataCall.activate(1)
            if  ret and ret2:
                print("Net injection failure")
                break
    
    app = create_app()
    logger.debug('Start')          
    app.run()
    logger.debug('Stop')

