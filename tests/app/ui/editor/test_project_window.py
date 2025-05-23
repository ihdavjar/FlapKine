import pytest
from pathlib import Path
from unittest.mock import patch
from app.ui.editor.project_editor import ProjectWindow
from PyQt5.QtWidgets import QMessageBox


@pytest.fixture
def example_project_path():
    """Returns the path to the example project next to this test file."""
    return Path(__file__).parent / "1_DOF_1"


def test_project_window_loads_example(example_project_path):
    """Test that ProjectWindow can load the provided example project."""
    with patch("PyQt5.QtWidgets.QMessageBox.exec_", return_value=0):
        window = ProjectWindow(str(example_project_path))

    assert window.windowTitle() == "FlapKine"
    assert hasattr(window, "right_group")
    assert hasattr(window, "topleftgroup")
    assert hasattr(window, "bottomleftgroup")


def test_project_window_missing_scene_in_example(example_project_path):
    """Ensure error is shown if scene.pkl is removed from example folder."""
    # Temporarily rename scene.pkl if it exists
    scene_file = example_project_path / "1_DOF_1/scene.pkl"
    if scene_file.exists():
        scene_file.rename(scene_file.with_suffix(".bak"))

    try:
        with patch.object(QMessageBox, "exec_", return_value=None) as mock_exec:
            _ = ProjectWindow(str(example_project_path))
            mock_exec.assert_called_once()
    finally:
        # Restore the file
        bak_file = example_project_path / "scene.bak"
        if bak_file.exists():
            bak_file.rename(scene_file)
