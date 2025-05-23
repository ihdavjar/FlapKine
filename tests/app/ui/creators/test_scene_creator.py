from unittest.mock import patch
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from app.ui.creators.scene_creator import SceneCreator

def test_initial_ui_state(qtbot):
    """Verify initial state of UI elements"""
    window = SceneCreator(project_folder="/test")
    qtbot.addWidget(window)
    import_scene = window.centralWidget().children()[2]
    assert import_scene.isEnabled()
    assert window.sprites_list_layout.count() == 0

def test_add_sprite_group(qtbot):
    """Test adding new sprite groups"""
    window = SceneCreator(project_folder="/test")
    qtbot.addWidget(window)
    add_button = window.centralWidget().children()[0].layout().itemAt(0).widget().children()[2]
    qtbot.mouseClick(add_button, Qt.LeftButton)

    assert window.sprites_list_layout.count() == 1
    assert "Sprite 1" in window.sprites_list_layout.itemAt(0).widget().title()

def test_remove_sprite_group(qtbot):
    """Test removing sprite groups"""
    window = SceneCreator(project_folder="/test")
    qtbot.addWidget(window)

    # Add 3 groups then remove 1
    add_button = window.centralWidget().children()[0].layout().itemAt(0).widget().children()[2]
    for _ in range(3):
        qtbot.mouseClick(add_button, Qt.LeftButton)

    drop_button = window.centralWidget().children()[0].layout().itemAt(0).widget().children()[3]
    qtbot.mouseClick(drop_button, Qt.LeftButton)

    assert window.sprites_list_layout.count() == 2

def test_sprite_creation_dialog(qtbot):
    """Verify SpriteCreator window opens"""
    window = SceneCreator(project_folder="/test")
    qtbot.addWidget(window)

    # Add a sprite group first
    add_button = window.centralWidget().children()[0].layout().itemAt(0).widget().children()[2]
    qtbot.mouseClick(add_button, Qt.LeftButton)

    create_button = window.sprites_list_layout.itemAt(0).widget().children()[3]
    qtbot.mouseClick(create_button, Qt.LeftButton)

    assert window.window.isVisible()
    window.window.close()

def test_file_import_interaction(qtbot, tmp_path):
    """Test .pkl file import workflow without opening file dialog"""
    window = SceneCreator(project_folder="/test")
    qtbot.addWidget(window)

    # Create test file
    test_file = tmp_path / "test_scene.pkl"
    test_file.write_bytes(b"test_data")

    # Patch QFileDialog to return the test file path
    with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), '')):
        # Add sprite group and click import
        add_button = window.centralWidget().children()[0].layout().itemAt(0).widget().children()[2]
        qtbot.mouseClick(add_button, Qt.LeftButton)

        import_button = window.sprites_list_layout.itemAt(0).widget().children()[2]
        qtbot.mouseClick(import_button, Qt.LeftButton)

    line_edit = window.sprites_list_layout.itemAt(0).widget().findChild(QLineEdit)
    assert str(test_file) in line_edit.text()
    assert "green" in import_button.styleSheet()
