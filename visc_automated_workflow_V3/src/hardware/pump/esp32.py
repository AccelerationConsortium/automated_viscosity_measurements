import time
import serial
from serial import SerialException

ESP32_BOOT_DELAY_S = 1.5

class PumpESP32:
    def __init__(self, port: str, baud: int = 9600, virtual: bool = False):
        self.port = port
        self.baud = baud
        self.virtual = virtual
        self.ser: serial.Serial | None = None

    def open(self):
        if self.virtual:
            print(f"[PUMP VIRTUAL] open {self.port} @ {self.baud}")
            return
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(ESP32_BOOT_DELAY_S)
        except SerialException as e:
            print(f"[PUMP WARN] could not open {self.port}: {e}. Falling back to virtual.")
            self.virtual = True

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def send_tag(self, tag: bytes):
        if self.virtual:
            print(f"[PUMP VIRTUAL] tag -> {tag!r}")
            return
        self.ser.write(tag)
