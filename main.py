from datetime import datetime
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer
import csv


linebreak = f"<br>"  # global line break


class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi("boat.ui", self)
        self.layout = QVBoxLayout()  # Create a QVBoxLayout
        self.statistics = QTextEdit()  # Create a QTextEdit
        self.statistics.setReadOnly(True)  # Make it read-only
        self.layout.addWidget(self.statistics)  # Add the QTextEdit to the layout
        # self.centralwidget.setLayout(self.layout)

        # Open the CSV file in write mode to clear its content
        self.csv_file = open("boat_records.csv", mode="w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        # noinspection PyUnresolvedReferences
        self.centralwidget.setStyleSheet("* { color: black; }")
        # Define a list to keep track of rented boats
        self.rented_boats = []
        self.boat_times = {}  # Rented and Returned boats dictionary
        self.boat_durations = {}

        self.timer_lost_boats = QTimer(self)
        self.timer_lost_boats.timeout.connect(self.checkLostBoats)
        self.timer_lost_boats.start(
            60000
        )  # Check every minute (you can adjust the interval)

        # Define our widgets
        self.ttDispBoat = self.findChild(QtWidgets.QLabel, "ttDispBoat")
        self.ttDispStart = self.findChild(QtWidgets.QLabel, "ttDispStart")
        self.ttDispEnd = self.findChild(QtWidgets.QLabel, "ttDispEnd")
        self.ttAvgDisp = self.findChild(QtWidgets.QLabel, "ttAvgDisp")
        # self.statistics = self.findChild(QtWidgets.QLabel, "statistics")

        self.addBbtn = self.findChild(QtWidgets.QPushButton, "addBbtn")
        self.delBbtn = self.findChild(QtWidgets.QPushButton, "delBbtn")
        self.takeBbtn = self.findChild(QtWidgets.QPushButton, "takeBbtn")
        self.retBbtn = self.findChild(QtWidgets.QPushButton, "retBbtn")
        self.cal = self.findChild(QtWidgets.QPushButton, "cal")

        self.availableCB = self.findChild(QtWidgets.QComboBox, "availableCB")
        self.rentedCB = self.findChild(QtWidgets.QComboBox, "rentedCB")
        self.time = self.findChild(QtWidgets.QComboBox, "time")

        # Change text color for items in QComboBox
        self.changeComboBoxItemBackgroundColor(self.availableCB, "red")
        self.changeComboBoxItemBackgroundColor(self.rentedCB, "blue")
        self.changeComboBoxItemBackgroundColor(self.time, "green")

        # Statistics pan
        self.statistics = self.findChild(
            QtWidgets.QTextEdit, "statistics"
        )  # Find the QTextEdit widget
        self.statistics.setReadOnly(True)  # Make it read-only
        self.statistics.setLineWrapMode(
            QtWidgets.QTextEdit.WidgetWidth
        )  # Wrap text at widget width
        self.statistics.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn
        )  # Always show vertical scroll bar
        self.statistics.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )  # Disable horizontal scroll bar

        # Initialize global time variables
        global start1
        global start2
        global current_time1
        global current_time2
        start1 = None
        start2 = None

        # Connect button signals to functions
        self.addBbtn.clicked.connect(self.addNewBoat)
        self.delBbtn.clicked.connect(self.deleteBoat)
        self.takeBbtn.clicked.connect(self.addToRent)
        self.retBbtn.clicked.connect(self.returnBoat)
        self.cal.clicked.connect(self.avgTime)

        # Show the UI
        self.show()

    def appendStatistics(
        self, event, boat=None, rented_time=None, current_time=None, is_returned=False
    ):
        separator = "<div><hr></div>"
        event_text = f"<div><b>{event}</b></div>"
        boat_text = f"<div>Boat: {boat}</div>" if boat is not None else ""
        rented_time_text = (
            f"<div>Rented Time: {rented_time}</div>"
            if rented_time is not None and not is_returned
            else ""
        )
        returned_time_text = (
            f"<div>Returned Time: {current_time}</div>"
            if current_time is not None and is_returned
            else ""
        )

        # Combine the text with the separator at the top
        new_event_text = (
            f"{separator}"
            f"{event_text}{boat_text}{rented_time_text}{returned_time_text}"
        )

        current_text = self.statistics.toHtml()  # Get the existing HTML

        # If there is existing text, append a line break before adding the new event
        if current_text:
            new_event_text = f"{linebreak}{new_event_text}"

        full_text = f"{new_event_text}{current_text}"

        # Wrap the entire content in a div and apply centering styles
        centered_content = f"<div style='text-align: center; vertical-align: middle;'>{full_text}</div>"

        self.statistics.setHtml(centered_content)

    def changeComboBoxItemBackgroundColor(self, combobox, color):
        combo_stylesheet = (
            f"QComboBox QAbstractItemView {{ background-color: {color}; }}"
        )
        combobox.setStyleSheet(combo_stylesheet)

    def write_to_csv(
        self, event, boat, rented_time, current_time, rental_duration=None
    ):
        with open("boat_records.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([event, boat, rented_time, current_time, rental_duration])

    def addNewBoat(self):
        largest_number = 0
        # Find the current largest boat number
        for i in range(self.availableCB.count()):
            text = self.availableCB.itemText(i)
            boat_number = int(text.split("#")[1])
            if boat_number > largest_number:
                largest_number = boat_number

        # Add the next largest boat number
        next_boat_number = largest_number + 1
        new_boat_item = f"Boat #{next_boat_number}"
        self.availableCB.addItem(new_boat_item)

        # Print the statistics of the new boat
        current_time = datetime.now().strftime("%H:%M:%S")
        self.write_to_csv("New Boat Added", new_boat_item, current_time, current_time)
        self.appendStatistics(
            f"New boat added: {new_boat_item}{linebreak}"
            f"Time: {current_time}{linebreak}"
            "Check in the terminal or the csv file to see the full statistics as well"
        )
        self.ttDispBoat.setText(new_boat_item)
        self.ttDispStart.setText(current_time)
        self.ttDispEnd.setText("")
        print(f"New boat added: {new_boat_item} at {current_time}")

    def deleteBoat(self):
        if self.availableCB.count() > 0:
            deleted_boat = self.availableCB.currentText()
            self.availableCB.removeItem(self.availableCB.currentIndex())

            # Print the statistics of the deleted boat
            current_time = datetime.now().strftime("%H:%M:%S")
            self.write_to_csv("Boat Deleted", deleted_boat, current_time, current_time)
            self.appendStatistics(
                f"Boat deleted: {deleted_boat}{linebreak}"
                f"Time: {current_time}{linebreak}"
                "Check in the terminal or the csv file to see the full statistics as well"
            )
            self.ttDispBoat.setText(deleted_boat)
            self.ttDispStart.setText(current_time)
            self.ttDispEnd.setText("")
            print(f"Boat deleted: {deleted_boat} at {current_time}")

    def addToRent(self):
        global start1
        if start1 is None:
            start1 = datetime.now()
        global current_time1

        if self.availableCB.count() > 0:
            item = self.availableCB.currentText()
            self.availableCB.removeItem(self.availableCB.currentIndex())
            self.rented_boats.append(item)
            self.rented_boats.sort(key=lambda x: int(x.split("#")[1]))
            self.updateRentedComboBox()

            # Get the current time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.write_to_csv("Boat Rented", item, current_time, current_time)
            self.appendStatistics("Boat Rented", item, current_time, current_time)
            self.ttDispBoat.setText(item)
            self.ttDispStart.setText(current_time)
            self.ttDispEnd.setText("")
            print(f"{item} Has been rented at {current_time}")

            # Set the new start time
            start1 = datetime.now()
            current_time1 = start1.strftime("%H:%M:%S")
            self.ttDispStart.setText(current_time1)

            # Record the rental time for the boat
            self.boat_times[item] = [current_time1]
        else:
            self.appendStatistics("No boats available for rent.")
            print("No boats available for rent.")

    def returnBoat(self):
        global start2
        start2 = datetime.now()
        ritem = self.rentedCB.currentText()

        if ritem in self.rented_boats:
            self.rented_boats.remove(ritem)
            self.rented_boats.sort(key=lambda x: int(x.split("#")[1]))
            self.updateRentedComboBox()
            self.availableCB.addItem(ritem, ritem)
            self.sortAvailableBoats()

            # Get the current time
            current_time = datetime.now().strftime("%H:%M:%S")
            # Record the return time for the boat
            self.boat_times[ritem].append(current_time)
            # Calculate and display the time the boat was rented and returned
            start_time = self.boat_times[ritem][0]
            rental_duration = self.calculateTimeDifference(start_time, current_time)
            self.boat_durations[ritem] = rental_duration

            self.appendStatistics(
                f"Boat returned: {ritem} {linebreak}"
                f"Time rented: {start_time}{linebreak}"
                f"Time returned: {current_time}{linebreak}"
                f"Rental duration: {rental_duration}{linebreak}"
                "Check in the terminal or the csv file to see the full statistics as well",
            )
            print(
                f"Boat returned: {ritem} at {current_time}, rented at {start_time}, rental duration: {rental_duration}"
            )

            self.ttDispEnd.setText(current_time)
            self.ttDispBoat.setText(ritem)
            self.ttDispStart.setText(start_time)
            self.write_to_csv(
                "Boat Returned", ritem, start_time, current_time, rental_duration
            )

            # Set the new start time
            start2 = datetime.now()
        else:
            self.appendStatistics("No boat found to return.")
            print("No boat found to return.")

    def updateRentedComboBox(self):
        self.rentedCB.clear()
        for boat in self.rented_boats:
            self.rentedCB.addItem(boat, boat)

    def sortAvailableBoats(self):
        items = [self.availableCB.itemText(i) for i in range(self.availableCB.count())]
        items.sort(key=lambda x: int(x.split("#")[1]))
        self.availableCB.clear()
        self.availableCB.addItems(items)

    def checkLostBoats(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        for boat, times in self.boat_times.items():
            if len(times) == 1:
                # This boat was not returned
                self.handleLostBoat(boat, times[0], current_time)

    def handleLostBoat(self, boat, rented_time, current_time):
        b_num = "Lost boat: Boat #" + str(boat.split("#")[1]) + f"{linebreak}"
        b_rented_time = "Time rented: " + str(rented_time) + f"{linebreak}"
        b_current_time = "Current time: " + str(current_time) + f"{linebreak}"
        b_check_terminal = (
            "Check in the terminal or the csv file to see the full statistics as well"
        )
        self.appendStatistics(
            f"{b_num}\n {b_rented_time}\n {b_current_time}\n {b_check_terminal}"
        )
        # Add a record for the lost boat in the CSV file
        self.write_to_csv("Lost Boat", boat, rented_time, current_time)
        self.ttDispBoat.setText(boat)
        self.ttDispStart.setText(rented_time)
        self.ttDispEnd.setText(current_time)

    def calculateTimeDifference(self, start_time, end_time):
        start_time = datetime.strptime(start_time, "%H:%M:%S")
        end_time = datetime.strptime(end_time, "%H:%M:%S")
        time_difference = end_time - start_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} {'hour' if hours == 1 else 'hours'} {minutes} {'minute' if minutes == 1 else 'minutes'} {seconds} {'second' if seconds == 1 else 'seconds'}"

    def get_current_time(self):
        current_time = datetime.now()
        time_format = current_time.strftime("%I:%M %p")  # Format as HH:MM AM/PM
        is_am = current_time.strftime("%p") == "AM"
        return time_format, is_am

    def calculateTotalDuration(self):
        total_duration = 0
        for boat, start_time in self.boat_times.items():
            if len(start_time) == 1:
                # Boat is still rented, calculate duration until the current time
                current_time = datetime.now().strftime("%H:%M:%S")
                total_duration += self.parseDuration(
                    self.calculateTimeDifference(start_time[0], current_time)
                )
            elif len(start_time) == 2:
                # Boat has been returned, calculate the recorded duration
                total_duration += self.parseDuration(
                    self.calculateTimeDifference(start_time[0], start_time[1])
                )
        return total_duration

    def avgTime(self):
        total_duration = self.calculateTotalDuration()
        num_boats = len(self.boat_times)
        if num_boats > 0:
            average_duration = total_duration / num_boats
            self.ttAvgDisp.setText(
                f"Average Time for All Boats: {self.formatDuration(average_duration)}"
            )

    def parseDuration(self, duration):
        parts = duration.split()
        hours = int(parts[0])
        minutes = int(parts[2])
        seconds = int(parts[4])
        return hours * 3600 + minutes * 60 + seconds

    def formatDuration(self, total_seconds):
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def closeEvent(self, event):
        self.checkLostBoats()
        # Close the CSV file properly when the application is closed
        self.csv_file.close()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
