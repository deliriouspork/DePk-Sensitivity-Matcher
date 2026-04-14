import evdev, time
from evdev import InputDevice, ecodes, UInput
import selectors
from PyQt6 import QtCore

class GlobalHotkeyWorker(QtCore.QThread):
    hotkey_triggered = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        # Define a virtual mouse that can move relatively (REL_X)
        capabilities = {
            ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y]
        }
        self.vmouse = UInput(capabilities, name="Sensitivity-Matcher-Virtual-Mouse")

    def move_mouse_relative(self, total_x, speed_multiplier):
        # Base step size is 100 pixels multiply by speed.
        step_size = 100 * speed_multiplier

        # Determine direction
        direction = 1 if total_x > 0 else -1
        remaining = abs(total_x)

        while remaining > 0:
            move = min(step_size, remaining)
            self.vmouse.write(ecodes.EV_REL, ecodes.REL_X, int(move * direction))
            self.vmouse.syn()
            remaining -= move
            time.sleep(0.001)

    def run(self):
        devices = [InputDevice(path) for path in evdev.list_devices()]
        selector = selectors.DefaultSelector()
        
        for dev in devices:
            if ecodes.EV_KEY in dev.capabilities():
                selector.register(dev, selectors.EVENT_READ)

        active_keys = set()
        print(f"Hotkey listener started on {len(devices)} devices.")

        try:
            while True:
                for key, mask in selector.select():
                    device = key.fileobj
                    try:
                        for event in device.read():
                            if event.type == ecodes.EV_KEY:
                                if event.value == 1: # Down
                                    active_keys.add(event.code)
                                elif event.value == 0: # Up
                                    active_keys.discard(event.code)

                                # Alt + Backspace logic
                                if event.code == ecodes.KEY_BACKSPACE and event.value == 1:
                                    if ecodes.KEY_LEFTALT in active_keys or ecodes.KEY_RIGHTALT in active_keys:
                                        self.hotkey_triggered.emit()
                    except (OSError, RuntimeError):
                        selector.unregister(device)
        except Exception as e:
            print(f"Error in hotkey thread: {e}")