import evdev
from evdev import InputDevice, ecodes, UInput
import time
import selectors
from PyQt6 import QtCore

class GlobalHotkeyWorker(QtCore.QThread):
    hotkey_triggered = QtCore.pyqtSignal()
    init_failed = QtCore.pyqtSignal(str)
    runtime_error = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = True
        self.vmouse = None
        # Define a virtual mouse that can move relatively (REL_X)
        # and has a left click (BTN_LEFT) DONT REMOVE THAT SHIT FOR SOME FUCKING REASON IT BREAKS EVEN THOUGH ITS NOT FUCKIN USED AT ALL
        try:
            capabilities = {
                ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y],
                ecodes.EV_KEY: [ecodes.BTN_LEFT]
            }
            self.vmouse = UInput(capabilities, name="Sensitivity-Matcher-Virtual-Mouse")
        except PermissionError:
            self.init_failed.emit("Permission denied creating virtual mouse.\n\nMake sure you're running with input group access:\n\nsudo -E -g input bash")
        except Exception as e:
            self.init_failed.emit(f"Failed to initialise virtual mouse:\n\n{e}")

    def move_mouse_relative(self, total_x, speed_multiplier):
        if self.vmouse is None:
            return
        step_size = 100 * speed_multiplier
        direction = 1 if total_x > 0 else -1
        remaining = abs(total_x)
        while remaining > 0:
            move = min(step_size, remaining)
            self.vmouse.write(ecodes.EV_REL, ecodes.REL_X, int(move * direction))
            self.vmouse.syn()
            remaining -= move
            time.sleep(0.001)

    def stop(self):
        self._running = False

    def run(self):
        devices = [InputDevice(path) for path in evdev.list_devices()]
        selector = selectors.DefaultSelector() 
        for dev in devices:
            if ecodes.EV_KEY in dev.capabilities():
                selector.register(dev, selectors.EVENT_READ)
        active_keys = set()
        try:
            while self._running:
                for key, mask in selector.select(timeout=1):
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
            self.runtime_error.emit(f"Hotkey listener crashed:\n\n{e}")
        finally:
            if self.vmouse is not None:
                self.vmouse.close()