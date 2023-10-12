import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from main import UI  # Import your UI class from main.py

# Directory to save screenshots
screenshot_directory = "screenshots"
if not os.path.exists(screenshot_directory):
    os.mkdir(screenshot_directory)

# Function to capture and save a screenshot
screenshot_counter = 0


def capture_screenshot(window):
    global screenshot_counter
    screenshot_name = f"screenshot_{screenshot_counter}.png"
    screenshot_path = os.path.join(screenshot_directory, screenshot_name)
    window.grab().save(screenshot_path, "png")
    screenshot_counter += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = UI()
    main_window.show()

    # Capture a screenshot of the initial window
    initial_screenshot_name = "initial_screenshot.png"
    capture_screenshot(main_window)
    screenshot_counter += 1

    # Set up a timer to capture screenshots every 3 seconds
    timer = QTimer()
    timer.timeout.connect(lambda: capture_screenshot(main_window))
    timer.start(5000)  # 3000 milliseconds = 3 seconds

    app.exec_()
