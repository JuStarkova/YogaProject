from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os


class MainMenu(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window  # <-- связь с главным окном

        self.setMinimumSize(800, 600)

        # === ФОН ===
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "assets", "images", "background.jpg")

        pixmap = QPixmap(image_path)
        self.bg_label.setPixmap(pixmap)

        # === КОНТЕНТ ===
        self.container = QWidget(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        # Заголовок
        title = QLabel("Главное меню")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 40px;
            color: white;
            font-weight: bold;
        """)

        # Кнопки
        practice_btn = QPushButton("Практика")
        asanas_btn = QPushButton("Асаны")
        music_btn = QPushButton("Музыка")

        button_style = """
            QPushButton {
                border-radius: 25px;
                padding: 15px;
                font-size: 18px;
                min-width: 250px;
                background-color: rgba(255, 255, 255, 0.85);
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 1);
            }
        """

        practice_btn.setStyleSheet(button_style)
        asanas_btn.setStyleSheet(button_style)
        music_btn.setStyleSheet(button_style)

        # === СВЯЗЫВАЕМ КНОПКИ ===
        practice_btn.clicked.connect(self.main_window.show_practice)
        asanas_btn.clicked.connect(self.main_window.show_asanas)
        music_btn.clicked.connect(self.main_window.show_music)

        layout.addWidget(title)
        layout.addWidget(practice_btn)
        layout.addWidget(asanas_btn)
        layout.addWidget(music_btn)

        self.container.setLayout(layout)

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.container.setGeometry(0, 0, self.width(), self.height())