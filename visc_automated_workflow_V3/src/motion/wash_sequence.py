import time
from hardware.pump.esp32 import PumpESP32
from motion.sample_handler import go_to_wash_station

WASH1_WAIT = 30
WASH2_WAIT = 30
WASH3_WAIT = 30


def wash1(cnc, pump: PumpESP32):
    go_to_wash_station(cnc, station_idx=0, safe=True)
    print("[WASH1] start")
    pump.send_tag(b"1")
    time.sleep(WASH1_WAIT)


def wash2(cnc, pump: PumpESP32):
    go_to_wash_station(cnc, station_idx=1, safe=True)
    print("[WASH2] start")
    pump.send_tag(b"2")
    time.sleep(WASH2_WAIT)


def wash3(cnc, pump: PumpESP32):
    go_to_wash_station(cnc, station_idx=2, safe=True)
    print("[WASH3] start")
    pump.send_tag(b"3")
    time.sleep(WASH3_WAIT)
