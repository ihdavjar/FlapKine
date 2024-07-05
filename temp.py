import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QComboBox, QWidget, QHBoxLayout

class DynamicDropdowns(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dynamic Dropdowns")
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Add and Drop buttons
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Dropdown")
        self.add_button.clicked.connect(self.add_dropdown)
        self.button_layout.addWidget(self.add_button)
        
        self.drop_button = QPushButton("Drop Dropdown")
        self.drop_button.clicked.connect(self.drop_dropdown)
        self.button_layout.addWidget(self.drop_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        # Layout for dropdowns
        self.dropdown_layout = QVBoxLayout()
        self.main_layout.addLayout(self.dropdown_layout)
        
        self.setCentralWidget(self.main_widget)
    
    def add_dropdown(self):
        # Create a new dropdown menu
        dropdown = QComboBox()
        dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        self.dropdown_layout.addWidget(dropdown)
    
    def drop_dropdown(self):
        # Remove the last dropdown menu if exists
        if self.dropdown_layout.count() > 0:
            widget_to_remove = self.dropdown_layout.itemAt(self.dropdown_layout.count() - 1).widget()
            self.dropdown_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicDropdowns()
    window.show()
    sys.exit(app.exec_())
