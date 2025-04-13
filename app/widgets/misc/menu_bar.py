from PyQt5.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        """
        MenuBar Class
        =============

        A customizable menu bar for the FlapKine application interface.

        This class defines and organizes menus and actions for standard application operations such as
        file handling, editing, window management, rendering settings, and help options. The actions 
        can be dynamically connected to custom handlers using the `connect_actions` method.

        Attributes
        ----------
        file_menu : QMenu
            The "File" menu containing actions for creating a new file, opening a file, and exiting the application.

        new_action : QAction
            Action for creating a new file.

        open_action : QAction
            Action for opening an existing file.

        exit_action : QAction
            Action for exiting the application.

        edit_menu : QMenu
            The "Edit" menu containing actions for undoing and redoing operations.

        undo_action : QAction
            Action for undoing the last operation. Initially disabled.

        redo_action : QAction
            Action for redoing the last undone operation. Initially disabled.

        window_menu : QMenu
            The "Window" menu containing actions for minimizing, maximizing, and restoring the application window.

        minimize_action : QAction
            Action for minimizing the application window.

        maximize_action : QAction
            Action for maximizing the application window.

        restore_action : QAction
            Action for restoring the application window to its original size.

        render_menu : QMenu
            The "Render" menu containing actions related to rendering configurations.

        render_option : QAction
            Action for configuring render settings. Initially disabled.

        help_menu : QMenu
            The "Help" menu containing actions for accessing help and application information.

        about_action : QAction
            Action for displaying information about the application.

        Methods
        -------
        __init__(parent=None)
            Constructor that initializes all menus, actions, and their properties.

        connect_actions(handlers: dict)
            Connects menu actions to handler functions provided in a dictionary and enables/disables them accordingly.
        """

        super().__init__(parent)
        
        # File Menu
        self.file_menu = self.addMenu('File')
        self.new_action = self.file_menu.addAction('New')
        self.open_action = self.file_menu.addAction('Open')
        self.exit_action = self.file_menu.addAction('Exit')

        # Edit Menu
        self.edit_menu = self.addMenu('Edit')
        self.undo_action = self.edit_menu.addAction('Undo')
        self.undo_action.setEnabled(False)
        self.redo_action = self.edit_menu.addAction('Redo')
        self.redo_action.setEnabled(False)

        # Window Menu
        self.window_menu = self.addMenu('Window')
        self.minimize_action = self.window_menu.addAction('Minimize')
        self.maximize_action = self.window_menu.addAction('Maximize')
        self.restore_action = self.window_menu.addAction('Restore')

        # Render Menu
        self.render_menu = self.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')
        self.render_option.setEnabled(False)

        # Help Menu
        self.help_menu = self.addMenu('Help')
        self.about_action = self.help_menu.addAction('About')

        self.setStyleSheet("""
            QMenuBar {
            background-color: #2c3e50; 
            color: white;
            }
            QMenuBar::item {
            background-color: #2c3e50; 
            color: white;
            }
            QMenuBar::item:selected {
            background-color: #34495e; 
            color: #dcdcdc; /* Lighter color on hover */
            }
        """)

    def connect_actions(self, handlers)-> None:
        """
        Connects menu actions to their corresponding handler functions.

        Iterates through a predefined set of menu actions and links them to the corresponding 
        handler functions provided in the `handlers` dictionary. Each action is enabled if a 
        handler is available, and disabled otherwise.

        This modular approach allows dynamic configuration of the menu bar based on context 
        or application state.

        Args:
            handlers (dict): A dictionary mapping action keys (e.g., 'new', 'open', 'exit') 
                             to their corresponding function references.

        Behavior:
            - Enables and connects actions that have handlers defined.
            - Disables actions for which no handler is provided.

        Example:
            handlers = {
                'new': self.create_new_file,
                'open': self.load_file_dialog,
                'exit': self.close_app
            }

        Notes:
            The following action keys are supported:
                - 'new', 'open', 'exit'
                - 'undo', 'redo'
                - 'minimize', 'maximize', 'restore'
                - 'configure_render'
                - 'about'
        """

        actions = {
            'new': self.new_action,
            'open': self.open_action,
            'exit': self.exit_action,
            'minimize': self.minimize_action,
            'maximize': self.maximize_action,
            'restore': self.restore_action,
            'about': self.about_action,
            'undo': self.undo_action,
            'redo': self.redo_action,
            'configure_render': self.render_option
        }

        for key, action in actions.items():
            if key in handlers:
                action.triggered.connect(handlers[key])  # Connect event
                action.setEnabled(True)  # Enable the action
            else:
                action.setEnabled(False)  # Disable if no handler is provided
