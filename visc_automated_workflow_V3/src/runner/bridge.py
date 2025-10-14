import pathlib
from hardware.viscometer.client import ViscometerClient

def create_client(cfg: dict) -> ViscometerClient:
    """Instantiate the 32-bit worker client using config."""
    py32 = cfg['python32']
    # locate worker.py relative to this file
    worker_path = pathlib.Path(__file__).resolve().parents[2] / 'src' / 'hardware' / 'viscometer' / 'worker.py'
    return ViscometerClient(py32, worker_path)