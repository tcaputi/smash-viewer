import ctypes
import time
import tkinter
import math
from pathlib import Path

"""
/* GCAPI Report Type
*  This data structure is intended to inform the plugin or the application
*  about the current state of the device input and output ports, about
*  parameters set by the console (LED, rumble, battery) and, as well as,
*  about the current values of the buttons, sticks and sensors.
*
*  Read-only data structure.
*/
typedef struct {
    uint8_t console;             // Receives values established by the #defines CONSOLE_*
    uint8_t controller;          // Values from #defines CONTROLLER_* and EXTENSION_*
    uint8_t led[4];              // Four LED - #defines LED_*
    uint8_t rumble[2];           // Two rumbles - Range: [0 ~ 100] %
    uint8_t battery_level;       // Battery level - Range: [0 ~ 10] 0 = empty, 10 = full
    struct {
        int8_t value;            // Current value - Range: [-100 ~ 100] %
        int8_t prev_value;       // Previous value - Range: [-100 ~ 100] %
        uint32_t press_tv;       // Time marker for the button press event
    } input[GCAPI_INPUT_TOTAL];  // Input structure (for controller entries)
} GCAPI_REPORT;
"""
class GCAPI_Input(ctypes.Structure):
    _fields_ = [
        ("value",               ctypes.c_int8),
        ("prev_value",          ctypes.c_int8),
        ("press_tv",            ctypes.c_uint32),
    ]


class GCAPI_Report(ctypes.Structure):
    _fields_ = [
        ("console",             ctypes.c_uint8),
        ("controller",          ctypes.c_uint8),
        ("led",                 ctypes.c_uint8 * 4),
        ("rumble",              ctypes.c_uint8 * 2),
        ("battery_level",       ctypes.c_uint8),
        ("input",       GCAPI_Input * 30),
    ]


class ControllerState:
    def __init__(self):
        self.buttons = []
        self.lx = 0
        self.ly = 0
        self.rx = 0
        self.ry = 0

    def add_button(self, button):
        self.buttons.append(button)

    def set_left_stick(self, x, y):
        self.lx = x
        self.ly = y

    def set_right_stick(self, x, y):
        self.rx = x
        self.ry = y


class Controller:
    def __init__(self, dll_path):
        self.dll_path = dll_path
        self.dll = ctypes.WinDLL(dll_path)

        gcdapi_unload = self.dll.gcdapi_Unload
        gcdapi_unload.restype = None
        gcdapi_unload.argtypes = []
        setattr(self, "gcdapi_unload", gcdapi_unload)

        gcdapi_load = self.dll.gcdapi_Load
        gcdapi_load.restype = ctypes.c_uint8
        gcdapi_load.argtypes = []
        setattr(self, "gcdapi_load", gcdapi_load)

        gcapi_is_connected = self.dll.gcapi_IsConnected
        gcapi_is_connected.restype = ctypes.c_uint8
        gcapi_is_connected.argtypes = []
        setattr(self, "gcapi_is_connected", gcapi_is_connected)

        gcapi_get_fwver = self.dll.gcapi_GetFWVer
        gcapi_get_fwver.restype = ctypes.c_uint16
        gcapi_get_fwver.argtypes = []
        setattr(self, "gcapi_get_fwver", gcapi_get_fwver)

        gcapi_read = self.dll.gcapi_Read
        gcapi_read.restype = ctypes.c_uint8
        gcapi_read.argtypes = [ctypes.POINTER(GCAPI_Report)]
        setattr(self, "gcapi_read", gcapi_read)

        self.gcdapi_load()
        time.sleep(1)

    def __del__(self):
        self.gcdapi_unload()

    def __dump(self, indent_lvl, name, val):
        indent = "    " * indent_lvl

        if isinstance(val, ctypes.Array):
            print(f"{indent}{name}")
            for i, arr_val in enumerate(val):
                self.__dump(indent_lvl + 1, f"{i}", arr_val)

        elif isinstance(val, ctypes.Structure):
            print(f"{indent}{name}")
            for field_name, _ in val._fields_:
                self.__dump(indent_lvl + 1, field_name, getattr(val, field_name))
        else:
            print(f"{indent}{name}: {val}")

    def dump(self, name, val):
        print()
        self.__dump(0, name, val)
        print()

    def input_idx_to_name(self, idx):
        if idx == 0:        return "home"
        if idx == 1:        return "minus"
        if idx == 2:        return "plus"
        if idx == 3:        return "R"
        if idx == 4:        return "ZR"
        if idx == 5:        return "SR"
        if idx == 6:        return "L"
        if idx == 7:        return "ZL"
        if idx == 8:        return "SL"
        if idx == 9:        return "RX"
        if idx == 10:       return "RY"
        if idx == 11:       return "LX"
        if idx == 12:       return "LY"
        if idx == 13:       return "up"
        if idx == 14:       return "down"
        if idx == 15:       return "left"
        if idx == 16:       return "right"
        if idx == 17:       return "X"
        if idx == 18:       return "A"
        if idx == 19:       return "B"
        if idx == 20:       return "Y"
        if idx == 21:       return "accx"
        if idx == 22:       return "accy"
        if idx == 23:       return "accz"
        if idx == 24:       return "gyrox"
        if idx == 25:       return "gyroy"
        if idx == 26:       return "gyroz"
        if idx == 27:       return "screenshot"
        return None

    def input_is_button(self, input_name):
        if input_name == "RX":          return False
        if input_name == "RY":          return False
        if input_name == "LX":          return False
        if input_name == "LY":          return False
        if input_name == "accx":        return False
        if input_name == "accy":        return False
        if input_name == "accz":        return False
        if input_name == "gyrox":       return False
        if input_name == "gyroy":       return False
        if input_name == "gyroz":       return False
        return True

    def read_state(self):
        state = ControllerState()
        report = GCAPI_Report()
        self.gcapi_read(ctypes.byref(report))

        for i, input in enumerate(report.input):
            input_name = self.input_idx_to_name(i)
            if input_name is None:
                break

            if self.input_is_button(input_name) and input.value != 0:
                state.add_button(input_name)

        state.set_left_stick(report.input[12].value, report.input[11].value)
        state.set_right_stick(report.input[10].value, report.input[9].value)

        return state

    def is_connected(self):
        return self.gcapi_is_connected()

    def get_fwver(self):
        return self.gcapi_get_fwver()


