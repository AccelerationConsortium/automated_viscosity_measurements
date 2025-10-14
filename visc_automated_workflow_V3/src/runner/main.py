# Runner entrypoint: load config, wire up hardware, motion, and analysis.

import pathlib, yaml, time, sys
# Add project `src` directory to Python path
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from hardware.cnc.controller import CNC_Machine
from hardware.pump.esp32 import PumpESP32
from motion.sample_handler import go_to_sample
from motion.wash_sequence import wash1, wash2, wash3
from analysis.single import run_single_rpm
from analysis.dynamic import run_dynamic_analysis
from analysis.bisection import run_bisection
from runner.bridge import create_client

# Load config
def load_config():
    root = pathlib.Path(__file__).resolve().parents[2]
    cfg_file = root / 'config' / 'default.yaml'
    with cfg_file.open('r') as f:
        return yaml.safe_load(f)

# Paths
def _results_dir(root):
    d = root / 'results'
    d.mkdir(parents=True, exist_ok=True)
    return d

# Main
def main():
    cfg = load_config()
    root = pathlib.Path(__file__).resolve().parents[2]
    results_root = _results_dir(root)
    # Instantiate CNC with serial port, baud, and locations grid from config
    loc_file = root / cfg['location_file']
    cnc = CNC_Machine(
        port=cfg['cnc_port'],
        baud=cfg['cnc_baud'],
        location_file=str(loc_file),
        virtual=False
    )
    cnc.home()
    time.sleep(cfg['pause_after_home'])

    pump = None
    if cfg['enable_wash']:
        pump = PumpESP32(port=cfg['esp32_port'], baud=cfg['esp32_baud'], virtual=cfg['pump_virtual'])
        pump.open()

    client = create_client(cfg)
    client.init(port=cfg['visco_port'], baud=cfg['visco_baud'], timeout=cfg['visco_timeout'], spindle_k=cfg['spindle_k'])

    for i in cfg['sample_range']:
        sample_dir = results_root / f"sample_{i:03d}"
        sample_dir.mkdir(parents=True, exist_ok=True)
        go_to_sample(cnc, rack=cfg['sample_rack'], idx=i, safe=True, wait_s=0)
        time.sleep(cfg['pause_after_move'])

        mode = cfg['analysis_mode']
        if mode == 'single':
            path = run_single_rpm(sample_dir, client)
        elif mode == 'dynamic':
            path = run_dynamic_analysis(sample_dir, client)
        elif mode == 'bisection':
            path = run_bisection(sample_dir, client)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        print(f"[sample {i}] results -> {path}")

        if cfg['enable_wash'] and pump:
            # run wash sequence using pump
            wash1(cnc, pump)
            wash2(cnc, pump)
            wash3(cnc, pump)

    cnc.home()
    client.stop()
    client.close()
    if pump:
        pump.close()

if __name__ == '__main__':
    main()
