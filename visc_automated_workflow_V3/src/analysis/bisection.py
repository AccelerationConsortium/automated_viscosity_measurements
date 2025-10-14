import csv, time, pathlib
from hardware.viscometer.client import ViscometerClient

def run_bisection(results_dir: pathlib.Path, client: ViscometerClient):
    TARGET_TORQUE_PCT = 50.0    
    TOL_PCT           = 20.0    
    LOW_RPM           = 0.5
    HIGH_RPM          = 30
    MAX_ITERS         = 20
    SETTLE_SECONDS    = 60.0
    FINAL_HOLD_S      = 60.0     
    INTER_PAUSE_SEC   = 2.0     
    CSV_NAME          = "bisection_analysis.csv"

    out = results_dir / CSV_NAME
    out.parent.mkdir(parents=True, exist_ok=True)

    history = []
    lo, hi = float(LOW_RPM), float(HIGH_RPM)
    best_rpm, best_err = None, float("inf")

    for _ in range(MAX_ITERS):
        mid = (lo + hi) / 2.0
        client.set_speed(mid)
        time.sleep(SETTLE_SECONDS)
        pkt = client.read_single(timeout=1.0)
        client.stop()
        time.sleep(INTER_PAUSE_SEC)

        if not pkt or not pkt.get("torque_valid"):
            # treat as unusable datapoint; shrink range slightly around mid and continue
            lo = max(0.1, mid * 0.9)
            hi = min(200.0, mid * 1.1)
            continue

        tq = float(pkt["torque_percent"])
        err = abs(tq - TARGET_TORQUE_PCT)
        history.append({"rpm": mid, "torque_percent": tq, "viscosity_cp": pkt.get("viscosity_cp")})

        if err < best_err:
            best_err, best_rpm = err, mid
        if err <= TOL_PCT:
            break
        if tq < TARGET_TORQUE_PCT:
            lo = mid
        else:
            hi = mid

    # Final hold at best_rpm (if none, fall back to mid of last range)
    final_rpm = best_rpm if best_rpm is not None else (lo + hi) / 2.0
    client.set_speed(final_rpm)
    time.sleep(FINAL_HOLD_S)
    final_pkt = client.read_single(timeout=1.0)
    client.stop()

    # write CSV
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# Target torque (%)", TARGET_TORQUE_PCT])
        w.writerow(["# Tolerance (%)", TOL_PCT])
        w.writerow(["# Final RPM", round(final_rpm, 3)])
        w.writerow([])
        w.writerow(["RPM", "Torque (%)", "Viscosity (cP)"])
        for h in history:
            w.writerow([round(h["rpm"], 3), h["torque_percent"], h["viscosity_cp"]])
        w.writerow([])
        w.writerow(["FINAL_RPM", round(final_rpm, 3)])
        if final_pkt:
            w.writerow(["FINAL_TORQUE_%", final_pkt.get("torque_percent")])
            w.writerow(["FINAL_VISCOSITY_cP", final_pkt.get("viscosity_cp")])
    return str(out)