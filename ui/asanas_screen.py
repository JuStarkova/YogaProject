from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation

from utils.data_loader import load_asanas
from widgets.asana_card import AsanaCard


class AsanasScreen(QWidget):

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.asanas = load_asanas()
        self.current_index = 0

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        # === ЗАГОЛОВОК ===
        title = QLabel("Асаны")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 30px;
            color: #3a3a3a;
            font-weight: 600;
        """)

        # === КАРТОЧКА ===
        self.card_container = QVBoxLayout()
        self.card_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = AsanaCard(self.asanas[self.current_index])
        self.card_container.addWidget(self.card)

        # === ИНДИКАТОР ===
        self.counter = QLabel()
        self.counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter.setStyleSheet("color: #555; font-size: 14px;")
        self.update_counter()

        # === КНОПКИ ===
        nav_layout = QHBoxLayout()

        prev_btn = QPushButton("←")
        next_btn = QPushButton("→")

        nav_style = """
            QPushButton {
                font-size: 20px;
                border-radius: 18px;
                padding: 10px 20px;
                background-color: #f0e8db;
                color: #3a3a3a;
            }
            QPushButton:hover {
                background-color: #e5d9c8;
            }
        """

        prev_btn.setStyleSheet(nav_style)
        next_btn.setStyleSheet(nav_style)

        prev_btn.clicked.connect(self.prev_asana)
        next_btn.clicked.connect(self.next_asana)

        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)

        # === НАЗАД ===
        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2dbd3;
                border-radius: 12px;
                padding: 8px 20px;
                color: #2b2b2b;
            }
            QPushButton:hover {
                background-color: #d9d0c6;
            }
        """)
        back_btn.clicked.connect(self.main_window.show_main_menu)

        # === СБОРКА ===
        main_layout.addWidget(title)
        main_layout.addLayout(self.card_container)
        main_layout.addWidget(self.counter)
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(back_btn)

        self.setLayout(main_layout)

    def update_counter(self):
        self.counter.setText(f"{self.current_index + 1} / {len(self.asanas)}")

    def animate_card(self):
        effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(effect)

        self.anim = QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def update_card(self):
        self.card.setParent(None)
        self.card = AsanaCard(self.asanas[self.current_index])
        self.card_container.addWidget(self.card)

        self.update_counter()
        self.animate_card()

    def next_asana(self):
        if self.current_index < len(self.asanas) - 1:
            self.current_index += 1
            self.update_card()

    def prev_asana(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_card()