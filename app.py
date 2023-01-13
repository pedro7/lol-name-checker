from checker import Checker
from datetime import datetime
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from requests import HTTPError
from sys import exit

class CheckWorker(QObject):
    complete = pyqtSignal(str)

    def check_name(self, key, server, name):
        checker = Checker(key, server)
        try:
            date = checker.get_name_availability_datetime(name)
        except HTTPError as err:
            if (err.response.status_code == 404):
                self.complete.emit('The name is available for new\nand existent accounts. ✅')
                return
            elif (err.response.status_code == 403):
                self.complete.emit('❌ Invalid or expired key ❌')
                return
            elif (err.response.status_code == 429):
                self.complete.emit('❌ Exceeded number of requests ❌')
                return
            else:
                self.complete.emit('❌ Unknown error ❌')
                return
        months = {1 : 'Jan', 2 : 'Feb', 3 : 'Mar', 4 : 'Apr', 5 : 'May', 6 : 'Jun', 7 : 'Jul', 8 : 'Aug', 9 : 'Sep', 10 : 'Oct', 11 : 'Nov', 12 : 'Dec'}
        if (date > datetime.now()):
            self.complete.emit(f'Available in {(date - datetime.now()).days + 1} day(s).\n{date.day} {months[date.month]} {date.year}, {date.time()}')
        else:
            self.complete.emit('The name is available for\nexistent accounts. ✅') 

class NameChecker(QWidget):
    check_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.name = QLineEdit()
        self.name.setPlaceholderText('Summoner name')

        self.combo = QComboBox()
        self.combo.addItems(['BR', 'EUNE', 'EUW', 'LAN', 'LAS', 'NA', 'OCE', 'RU', 'TR', 'JP', 'KR'])

        self.key = QLineEdit()
        self.key.setPlaceholderText('Paste the api key')

        self.button = QPushButton('Search')
        self.button.clicked.connect(self.check_name)

        self.label = QLabel('<a href=http://www.github.com/pedro7><font size="4" color="black">github.com/pedro7</font></a>')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setOpenExternalLinks(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.name)
        top_layout.addWidget(self.combo)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.key)
        bottom_layout.addWidget(self.button)
        bottom_layout.addWidget(self.label)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        self.setWindowTitle('Name Checker')
        self.setFixedSize(246, 143)
        self.setLayout(layout)
        self.show()

    def check_name(self):
        self.button.setEnabled(False)

        self.worker = CheckWorker()
        self.thread = QThread(parent=self)
        self.worker.moveToThread(self.thread)

        self.check_signal.connect(self.worker.check_name)
        self.worker.complete.connect(self.update_label)
        self.worker.complete.connect(lambda: self.button.setEnabled(True))

        self.thread.start()

        key = self.key.text()
        server = self.combo.currentText()
        name = self.name.text()

        self.check_signal.emit(key, server, name)

    def update_label(self, text):
        self.label.setText(text)

def app():
    app = QApplication([])
    app.setStyle('Fusion')
    name_checker = NameChecker()
    exit(app.exec())

if __name__ == '__main__':
    app()