import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QComboBox, QPushButton
import numpy as np
from unittest.mock import MagicMock
from app.ui.creators.sprite_creator import SpriteCreator

@pytest.fixture
def sprite_creator(qtbot, tmp_path):
    """Fixture to create SpriteCreator with test project folder"""
    creator = SpriteCreator(project_folder=str(tmp_path))
    qtbot.addWidget(creator)
    return creator

def test_initial_state(sprite_creator):
    """Verify initial UI state after creation"""
    assert sprite_creator.sprite_name.text() == ""
    assert sprite_creator.sprite_stl_path.text() == ""
    assert not sprite_creator.group_2.isEnabled()
    assert sprite_creator.translation_transform.currentIndex() == 0

from unittest.mock import patch
from PyQt5.QtWidgets import QFileDialog

def test_stl_file_import(sprite_creator, qtbot, tmp_path):
    """Test STL file import workflow without opening file dialog"""

    # Create test STL file
    test_file = tmp_path / "test.stl"
    test_file.write_text("solid test\nendsolid test")

    # Patch the file dialog to return the test file path
    with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), '')):
        qtbot.mouseClick(sprite_creator.sprite_stl_open, Qt.LeftButton)

    actors = sprite_creator.ren.GetActors()
    actors.InitTraversal()  # Always call this before traversal

    count = 0
    while actors.GetNextActor():
        count += 1
    assert sprite_creator.sprite_stl_path.text() == str(test_file)
    assert count == 13

def test_translation_transform_selection(sprite_creator, qtbot):
    """Test translation transform UI updates"""
    # Select "Linear" translation
    sprite_creator.translation_transform.setCurrentIndex(1)

    # Verify UI elements
    translation_group = sprite_creator.translation_transform_layout.itemAt(1).widget()
    assert translation_group is not None
    assert translation_group.findChild(QLineEdit).placeholderText() == "Time series of body origin position"

def test_initial_conditions_transform(sprite_creator, qtbot, tmp_path):
    """Test initial conditions affect actor transform"""
    # Create test STL file
    test_file = tmp_path / "test.stl"
    test_file.write_text("solid test\nendsolid test")

    # Patch the file dialog to return the test file path
    with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), '')):
        qtbot.mouseClick(sprite_creator.sprite_stl_open, Qt.LeftButton)

    # Enable initial conditions
    qtbot.mouseClick(sprite_creator.enable_checkbox, Qt.LeftButton)

    # Set test values
    sprite_creator.position_x.setValue(5.0)
    sprite_creator.angle_input_alpha.setValue(45.0)

    # Verify transform updates
    actor = sprite_creator.actor
    transform = actor.GetUserTransform()
    assert transform.GetPosition() == (5.0, 0.0, 0.0)
    assert transform.GetOrientation()[0] == pytest.approx(45.0)

def test_sprite_creation_signal(sprite_creator, qtbot, tmp_path):
    """Test complete sprite creation workflow with valid STL geometry"""
    from textwrap import dedent

    # Setup test data
    sprite_creator.sprite_name.setText("TestSprite")

    # Create a valid minimal ASCII STL file (single triangle)
    stl_content = dedent("""\
        solid test
          facet normal 0 0 1
            outer loop
              vertex 0 0 0
              vertex 1 0 0
              vertex 0 1 0
            endloop
          endfacet
        endsolid test
    """)
    test_file = tmp_path / "test.stl"
    test_file.write_text(stl_content)

    # Patch the file dialog to return the test file path
    with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), '')):
        qtbot.mouseClick(sprite_creator.sprite_stl_open, Qt.LeftButton)

    # Connect to signal and click finish
    with qtbot.waitSignal(sprite_creator.SpriteCreated, timeout=3000) as emitter:
        qtbot.mouseClick(sprite_creator.finish_button, Qt.LeftButton)

    assert emitter.args[0].object_.name == "TestSprite"
