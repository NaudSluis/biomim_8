import json
import manual
from manual import start_manual_control

def move_to_home():
    # while home_x != pressed:
    #   left()
    # while home_y != pressed:
    #   down()
    return #this is place holder now to avoid error

def reset_manual_state():
    """Resets the step counters in the 'manual' module before starting."""
    #Move to home first
    move_to_home()

    manual.x_axis = 0
    manual.y_axis = 0

    manual.is_moving_forward = False
    manual.is_moving_down = False
    manual.is_moving_right = False
    manual.is_moving_left = False

def dump_to_json(x_axis, y_axis):
    coords = {"end position x":x_axis, "end position y":y_axis}

    with open('calibration_info.json', 'w') as fp:
        json.dump(coords, fp)

if __name__ == "__main__":
    reset_manual_state()
    start_manual_control()
    dump_to_json(manual.x_axis, manual.y_axis)