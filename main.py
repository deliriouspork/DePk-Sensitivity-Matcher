import sys
import os
import json
from PyQt6 import QtWidgets, uic
from hotkeys import GlobalHotkeyWorker # import class from hotkeys.py

''' Pyinstaller shit '''
def resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

YAW_PRESETS = {
    "Quake/Source/Apex": "0.022",
    "Overwatch/Valorant/CoD": "0.0066",
    "Rainbow Six Siege": "0.02",
	"Fortnite": "0.002201",
	"Battlefield/Frostbite": "0.002",
}

DEFAULTS = {
	"sens": "4.0",
	"yaw": "0.022",
	"speed": "1",
	"preset_index": 0
}

class SensitivityMatcher:
	def __init__(self):
		self.app = QtWidgets.QApplication(sys.argv)
		self.window = uic.loadUi(resource_path("mainwindow.ui")) # pyinstaller fix
		self.worker = GlobalHotkeyWorker()
		self.worker.init_failed.connect(lambda msg: self._show_error("Startup Error", msg))
		self.worker.runtime_error.connect(lambda msg: self._show_error("Runtime Error", msg))
		self.worker.start()
		self.settings_path = "settings.json"
		self._load_settings()
		self._update_increment()
		self.window.mousePressEvent = self._mouse_press_event
		self._connect_signals()

	def _load_settings(self):
		if os.path.exists(self.settings_path):
			try:
				with open(self.settings_path, "r") as f:
					data = json.load(f)
				self.window.sens.setText(data.get("sens", DEFAULTS["sens"]))
				self.window.yaw.setText(data.get("yaw", DEFAULTS["yaw"]))
				self.window.speed.setText(data.get("speed", DEFAULTS["speed"]))
				self.window.presetYaw.setCurrentIndex(data.get("preset_index", DEFAULTS["preset_index"]))
			except json.JSONDecodeError:
				self._show_warning("Settings Warning", "settings.json is corrupted. Loading defaults.")
				self._apply_defaults()
			except Exception as e:
				self._show_warning("Settings Warning", f"Could not load settings:\n\n{e}\n\nLoading defaults.")
				self._apply_defaults()
		else:
			self._apply_defaults()

	def _apply_defaults(self):
		self.window.sens.setText(DEFAULTS["sens"])
		self.window.yaw.setText(DEFAULTS["yaw"])
		self.window.speed.setText(DEFAULTS["speed"])
		self.window.presetYaw.setCurrentIndex(DEFAULTS["preset_index"])

	def _save_settings(self):
		data = {
            "sens": self.window.sens.text(),
            "yaw": self.window.yaw.text(),
            "speed": self.window.speed.text(),
            "preset_index": self.window.presetYaw.currentIndex()
        }
		try:
			with open(self.settings_path, "w") as f:
				json.dump(data, f, indent=4)
		except Exception as e:
			self._show_error("Save Error", f"Failed to save settings:\n\n{e}")

	def _mouse_press_event(self, event):
		focused_widget = self.window.focusWidget()
		if isinstance(focused_widget, QtWidgets.QLineEdit):
			focused_widget.clearFocus()

	def _connect_signals(self):
		self.worker.hotkey_triggered.connect(self._handle_hotkey)
		self.window.presetYaw.currentTextChanged.connect(self._on_yaw_preset_change)
		self.window.sens.textChanged.connect(self._update_increment) 
		self.window.yaw.textChanged.connect(self._on_yaw_changed)
		self.app.aboutToQuit.connect(self._on_quit)

	def _handle_hotkey(self):
		try:
			yaw, sens = self._get_yaw_sens()
			speed_mult = float(self.window.speed.text())
			total_counts = 360 / (yaw * sens)
			self.worker.move_mouse_relative(total_counts, speed_mult)
		except ValueError:
			self._show_error("Invalid Input", "Yaw, Sensitivity, and Speed must all be valid numbers.")
		except ZeroDivisionError:
			self._show_error("Invalid Input", "Yaw and Sensitivity cannot be zero.")

	def _on_yaw_preset_change(self):
		preset = self.window.presetYaw.currentText()
		if preset in YAW_PRESETS:
			self.window.yaw.setText(YAW_PRESETS[preset])

	def _check_if_preset(self):
		yaw = self.window.yaw.text()
		if yaw in YAW_PRESETS.values():
			preset_name = [name for name, val in YAW_PRESETS.items() if val == yaw][0]
			self.window.presetYaw.setCurrentText(preset_name)
		else:
			last_index = self.window.presetYaw.count() - 1
			self.window.presetYaw.setCurrentIndex(last_index)

	def _on_yaw_changed(self):
		self._update_increment()
		self._check_if_preset()

	def _update_increment(self):
		try:
			yaw, sens = self._get_yaw_sens()
			if yaw == 0 or sens == 0:
				raise ZeroDivisionError
			increment = yaw * sens
			formatted_inc = f"{increment:.10f}".rstrip('0').rstrip('.')
			self.window.increment.setText(formatted_inc)
		except (ValueError, ZeroDivisionError):
			self.window.increment.setText("?")

	def _get_yaw_sens(self):
		return float(self.window.yaw.text()), float(self.window.sens.text())

	def _show_error(self, title, message):
		QtWidgets.QMessageBox.critical(self.window, title, message)

	def _show_warning(self, title, message):
		QtWidgets.QMessageBox.warning(self.window, title, message)

	def _on_quit(self):
		self._save_settings()
		self.worker.stop()
		self.worker.wait()

	def run(self):
		self.window.show()
		return self.app.exec()

if __name__ == "__main__":
	sys.exit(SensitivityMatcher().run())