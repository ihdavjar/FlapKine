import sys
from app.ui.main_window import MainWindow
from app.core.invkinematics import InvKineWindow
from app.ui.creators.project_creator import ProjectCreator  
from app.assets.styles import dark_stylesheet
from PyQt5.QtWidgets import QApplication


# window()
def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet(dark_stylesheet)
    win = ProjectCreator("D:\Research\Kinematics_App\inv_proj_2")  
    # win = InvKineWindow()
    win.show()
    sys.exit(app.exec_())

main()      