import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from app.ui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    """Create and show the MainWindow."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


def test_new_project_button(qtbot, main_window, mocker):
    """Test clicking the 'New Project' button opens save dialog and launches ProjectCreator."""
    mock_save_dialog = mocker.patch.object(QFileDialog, "getSaveFileName", return_value=("mock_project_path", ''))
    mock_creator = mocker.patch("app.ui.main_window.ProjectCreator")

    qtbot.mouseClick(main_window.b_new, Qt.LeftButton)

    mock_save_dialog.assert_called_once()
    mock_creator.assert_called_once_with("mock_project_path")


def test_open_project_button(qtbot, main_window, mocker):
    """Test clicking the 'Open Project' button opens directory dialog and launches ProjectWindow."""
    mock_dir_dialog = mocker.patch.object(QFileDialog, "getExistingDirectory", return_value="mock_project_dir")
    mock_editor = mocker.patch("app.ui.main_window.ProjectWindow")

    qtbot.mouseClick(main_window.b_open, Qt.LeftButton)

    mock_dir_dialog.assert_called_once()
    mock_editor.assert_called_once_with("mock_project_dir")
