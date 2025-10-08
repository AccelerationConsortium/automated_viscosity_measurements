# src/python_64/main.py
import pathlib
import time
from cnc_controller import CNC_Machine
from move_to_locations import PumpESP32, go_to_sample, wash1, wash2, wash3
from viscometer_client import ViscometerClient
from analysis_methods import run_single_rpm, run_dynamic_analysis, run_bisection

# Paths & device settings 
PYTHON32    = ".\\.venv32\\Scripts\\python.exe"  
VISCO_PORT  = "COM6"
VISCO_BAUD  = 115200
VISCO_TOUT  = 1.0
SPINDLE_K   = 992.47
ANALYSIS_MODE = "single"  # "single" | "dynamic" | "bisection"
SAMPLE_RACK  = "main_rack_A"
SAMPLE_RANGE = range(0, 1)     
# Wash / Pump settings # ENABLE_WASH  = False # ESP32_PORT = "COM4"  #ESP32_BAUD = 9600#PUMP_VIRTUAL = True             
PAUSE_AFTER_HOME = 0.2
PAUSE_AFTER_MOVE = 0.1

def _root_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]

def _worker_path() -> pathlib.Path:
    return _root_dir() / "src" / "python_32" / "worker32.py"

def _results_dir() -> pathlib.Path:
    d = _root_dir() / "results"
    d.mkdir(parents=True, exist_ok=True)
    return d

def main():
    root = _root_dir()
    results_root = _results_dir()
    worker = _worker_path()
    
    cnc = CNC_Machine(virtual=False)
    cnc.home()
    time.sleep(PAUSE_AFTER_HOME)
    #pump = None
    #if ENABLE_WASH:
     #   pump = PumpESP32(port=ESP32_PORT, baud=ESP32_BAUD, virtual=PUMP_VIRTUAL)
      #  pump.open()

    client = ViscometerClient(PYTHON32, worker)
    try:
        client.init(port=VISCO_PORT, baud=VISCO_BAUD, timeout=VISCO_TOUT, spindle_k=SPINDLE_K)

        for i in SAMPLE_RANGE:
            sample_dir = results_root / f"sample_{i:03d}"
            sample_dir.mkdir(parents=True, exist_ok=True)
            go_to_sample(cnc, rack=SAMPLE_RACK, idx=i, safe=True, wait_s=0)
            time.sleep(PAUSE_AFTER_MOVE)

            # Run the chosen viscometer analysis 
            if ANALYSIS_MODE == "single":
                csv_path = run_single_rpm(sample_dir, client)
            elif ANALYSIS_MODE == "dynamic":
                csv_path = run_dynamic_analysis(sample_dir, client)
            elif ANALYSIS_MODE == "bisection":
                csv_path = run_bisection(sample_dir, client)
            else:
                raise ValueError(f"Unknown ANALYSIS_MODE: {ANALYSIS_MODE}")
            print(f"[sample {i}] results -> {csv_path}")

            #wash sequence between samples 
           # if ENABLE_WASH and pump is not None:
            #  wash1(cnc, pump)# wash2(cnc, pump) # wash3(cnc, pump)
        cnc.home()

    finally:
        try:
            client.stop()
        except Exception:
            pass
        client.close()
        # Close pump if used
       # if pump is not None:
       #     try:
       #         pump.close()
        #    except Exception:
       #         pass

if __name__ == "__main__":
    main()
