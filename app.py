from checker import Checker
from datetime import datetime
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from requests import HTTPError
from sys import exit

class CheckWorker(QObject):
    complete = pyqtSignal(str)

    def check_name(self, server, key, name):
        checker = Checker(server, key)
        try:
            name = checker.get_name_availability(name)
        except HTTPError as http:
            if (http.response.status_code == 404):
                self.complete.emit('<font size="4" color="green">Available for new/existent accounts.</font>')
                return
            else:
                self.complete.emit(f'<font size="4" color="red"><b>HTTP {http.response.status_code}</b></font>')
                return
        except ValueError:
            self.complete.emit('<font size="4" color="green">Available for new/existent accounts.</font>')
            return
        months = {1 : 'Jan', 2 : 'Feb', 3 : 'Mar', 4 : 'Apr', 5 : 'May', 6 : 'Jun', 7 : 'Jul', 8 : 'Aug', 9 : 'Sep', 10 : 'Oct', 11 : 'Nov', 12 : 'Dec'}
        if (name > datetime.now()):
            self.complete.emit(f'Available in {str((name - datetime.now())).split(".")[0]}s\n{name.day} {months[name.month]} {name.year}, {name.time()}')
        else:
            self.complete.emit('<font size="4" color="green">Available for existent accounts.</font>') 

class NameChecker(QWidget):
    check_name_start = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.name = QLineEdit()
        self.name.setPlaceholderText('Summoner name')

        self.combo = QComboBox()
        self.combo.addItems(['BR', 'EUNE', 'EUW', 'LAN', 'LAS', 'NA', 'OCE', 'RU', 'TR', 'JP', 'KR', 'PH', 'SG', 'TW', 'TH', 'VN'])

        self.key = QLineEdit()
        self.key.setPlaceholderText('Paste the api key (optional)')

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

    def keyPressEvent(self, event):
        if (event.key() == 16777220 or event.key() == 43) and self.button.isEnabled():
            self.check_name()

    def check_name(self):
        self.button.setEnabled(False)
        self.name.selectAll()

        self.worker = CheckWorker()
        self.thread = QThread(parent=self)
        self.worker.moveToThread(self.thread)

        self.check_name_start.connect(self.worker.check_name)
        self.worker.complete.connect(self.update_label)
        self.worker.complete.connect(lambda: self.button.setEnabled(True))

        self.thread.start()

        server = self.combo.currentText()
        key = self.key.text()
        name = self.name.text()

        self.check_name_start.emit(server, key, name)

    def update_label(self, text):
        self.label.setText(text) 

def app():
    app = QApplication([])
    app.setStyle('Fusion')
    name_checker = NameChecker()
    exit(app.exec())

if __name__ == '__main__':
    app()
