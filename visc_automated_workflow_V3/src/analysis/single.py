import csv, time, pathlib
from hardware.viscometer.client import ViscometerClient

def run_single_rpm(results_dir: pathlib.Path, client: ViscometerClient):
    RPM                = 32
    TOTAL_SECONDS      = 180
    SAMPLE_EVERY_SEC   = 1
    SETTLE_SECONDS     = 1.0
    CSV_NAME           = f"single_rpm_{RPM:.2f}.csv"

    out = results_dir / CSV_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    client.set_speed(RPM)
    time.sleep(SETTLE_SECONDS)
    t0 = time.time()
    next_t = t0 + SAMPLE_EVERY_SEC
    rows = []

    while True:
        now = time.time()
        if now - t0 >= TOTAL_SECONDS:
            break
        if now >= next_t:
            pkt = client.read_single(timeout=1.0)  
            if pkt:
                rows.append({
                    "t_elapsed_s": round(now - t0, 2),
                    "rpm": RPM,
                    "torque_percent": pkt.get("torque_percent"),
                    "torque_valid": pkt.get("torque_valid"),
                    "temperature_c": pkt.get("temperature_c"),
                    "temp_valid": pkt.get("temp_valid"),
                    "viscosity_cp": pkt.get("viscosity_cp"),
                    "status": pkt.get("status"),
                    "record": pkt.get("record_number"),
                })
            next_t += SAMPLE_EVERY_SEC
        else:
            time.sleep(0.05)

    client.stop()
    with out.open("w", newline="", encoding="utf-8") as f: # Write CSV
        w = csv.DictWriter(f, fieldnames=[
            "t_elapsed_s","rpm","torque_percent","torque_valid",
            "temperature_c","temp_valid","viscosity_cp","status","record"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return str(out)