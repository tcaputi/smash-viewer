import tkinter
import math
from pathlib import Path

from controller import Controller

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
            self.tk.after(4, on_update)

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
        x = x_origin + radius * math.cos(angle)
        y = y_origin + radius * math.sin(angle)

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
