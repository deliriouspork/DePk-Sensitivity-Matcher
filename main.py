import sys, os
from PyQt6 import QtWidgets, uic
from hotkeys import GlobalHotkeyWorker # import class from hotkeys.py

''' Pyinstaller shit '''
def resource_path(relative_path):
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

def on_yaw_change():
	if window.presetYaw.currentText() == 'Quake/Source':
		window.yaw.setText("0.022")
	elif window.presetYaw.currentText() == 'Overwatch/Valorant':
		window.yaw.setText("0.0066")
	elif window.presetYaw.currentText() == 'Rainbow Six Siege':
		window.yaw.setText("0.002230")



def on_sens_change():
	try:
		yaw = float(window.yaw.text())
		sens = float(window.sens.text())
		increment = yaw * sens

		formatted_inc = f"{increment:.10f}".rstrip('0').rstrip('.')
		window.increment.setText(formatted_inc)

	except ValueError:
		print("Check your Yaw/Sens fields - they must be numbers!")



def handle_hotkey():
	print(">>> Performing 360 Turn <<<")

	try:
		yaw = float(window.yaw.text())
		sens = float(window.sens.text())
		speed_mult = float(window.speed.text())

		# Calculate total counts (pixels/dots) needed for a full circle
		total_counts = 360 / (yaw * sens)

		# Move the virtual mouse
		worker.move_mouse_relative(total_counts, speed_mult)
	
	except ValueError:
		print("Check your Yaw/Sens fields - they must be numbers!")



def mousePressEvent(event):
    # Check if the click is on the background, not on a child widget
    focused_widget = window.focusWidget()
    if isinstance(focused_widget, QtWidgets.QLineEdit):
        focused_widget.clearFocus()



app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi(resource_path("mainwindow.ui")) # pyinstaller fix

# Setup Hotkey Worker
worker = GlobalHotkeyWorker()
worker.hotkey_triggered.connect(handle_hotkey)
worker.start()

# UI Connections
window.presetYaw.currentTextChanged.connect(on_yaw_change)
window.sens.textChanged.connect(on_sens_change) 
window.yaw.textChanged.connect(on_sens_change)

window.show()
window.mousePressEvent = mousePressEvent

sys.exit(app.exec())