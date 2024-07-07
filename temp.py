import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class Worker(QThread):
    # Signal to communicate with the main GUI thread
    progress_signal = pyqtSignal(str)

    def run(self):
        # Simulate a long-running task
        import time
        for i in range(10):
            time.sleep(1)  # Simulating a time-consuming task
            self.progress_signal.emit(f'Progress: {i+1}/10')

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.label = QLabel('Press the button to start the long-running task', self)
        self.layout.addWidget(self.label)
        
        self.button = QPushButton('Start Task', self)
        self.button.clicked.connect(self.start_task)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        self.setWindowTitle('PyQt Threading Example')
        self.show()

    def start_task(self):
        # Disable the button to prevent multiple clicks
        self.button.setEnabled(False)

        # Create and start the worker thread
        self.worker = Worker()
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()

        # Re-enable the button when the task is done
        self.worker.finished.connect(lambda: self.button.setEnabled(True))

    def update_progress(self, message):
        # Update the label text with progress
        self.label.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
