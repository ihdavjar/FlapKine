# import pytest
# from PyQt5.QtCore import Qt
# from unittest.mock import patch
# from PyQt5.QtWidgets import QFileDialog
# from app.core.invkinematics import InvKineWindow

# @pytest.fixture
# def main_window(qtbot):
#     window = InvKineWindow()
#     qtbot.addWidget(window)
#     window.show()
#     return window

# def test_initial_state(main_window):
#     ''' Test the initial state of widgets before adding the inv data'''

#     assert not main_window.euler_angles_order.isEnabled()
#     assert not main_window.left_group.isEnabled()
#     assert not main_window.right_group.isEnabled()
#     assert not main_window.finish_button.isEnabled()


# def test_data_import(main_window, qtbot, tmp_path):
#     """Automated test for importing CSV data without manual file selection."""

#     # Create a dummy CSV file
#     test_file = tmp_path / "test_data.csv"
#     test_file.write_text(
#         "pt1_X,pt1_Y,pt1_Z,pt2_X,pt2_Y,pt2_Z,pt3_X,pt3_Y,pt3_Z,pt4_X,pt4_Y,pt4_Z\n" +
#         "0,0,0,1,0,0,1,-1,0,2,0,0\n" * 100
#     )

#     with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), 'csv')):
#         # Find the Import button
#         central_widget = main_window.centralWidget()
#         import_layout = central_widget.children()[1].children()

#         import_button = None

#         if len(import_layout) > 3:
#             import_button = import_layout[3]


#         assert import_button is not None, "Import button not found"

#         qtbot.mouseClick(import_button, Qt.LeftButton)

#     assert main_window.euler_angles_order.isEnabled()
#     assert main_window.left_group.isEnabled()
#     assert main_window.right_group.isEnabled()
#     assert main_window.finish_button.isEnabled()


# def test_angle_calculation_signal(main_window, qtbot, tmp_path):
#     """Test signal emission with calculated angles"""
#     # Create a dummy CSV file
#     test_file = tmp_path / "test_data.csv"
#     test_file.write_text(
#         "pt1_X,pt1_Y,pt1_Z,pt2_X,pt2_Y,pt2_Z,pt3_X,pt3_Y,pt3_Z,pt4_X,pt4_Y,pt4_Z\n" +
#         "0,0,0,1,0,0,1,-1,0,2,0,0\n" * 100
#     )

#     with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(test_file), 'csv')):
#         # Find the Import button
#         central_widget = main_window.centralWidget()
#         import_layout = central_widget.children()[1].children()

#         import_button = None

#         if len(import_layout) > 3:
#             import_button = import_layout[3]


#         assert import_button is not None, "Import button not found"

#         qtbot.mouseClick(import_button, Qt.LeftButton)

#     main_window.euler_angles_order.setCurrentText("XYZ")

#     with qtbot.waitSignal(main_window.angle_data, timeout=500) as emitter:
#         qtbot.mouseClick(main_window.finish_button, Qt.LeftButton)

#     assert emitter.args[0][1] == "XYZ"
#     assert len(emitter.args[0][0][0]) == 100
#     assert len(emitter.args[0][0][1]) == 100
#     assert len(emitter.args[0][0][2]) == 100
