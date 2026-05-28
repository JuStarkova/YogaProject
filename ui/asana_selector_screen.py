from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor
from utils.data_loader import load_asanas


# ─────────────────────────────────────────────────────────────────────────────
#  Карточка в списке порядка — перетаскиваемая
# ─────────────────────────────────────────────────────────────────────────────

class DraggableRow(QFrame):
    """Строка с асаной которую можно перетащить вверх/вниз."""

    def __init__(self, asana_name: str, ru_name: str, index: int, order_widget):
        super().__init__()
        self.asana_name = asana_name
        self.order_widget = order_widget
        self.setAcceptDrops(True)

        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.85);
                border-radius: 10px;
                border: 1px solid #c8dcc8;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(50)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(10)

        self._num_lbl = QLabel(str(index + 1))
        self._num_lbl.setFixedWidth(24)
        self._num_lbl.setStyleSheet("font-size: 13px; color: #888; background: transparent;")
        self._num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(self._num_lbl)

        drag_lbl = QLabel("☰")
        drag_lbl.setStyleSheet("font-size: 16px; color: #a0b8a0; background: transparent;")
        drag_lbl.setFixedWidth(20)
        hl.addWidget(drag_lbl)

        name_lbl = QLabel(f"{ru_name}  /  {asana_name}" if ru_name else asana_name)
        name_lbl.setStyleSheet("font-size: 14px; color: #2b3d2b; background: transparent;")
        hl.addWidget(name_lbl)
        hl.addStretch()

    def set_index(self, i: int):
        self._num_lbl.setText(str(i + 1))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self._drag_start).manhattanLength() < 10:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.asana_name)
        drag.setMimeData(mime)

        # Миниатюра для перетаскивания
        px = QPixmap(self.size())
        px.fill(QColor(0, 0, 0, 0))
        painter = QPainter(px)
        self.render(painter)
        painter.end()
        drag.setPixmap(px)
        drag.setHotSpot(self._drag_start)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background: #d0e8d0;
                    border-radius: 10px;
                    border: 2px solid #5a7d5a;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.85);
                border-radius: 10px;
                border: 1px solid #c8dcc8;
            }
        """)

    def dropEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.85);
                border-radius: 10px;
                border: 1px solid #c8dcc8;
            }
        """)
        src_name = event.mimeData().text()
        if src_name != self.asana_name:
            self.order_widget.swap_items(src_name, self.asana_name)
        event.acceptProposedAction()


# ─────────────────────────────────────────────────────────────────────────────
#  Виджет расстановки порядка
# ─────────────────────────────────────────────────────────────────────────────

class OrderWidget(QWidget):
    """Список асан с возможностью перетаскивания для смены порядка."""

    def __init__(self, asana_names: list, name_map: dict):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        self._order = list(asana_names)   # список english-имён в текущем порядке
        self._name_map = name_map         # en -> ru
        self._vl = QVBoxLayout(self)
        self._vl.setContentsMargins(0, 0, 0, 0)
        self._vl.setSpacing(6)
        self._rows: dict[str, DraggableRow] = {}
        self._rebuild()

    def _rebuild(self):
        # Очищаем layout
        for i in reversed(range(self._vl.count())):
            w = self._vl.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._rows.clear()

        for i, name in enumerate(self._order):
            ru = self._name_map.get(name, "")
            row = DraggableRow(name, ru, i, self)
            self._rows[name] = row
            self._vl.addWidget(row)

    def swap_items(self, src_name: str, dst_name: str):
        i = self._order.index(src_name)
        j = self._order.index(dst_name)
        self._order[i], self._order[j] = self._order[j], self._order[i]
        self._rebuild()

    def get_order(self) -> list:
        return list(self._order)


# ─────────────────────────────────────────────────────────────────────────────
#  Главный экран выбора асан
# ─────────────────────────────────────────────────────────────────────────────

class AsanaSelectorScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._all_asanas = load_asanas()
        # Словарь en -> ru
        self._name_map = {a.get("name", ""): a.get("ru_name", "")
                          for a in self._all_asanas}

        self._step = "select"   # "select" или "order"
        self._selected_names = []

        self.setStyleSheet("""
            AsanaSelectorScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f0e8, stop:1 #c8dcc8
                );
            }
            QCheckBox {
                font-size: 14px; color: #2b3d2b;
                spacing: 10px; padding: 5px 0;
            }
            QCheckBox::indicator {
                width: 20px; height: 20px; border-radius: 5px;
                background: rgba(255,255,255,0.7);
                border: 2px solid #a0b8a0;
            }
            QCheckBox::indicator:checked {
                background-color: #5a7d5a;
                border: 2px solid #5a7d5a;
            }
        """)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        self._build_select_screen()

    # ── Экран 1: выбор ──────────────────────────────────────────────────────

    def _build_select_screen(self):
        self._clear_root()

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(wrapper)
        vl.setContentsMargins(30, 20, 30, 16)
        vl.setSpacing(12)

        title = QLabel("Выберите асаны для практики")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #2b3d2b;")
        vl.addWidget(title)

        self._hint = QLabel("Выберите не менее 3 асан, затем расставьте порядок")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet("font-size: 13px; color: #5a7d5a;")
        vl.addWidget(self._hint)

        # Счётчик выбранных
        self._count_lbl = QLabel("Выбрано: 0")
        self._count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._count_lbl.setStyleSheet("font-size: 13px; color: #2b3d2b; font-weight: 600;")
        vl.addWidget(self._count_lbl)

        # Список
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        sc = QWidget()
        sc.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(sc)
        cl.setSpacing(2)
        cl.setContentsMargins(0, 0, 0, 0)

        self.checkboxes = []
        for asana in self._all_asanas:
            ru = asana.get('ru_name', '')
            en = asana.get('name', '')
            label = f"{ru}  /  {en}" if ru else en
            cb = QCheckBox(label)
            cb.setProperty("asana_name", en)
            cb.setChecked(False)   # всегда сбрасываем при открытии
            cb.stateChanged.connect(self._update_count)
            self.checkboxes.append(cb)
            cl.addWidget(cb)

        scroll.setWidget(sc)
        vl.addWidget(scroll)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet(
            "QPushButton { background: #a0524f; color: white; border-radius: 12px;"
            " padding: 12px 24px; font-size: 15px; font-weight: 600; border: none; }"
            " QPushButton:hover { background: #8a3f3c; }")
        cancel_btn.clicked.connect(self._go_back)
        btn_row.addWidget(cancel_btn)

        self._next_btn = QPushButton("Далее: порядок →")
        self._next_btn.setEnabled(False)
        self._next_btn.setStyleSheet(self._next_style(enabled=False))
        self._next_btn.clicked.connect(self._go_to_order)
        btn_row.addWidget(self._next_btn)

        vl.addLayout(btn_row)
        self._root.addWidget(wrapper)

    # ── Экран 2: порядок ────────────────────────────────────────────────────

    def _build_order_screen(self):
        self._clear_root()

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(wrapper)
        vl.setContentsMargins(30, 20, 30, 16)
        vl.setSpacing(12)

        title = QLabel("Расставьте асаны в нужном порядке")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #2b3d2b;")
        vl.addWidget(title)

        hint = QLabel("Перетащите строки для изменения порядка")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 13px; color: #5a7d5a;")
        vl.addWidget(hint)

        # Прокручиваемый список с порядком
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._order_widget = OrderWidget(self._selected_names, self._name_map)
        scroll.setWidget(self._order_widget)
        vl.addWidget(scroll)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        back_btn = QPushButton("← Назад")
        back_btn.setStyleSheet(
            "QPushButton { background: #7a9a7a; color: white; border-radius: 12px;"
            " padding: 12px 24px; font-size: 15px; font-weight: 600; border: none; }"
            " QPushButton:hover { background: #5a7d5a; }")
        back_btn.clicked.connect(self._go_back_to_select)
        btn_row.addWidget(back_btn)

        save_btn = QPushButton("Сохранить порядок")
        save_btn.setStyleSheet(
            "QPushButton { background: #5a7d5a; color: white; border-radius: 12px;"
            " padding: 12px 24px; font-size: 15px; font-weight: 600; border: none; }"
            " QPushButton:hover { background: #3d5a3d; }")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        vl.addLayout(btn_row)
        self._root.addWidget(wrapper)

    # ── Вспомогательные ─────────────────────────────────────────────────────

    def _clear_root(self):
        for i in reversed(range(self._root.count())):
            w = self._root.itemAt(i).widget()
            if w:
                w.setParent(None)

    def _update_count(self):
        n = sum(1 for cb in self.checkboxes if cb.isChecked())
        self._count_lbl.setText(f"Выбрано: {n}")
        enabled = n >= 3
        self._next_btn.setEnabled(enabled)
        self._next_btn.setStyleSheet(self._next_style(enabled=enabled))

    def _next_style(self, enabled=True):
        if enabled:
            return ("QPushButton { background: #5a7d5a; color: white; border-radius: 12px;"
                    " padding: 12px 24px; font-size: 15px; font-weight: 600; border: none; }"
                    " QPushButton:hover { background: #3d5a3d; }")
        return ("QPushButton { background: #a0b8a0; color: #d0d0d0; border-radius: 12px;"
                " padding: 12px 24px; font-size: 15px; font-weight: 600; border: none; }")

    def _go_to_order(self):
        self._selected_names = [cb.property("asana_name")
                                 for cb in self.checkboxes if cb.isChecked()]
        self._build_order_screen()

    def _go_back_to_select(self):
        self._build_select_screen()
        # Восстанавливаем отмеченные галочки
        for cb in self.checkboxes:
            cb.setChecked(cb.property("asana_name") in self._selected_names)
        self._update_count()

    def _go_back(self):
        self.parent.show_practice_setup()

    def _save(self):
        ordered = self._order_widget.get_order()
        self.parent.practice_setup.set_selected_asanas(ordered)
        self.parent.show_practice_setup()

    # Вызывается при каждом открытии экрана — сбрасывает состояние
    def reset(self):
        self._selected_names = []
        self._build_select_screen()