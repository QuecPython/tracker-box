# EG912U-GL-Tracker
EG912U-GL-Tracker code for QuecPython.

## Directory Structure

```plaintext
EG912U-GL-Tracker/
├── code/
│   ├── drivers/
│   │   ├── icm20948.py
│   │   ├── lps22hb.py
│   │   ├── shtc3.py
│   │   └── tcs34725.py
│   ├── extensions/
│   │   ├── __init__.py
│   │   ├── gnss_service.py
│   │   ├── lbs_service.py
│   │   ├── qth_client.py
│   │   └── sensor_service.py
│   ├── libs/
│   │   ├── __init__.py
│   │   ├── collections.py
│   │   ├── common.py
│   │   ├── i2c.py
│   │   ├── logging.py
│   │   ├── pypubsub.py
│   │   └── threading.py
│   ├── Qth/
│   │   ├── ...
│   ├── config.json
│   ├── config2.json
│   └── main.py
├── firmware/
│   └── 8915DM_cat1_open_EG912UGLAAR05A01M08_TEST0220_merge_20250319-1741.pac
└── readme.md
```

`drivers` -  driver code for SensorHub;

`gnss_service.py` - get GNSS data;

`lbs_service` - get LBS data;

`qth_client` - qthSDK code;

`sensor_service` - get sensors data;

`config.json` - Configuring the connected server;
