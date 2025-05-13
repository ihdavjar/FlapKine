import os
import sys

from PyQt5.QtWidgets import QApplication

from app.ui.main_window import MainWindow

import vtkmodules.util.data_model
import vtkmodules.util.execution_model
import vtkmodules.qt.QVTKRenderWindowInteractor

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
