# JSON-lines worker for the 32-bit viscometer side
import sys, json, traceback, time
from typing import Optional, Dict, Any

from .protocol import ViscometerProtocol

PROTO_VERSION = "1.0"

class DeviceState:
    def __init__(self):
        self.dev: Optional[ViscometerProtocol] = None
        self.opened: bool = False
        self.current_rpm: float = 0.0

STATE = DeviceState()

def ok(i, data=None, **extra):
    resp = {"id": i, "ok": True, "data": data or {}}
    if extra:
        resp.update(extra)
    return resp

def err(i, message):
    return {"id": i, "ok": False, "error": message}

def ensure_open():
    if not (STATE.dev and STATE.opened):
        raise RuntimeError("device not initialized; call 'init' first")

# Command handlers
# ... (rest of handlers copied from python_32/worker32.py, adjusting imports) ...

# Please refer to original worker32.py content