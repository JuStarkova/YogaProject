from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from ui.main_menu import MainMenu
from ui.asanas_screen import AsanasScreen
from ui.practice_screen import PracticeScreen
from ui.music_screen import MusicScreen
from ui.practice_setup_screen import PracticeSetupScreen
from ui.asana_selector_screen import AsanaSelectorScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yoga Practice App")
        self.setGeometry(200, 200, 900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenu(self)
        self.asanas_screen = AsanasScreen(self)
        self.practice_setup = PracticeSetupScreen(self)
        self.practice_screen = PracticeScreen(self)
        self.music_screen = MusicScreen(self)
        self.asana_selector = AsanaSelectorScreen(self)

        self.stack.addWidget(self.main_menu)        # 0
        self.stack.addWidget(self.asanas_screen)    # 1
        self.stack.addWidget(self.practice_setup)   # 2
        self.stack.addWidget(self.practice_screen)  # 3
        self.stack.addWidget(self.music_screen)     # 4
        self.stack.addWidget(self.asana_selector)   # 5

        self.stack.setCurrentWidget(self.main_menu)

    def show_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu)

    def show_asanas(self):
        self.stack.setCurrentWidget(self.asanas_screen)

    def show_music(self):
        self.stack.setCurrentWidget(self.music_screen)

    def show_practice(self):
        self.stack.setCurrentWidget(self.practice_setup)

    def show_practice_setup(self):
        self.stack.setCurrentWidget(self.practice_setup)

    def show_practice_run(self):
        self.stack.setCurrentWidget(self.practice_screen)

    def show_asana_selector(self):
        # Сбрасываем галочки при каждом открытии
        self.asana_selector.reset()
        self.stack.setCurrentWidget(self.asana_selector)