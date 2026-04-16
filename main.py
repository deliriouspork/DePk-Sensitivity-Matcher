import sys
import os
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
    "Quake/Source": "0.022",
    "Overwatch/Valorant": "0.0066",
    "Rainbow Six Siege": "0.002230",
}

class SensitivityMatcher:
	def __init__(self):
		self.app = QtWidgets.QApplication(sys.argv)
		self.window = uic.loadUi(resource_path("mainwindow.ui")) # pyinstaller fix
		self.worker = GlobalHotkeyWorker()
		self.worker.start()
		self.window.mousePressEvent = self._mouse_press_event
		self._connect_signals()

	def _mouse_press_event(self, event):
		focused_widget = self.window.focusWidget()
		if isinstance(focused_widget, QtWidgets.QLineEdit):
			focused_widget.clearFocus()

	def _connect_signals(self):
		self.worker.hotkey_triggered.connect(self._handle_hotkey)
		self.window.presetYaw.currentTextChanged.connect(self._on_yaw_change)
		self.window.sens.textChanged.connect(self._on_sens_change) 
		self.window.yaw.textChanged.connect(self._on_sens_change)
		self.app.aboutToQuit.connect(self._on_quit)

	def _handle_hotkey(self):
		print(">>> Performing 360 Turn <<<")
		try:
			yaw, sens = self._get_yaw_sens()
			speed_mult = float(self.window.speed.text())
			total_counts = 360 / (yaw * sens)
			self.worker.move_mouse_relative(total_counts, speed_mult)
		except ValueError:
			print("Check your Yaw/Sens fields - they must be numbers!")

	def _on_yaw_change(self):
		preset = self.window.presetYaw.currentText()
		if preset in YAW_PRESETS:
			self.window.yaw.setText(YAW_PRESETS[preset])

	def _on_sens_change(self):
		try:
			yaw, sens = self._get_yaw_sens()
			increment = yaw * sens
			formatted_inc = f"{increment:.10f}".rstrip('0').rstrip('.')
			self.window.increment.setText(formatted_inc)
		except ValueError:
			print("Check your Yaw/Sens fields - they must be numbers!")

	def _get_yaw_sens(self):
		return float(self.window.yaw.text()), float(self.window.sens.text())

	def _on_quit(self):
		print("Closing application...")
		self.worker.stop()
		self.worker.wait()

	def run(self):
		self.window.show()
		return self.app.exec()

if __name__ == "__main__":
	sys.exit(SensitivityMatcher().run())