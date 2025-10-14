import csv, time, pathlib
from hardware.viscometer.client import ViscometerClient

def run_dynamic_analysis(results_dir: pathlib.Path, client: ViscometerClient):
    RPMS              = [2.5, 3.0, 3.5, 4.0, 4.5, 4.5, 4.5, 5.0, 5.5, 6.0]  
    DWELL_SECONDS     = 90.0     
    SETTLE_SECONDS    = 1.0     
    INTER_PAUSE_SEC   = 1.0      
    CSV_NAME          = "dynamic_analysis.csv"

    out = results_dir / CSV_NAME
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for rpm in RPMS:
        client.set_speed(float(rpm))
        time.sleep(SETTLE_SECONDS)
        # dwell at rpm
        time.sleep(max(DWELL_SECONDS - SETTLE_SECONDS, 0.0))
        pkt = client.read_single(timeout=1.0)
        rows.append({
            "rpm": float(rpm),
            "torque_percent": None if not pkt else pkt.get("torque_percent"),
            "torque_valid": None if not pkt else pkt.get("torque_valid"),
            "temperature_c": None if not pkt else pkt.get("temperature_c"),
            "temp_valid":    None if not pkt else pkt.get("temp_valid"),
            "viscosity_cp":  None if not pkt else pkt.get("viscosity_cp"),
            "status":        None if not pkt else pkt.get("status"),
            "record":        None if not pkt else pkt.get("record_number"),
        })
        client.stop()
        time.sleep(INTER_PAUSE_SEC)

    with out.open("w", newline="", encoding="utf-8") as f:   # Write CSV 
        w = csv.DictWriter(f, fieldnames=[
            "rpm","torque_percent","torque_valid",
            "temperature_c","temp_valid","viscosity_cp","status","record"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return str(out)