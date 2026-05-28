from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os


class AsanaCard(QWidget):

    def __init__(self, asana_data):
        super().__init__()

        self.asana = asana_data
        self.setFixedSize(300, 420)

        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        # === FRONT ===
        self.front = QLabel()
        self.front.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.front.setStyleSheet("""
            border-radius: 20px;
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #ede1cf,
                stop:1 #dccfba
            );
        """)

        image_path = self.get_image_path(self.asana["image"])
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            self.front.setPixmap(
                pixmap.scaled(
                    260, 340,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            self.front.setText("Нет изображения")

        # === BACK ===
        self.back = QLabel()
        self.back.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.back.setWordWrap(True)
        self.back.setStyleSheet("""
            border-radius: 20px;
            padding: 18px;
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #f7efe4,
                stop:1 #e3d5bf
            );
            color: #2b2b2b;
            font-size: 15px;
        """)

        text = f"""
            <b style='font-size: 16px;'>{self.asana['ru_name']}</b>
            <br>
            <span style='font-size: 17px; color: #5c1a1a; font-style: italic; margin-top: 2px;'>{self.asana['name']}</span>
            <br><br>
            <i>{self.asana['description']}</i>
        """
        self.back.setText(text)

        self.layout.addWidget(self.front)
        self.layout.addWidget(self.back)

        self.show_front = True

    def mousePressEvent(self, event):
        if self.show_front:
            self.layout.setCurrentWidget(self.back)
        else:
            self.layout.setCurrentWidget(self.front)

        self.show_front = not self.show_front

    def get_image_path(self, image_name):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "assets", "images", image_name)