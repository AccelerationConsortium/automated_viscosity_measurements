import time
from hardware.cnc.controller import CNC_Machine


def go_to_sample(cnc: CNC_Machine, rack: str, idx: int, safe: bool = True, wait_s: float = 0):
    print(f"[SAMPLE] Moving to {rack}[{idx}]")
    cnc.move_to_location(rack, idx, safe=safe)
    if wait_s > 0:
        print(f"[SAMPLE] Waiting {wait_s}s for measurement...")
        time.sleep(wait_s)


def go_to_wash_station(cnc: CNC_Machine, station_idx: int, safe: bool = True):
    cnc.move_to_location("washing_station", station_idx, safe=safe)
