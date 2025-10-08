import serial, time, math, yaml

class CNC_Machine:
    BAUD_RATE = 115200
    SERIAL_PORT = "COM5"
    X_LOW_BOUND = 0;   X_HIGH_BOUND = 400
    Y_LOW_BOUND = 0;   Y_HIGH_BOUND = 400
    Z_LOW_BOUND = -75; Z_HIGH_BOUND = 0

    LOCATION_FILE = "config/locations.yaml"

    def __init__(self, virtual: bool = False):
        self.VIRTUAL = virtual
        with open(self.LOCATION_FILE, "r") as f:
            self.LOCATIONS = yaml.safe_load(f) or {}
        print(f"Connected to CNC Machine! (virtual={self.VIRTUAL})")

    # serial helpers
    def _wake(self, ser):
        ser.write(str.encode("\r\n\r\n"))
        time.sleep(1)
        ser.reset_input_buffer()

    def _wait_idle(self, ser):
        time.sleep(0.25)
        while True:
            ser.reset_input_buffer()
            ser.write(b"?\n")
            line = ser.readline().decode(errors="ignore").strip()
            if "Idle" in line:
                break
            time.sleep(0.1)

    # motion builders
    def _within(self, x, y, z) -> bool:
        xb = (x is None) or (self.X_LOW_BOUND <= x <= self.X_HIGH_BOUND)
        yb = (y is None) or (self.Y_LOW_BOUND <= y <= self.Y_HIGH_BOUND)
        zb = (z is None) or (self.Z_LOW_BOUND <= z <= self.Z_HIGH_BOUND)
        return xb and yb and zb

    def _gcode_to(self, x=None, y=None, z=None, speed=3000, gtype="G1"):
        s = gtype
        if x is not None: s += f" X{x}"
        if y is not None: s += f" Y{y}"
        if z is not None: s += f" Z{z}"
        if speed is not None: s += f" F{speed}"
        return s + "\n"

    # public ops
    def home(self):
        self.move_to_point_safe(0, 0, 0, gtype="G0")

    def move_to_point(self, x=None, y=None, z=None, speed=3000, gtype="G1"):
        if not self._within(x, y, z):
            print(f"Out of bounds: ({x},{y},{z})"); return
        g = self._gcode_to(x, y, z, speed, gtype)
        self.follow_gcode_path(g)

    def move_to_point_safe(self, x, y, z, speed=3000, gtype="G1"):
        if not self._within(x, y, z):
            print(f"Out of bounds: ({x},{y},{z})"); return
        g = ""
        g += self._gcode_to(z=self.Z_HIGH_BOUND, speed=speed, gtype=gtype)
        g += self._gcode_to(x=x, y=y, z=self.Z_HIGH_BOUND, speed=speed, gtype=gtype)
        g += self._gcode_to(z=z, speed=speed, gtype=gtype)
        self.follow_gcode_path(g)

    def get_location_position(self, name: str, idx: int):
        L = self.LOCATIONS[name]
        x = L["x_origin"]; y = L["y_origin"]; z = L["z_origin"]
        if idx > 0:
            num_x = L.get("num_x", 1); num_y = L.get("num_y", 1)
            x_off = L.get("x_offset", 0); y_off = L.get("y_offset", 0)
            x = x + (idx % num_x) * x_off
            y = y + (idx // num_x) * y_off
        return x, y, z

    def move_to_location(self, name: str, idx: int, safe: bool = True, speed: int = 3000):
        print(f"Moving to location: {name}[{idx}]")
        x, y, z = self.get_location_position(name, idx)
        if safe: self.move_to_point_safe(x, y, z, speed=speed)
        else:    self.move_to_point(x, y, z, speed=speed)

    def follow_gcode_path(self, gcode: str, buffer: int = 20):
        if self.VIRTUAL:
            print("VIRTUAL GCODE:\n" + gcode.strip())
            return ["ok"]
        outs = []
        with serial.Serial(self.SERIAL_PORT, self.BAUD_RATE) as ser:
            self._wake(ser)
            cmds = gcode.splitlines()
            for i in range(0, len(cmds), buffer):
                chunk = "\n".join(cmds[i:i+buffer]) + "\n"
                ser.write(chunk.encode())
                self._wait_idle(ser)
                out = ser.readline().decode(errors="ignore").strip()
                outs.append(out)
                print(f"Movement commands rendered: {min(i+buffer, len(cmds))}")
        return outs