class ControllerGUI:
    def __init__(self, controller, overlay_dir):
        self.controller = controller
        self.tk = tkinter.Tk()
        self.tk.title("Pro Controller Input Viewer")
        self.base_img = tkinter.PhotoImage(file=overlay_dir / "none.png")
        self.canvas_height = self.base_img.height() + 40
        self.canvas_width = self.base_img.width() + 40
        self.lx_origin = 102
        self.ly_origin = 100
        self.rx_origin = 264
        self.ry_origin = 157
        self.analog_radius = 30
        self.stick_icon_radius = 20
        self.canvas = tkinter.Canvas(self.tk, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.canvas.create_image((self.canvas_width / 2, self.canvas_height / 2), image=self.base_img, anchor=tkinter.CENTER)

        self.button_overlays = {
            "L":            tkinter.PhotoImage(file=overlay_dir / "L.png"),
            "ZL":           tkinter.PhotoImage(file=overlay_dir / "ZL.png"),
            "SL":           tkinter.PhotoImage(file=overlay_dir / "SL.png"),
            "R":            tkinter.PhotoImage(file=overlay_dir / "R.png"),
            "ZR":           tkinter.PhotoImage(file=overlay_dir / "ZR.png"),
            "SR":           tkinter.PhotoImage(file=overlay_dir / "SR.png"),
            "A":            tkinter.PhotoImage(file=overlay_dir / "A.png"),
            "B":            tkinter.PhotoImage(file=overlay_dir / "B.png"),
            "X":            tkinter.PhotoImage(file=overlay_dir / "X.png"),
            "Y":            tkinter.PhotoImage(file=overlay_dir / "Y.png"),
            "up":           tkinter.PhotoImage(file=overlay_dir / "up.png"),
            "down":         tkinter.PhotoImage(file=overlay_dir / "down.png"),
            "left":         tkinter.PhotoImage(file=overlay_dir / "left.png"),
            "right":        tkinter.PhotoImage(file=overlay_dir / "right.png"),
            "plus":         tkinter.PhotoImage(file=overlay_dir / "plus.png"),
            "minus":        tkinter.PhotoImage(file=overlay_dir / "minus.png"),
            "home":         tkinter.PhotoImage(file=overlay_dir / "home.png"),
            "screenshot":   tkinter.PhotoImage(file=overlay_dir / "screenshot.png"),
        }

        def on_update():
            state = self.controller.read_state()
            self.update(state)
            self.tk.after(16, on_update)

        on_update()
        self.tk.mainloop()

    def get_stick_position(self, x_origin, y_origin, max_radius, stick_x, stick_y):
        max_raw_radius = 100.0

        if stick_x == 0 and stick_y == 0:
            return x_origin, y_origin

        raw_radius = math.sqrt(float(stick_x) * float(stick_x) + float(stick_y) * float(stick_y))
        if raw_radius > max_raw_radius:
            raw_radius = max_raw_radius

        radius = raw_radius * float(max_radius) / max_raw_radius

        angle = math.atan2(float(stick_y), float(stick_x))
        x = x_origin + radius * math.sin(angle)
        y = y_origin + radius * math.cos(angle)

        return x, y

    def update(self, state):
        self.canvas.delete(tkinter.ALL)
        self.canvas.create_image((self.canvas_width / 2, self.canvas_height / 2), image=self.base_img, anchor=tkinter.CENTER)

        for button_name in state.buttons:
            button_img = self.button_overlays[button_name]
            self.canvas.create_image((self.canvas_width / 2, self.canvas_height / 2), image=button_img, anchor=tkinter.CENTER)

        lx, ly = self.get_stick_position(self.lx_origin, self.ly_origin, self.analog_radius, state.lx, state.ly)
        lx1 = lx - self.stick_icon_radius / 2
        ly1 = ly - self.stick_icon_radius / 2
        lx2 = lx + self.stick_icon_radius / 2
        ly2 = ly + self.stick_icon_radius / 2
        self.canvas.create_oval(lx1, ly1, lx2, ly2, fill="blue")

        rx, ry = self.get_stick_position(self.rx_origin, self.ry_origin, self.analog_radius, state.rx, state.ry)
        rx1 = rx - self.stick_icon_radius / 2
        ry1 = ry - self.stick_icon_radius / 2
        rx2 = rx + self.stick_icon_radius / 2
        ry2 = ry + self.stick_icon_radius / 2
        self.canvas.create_oval(rx1, ry1, rx2, ry2, fill="blue")


def main():
    controller = Controller("C:\\Development\\projects\\smash-viewer\\gcdapi.dll")
    gui = ControllerGUI(controller, Path("C:\\Development\\projects\\smash-viewer\\images\\"))


if __name__ == "__main__":
    main()
