import sys
from app.main_window import MainWindow
from app.project_window import ProjectWindow
from app.styles import dark_stylesheet
from PyQt5.QtWidgets import QApplication


# window()
def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet(dark_stylesheet)
    win = MainWindow()  
    win.show()
    sys.exit(app.exec_())

main()

