from PyQt5.QtCore import Qt
from unittest.mock import patch
from PyQt5.QtWidgets import QFileDialog
from app.ui.creators.project_creator import ProjectCreator

def test_initial_state(qtbot, tmp_path):
    """Verify initial UI state before any interactions"""
    window = ProjectCreator(str(tmp_path))
    qtbot.addWidget(window)

    assert window.text_editor_scene.text() == ""
    assert not window.config_group.isEnabled()
    assert not window.default_config_checkbox.isChecked()


def test_scene_import(qtbot, tmp_path):
    """Test scene file import functionality without opening file dialog"""
    window = ProjectCreator(str(tmp_path))
    qtbot.addWidget(window)

    test_file = tmp_path / "test_scene.pkl"
    test_file.write_bytes(b"test_data")

    with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), '')):
        # Simulate clicking the open button, which triggers the file dialog
        qtbot.mouseClick(window.open_button, Qt.LeftButton)

    # Verify expected results
    assert window.text_editor_scene.text() == str(test_file)
    assert "green" in window.open_button.styleSheet()
