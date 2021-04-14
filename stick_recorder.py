import sys
import time
from pathlib import Path

from controller import Controller

FRAME_DELAY_MS = 1

def main():
    output_dir = Path(sys.argv[1])
    record_secs = float(sys.argv[2])
    stick_data = {
        "lx" : [],
        "ly" : [],
        "rx" : [],
        "ry" : [],
    }

    controller = Controller("C:\\Development\\projects\\smash-viewer\\gcdapi.dll")

    next_frame_time = time.time()
    end_time = next_frame_time + record_secs

    while next_frame_time < end_time:
        next_frame_time += float(FRAME_DELAY_MS) / 1000
        state = controller.read_state()
        stick_data["lx"].append(state.lx + 100)
        stick_data["ly"].append(state.ly + 100)
        stick_data["rx"].append(state.rx + 100)
        stick_data["ry"].append(state.ry + 100)
        time.sleep(max(0, next_frame_time - time.time()))

    output_dir.mkdir(exist_ok=True)

    for channel_name in stick_data:
        path = output_dir / channel_name

        with open(path, "wb") as out_file:
            data = bytes(stick_data[channel_name])
            out_file.write(data)

if __name__ == "__main__":
    main()
