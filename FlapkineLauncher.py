import os
import sys

import bpy
# import bmesh

import vtkmodules.util.data_model
import vtkmodules.util.execution_model
import vtkmodules.qt.QVTKRenderWindowInteractor

with open("log.txt", "w") as f:
    f.write("Launching Flapkine...\n")

try:
    with open("log.txt", "a") as f:
        f.write("Importing PyQt5...\n")
    from PyQt5.QtWidgets import QApplication

    with open("log.txt", "a") as f:
        f.write("Importing MainWindow...\n")
    from app.ui.main_window import MainWindow

    def main():
        with open("log.txt", "a") as f:
            f.write("Creating QApplication...\n")
        app = QApplication(sys.argv)

        with open("log.txt", "a") as f:
            f.write("Instantiating MainWindow...\n")
        win = MainWindow()
        win.show()

        with open("log.txt", "a") as f:
            f.write("Starting event loop...\n")
        sys.exit(app.exec_())

    if __name__ == "__main__":
        main()

except Exception as e:
    with open("log.txt", "a") as f:
        f.write(f"Error occurred: {str(e)}\n")
