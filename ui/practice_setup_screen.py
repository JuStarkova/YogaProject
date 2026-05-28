from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSlider, QCheckBox, QStyle, QStyleOption,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPainter


SETUP_STYLE = """
#PracticeSetupScreen {
    background: qlineargradient(
        x1:0, y1:0, x2:0.3, y2:1,
        stop:0 #edf5ed, stop:1 #d8ead8
    );
}

#PracticeSetupScreen #section_label {
    font-size: 13px;
    font-weight: 700;
    color: #4a6a4a;
    letter-spacing: 1px;
}

#PracticeSetupScreen #card {
    background: rgba(255,255,255,0.75);
    border-radius: 16px;
    border: 1px solid rgba(90,125,90,0.15);
}

/* ── Переключатели (Уровень, Режим, Музыка) ── */
#PracticeSetupScreen QPushButton#toggle_btn {
    background: rgba(255,255,255,0.6);
    color: #2b3d2b;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: 600;
    border: 1.5px solid rgba(90,125,90,0.3);
}
#PracticeSetupScreen QPushButton#toggle_btn:hover {
    background: rgba(90,125,90,0.12);
    border: 1.5px solid #5a7d5a;
    color: #2b3d2b;
}
#PracticeSetupScreen QPushButton#toggle_btn[active="true"] {
    background: #5a7d5a;
    color: #ffffff;
    border: 1.5px solid #5a7d5a;
    font-weight: 700;
}

/* ── Фокус практики ── */
#PracticeSetupScreen QPushButton#focus_btn {
    background: rgba(255,255,255,0.6);
    color: #2b3d2b;
    border-radius: 12px;
    padding: 11px 18px;
    font-size: 16px;
    font-weight: 600;
    border: 1.5px solid rgba(90,125,90,0.3);
}
#PracticeSetupScreen QPushButton#focus_btn:hover {
    background: rgba(90,125,90,0.12);
    border: 1.5px solid #5a7d5a;
    color: #2b3d2b;
}
#PracticeSetupScreen QPushButton#focus_btn[active="true"] {
    background: #5a7d5a;
    color: #ffffff;
    border: 1.5px solid #5a7d5a;
    font-weight: 700;
}

/* ── Быстрые кнопки минут/секунд ── */
#PracticeSetupScreen QPushButton#quick_btn {
    background: rgba(255,255,255,0.6);
    color: #2b3d2b;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid rgba(90,125,90,0.3);
    padding: 6px 14px;
}
#PracticeSetupScreen QPushButton#quick_btn:hover {
    background: rgba(90,125,90,0.15);
    border: 1px solid #5a7d5a;
    color: #2b3d2b;
}

/* ── Ручной выбор асан ── */
#PracticeSetupScreen QPushButton#select_btn {
    background: #618061;
    color: #ffffff;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 600;
    border: 2px dashed #edf5ed;
}
#PracticeSetupScreen QPushButton#select_btn:hover {
    background: #3b523b;
}

/* ── Ползунки и чекбоксы ── */
#PracticeSetupScreen QSlider::groove:horizontal {
    height: 6px;
    background: rgba(90,125,90,0.2);
    border-radius: 3px;
}
#PracticeSetupScreen QSlider::handle:horizontal {
    width: 22px; height: 22px;
    background: #5a7d5a;
    border-radius: 11px;
    margin: -8px 0;
}
#PracticeSetupScreen QSlider::sub-page:horizontal {
    background: #5a7d5a;
    border-radius: 3px;
}

#PracticeSetupScreen QCheckBox {
    font-size: 16px;
    color: #2b3d2b;
    spacing: 10px;
    font-weight: 600;
}
#PracticeSetupScreen QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 6px;
    border: 1.5px solid rgba(90,125,90,0.4);
    background: rgba(255,255,255,0.7);
}
#PracticeSetupScreen QCheckBox::indicator:checked {
    background: #5a7d5a;
    border: 1.5px solid #5a7d5a;
}

#PracticeSetupScreen #slider_value {
    font-family: Georgia, serif;
    font-size: 30px;
    font-weight: bold;
    color: #2b3d2b;
}
#PracticeSetupScreen #slider_unit {
    font-size: 15px;
    color: #5a7d5a;
    font-weight: 600;
}

/* ── Нижние кнопки ── */
#PracticeSetupScreen QPushButton#btn_back {
    background: #a0524f;
    color: white;
    border-radius: 14px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 600;
    border: none;
}
#PracticeSetupScreen QPushButton#btn_back:hover { background: rgba(160,82,79,0.85); }

#PracticeSetupScreen QPushButton#btn_start {
    background: #5a7d5a;
    color: white;
    border-radius: 14px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 700;
    border: none;
}
#PracticeSetupScreen QPushButton#btn_start:hover { background: rgba(90,125,90,0.85); }
"""


class PracticeSetupScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        self.setObjectName("PracticeSetupScreen")
        self.setStyleSheet(SETUP_STYLE)

        self._level = "beginner"
        self._mode = "Готовая практика"
        self._duration = 20
        self._hold = 30
        self._music = "Без музыки"
        self._auto = True
        self._filters = []

        self._select_btn = QPushButton("Выбрать асаны вручную")
        self._select_btn.setObjectName("select_btn")
        self._select_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._select_btn.setVisible(False)
        try:
            self._select_btn.clicked.connect(self.parent.show_asana_selector)
        except Exception:
            pass

        self._selected_asanas = None
        self._start_btn = None
        self._build_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(content)
        vl.setContentsMargins(28, 24, 28, 16)
        vl.setSpacing(14)

        # Заголовок
        title = QLabel("Настройка практики")
        title.setStyleSheet(
            "font-family: Georgia, serif; font-size: 26px;"
            " font-weight: bold; color: #2b3d2b; margin-bottom: 4px;"
        )
        vl.addWidget(title)

        # ── Уровень ─────────────────────────────────────────────────────────
        vl.addWidget(self._section("Уровень подготовки"))
        lv_card = self._card()
        lv_row = QHBoxLayout()
        lv_row.setSpacing(10)
        self._level_btns = {}
        for text, key in [
            ("Начальный", "beginner"),
            ("Средний", "intermediate"),
            ("Продвинутый", "advanced"),
        ]:
            btn = self._toggle(text)
            btn.clicked.connect(lambda _, k=key: self._set_level(k))
            self._level_btns[key] = btn
            lv_row.addWidget(btn)
        lv_card.layout().addLayout(lv_row)
        vl.addWidget(lv_card)
        self._set_level("beginner")

        # ── Тип практики ────────────────────────────────────────────────────
        vl.addWidget(self._section("Тип практики"))
        mode_card = self._card()
        mode_row = QHBoxLayout()
        mode_row.setSpacing(10)
        self._mode_btns = {}
        for text in ["Готовая практика", "Своя практика"]:
            btn = self._toggle(text)
            btn.clicked.connect(lambda _, t=text: self._set_mode(t))
            self._mode_btns[text] = btn
            mode_row.addWidget(btn)
        mode_card.layout().addLayout(mode_row)
        vl.addWidget(mode_card)
        self._set_mode("Готовая практика")

        # ── Длительность ────────────────────────────────────────────────────
        vl.addWidget(self._section("Длительность (минут)"))
        dur_card = self._card()

        dur_top = QHBoxLayout()
        self._dur_val = QLabel("20")
        self._dur_val.setObjectName("slider_value")
        dur_unit = QLabel("мин")
        dur_unit.setObjectName("slider_unit")
        dur_top.addWidget(self._dur_val)
        dur_top.addWidget(dur_unit)
        dur_top.addStretch()
        for m in [10, 20, 30, 45, 60]:
            b = QPushButton(str(m))
            b.setObjectName("quick_btn")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, v=m: self._set_dur(v))
            dur_top.addWidget(b)
        dur_card.layout().addLayout(dur_top)

        self._dur_slider = QSlider(Qt.Orientation.Horizontal)
        self._dur_slider.setMinimum(5)
        self._dur_slider.setMaximum(90)
        self._dur_slider.setValue(20)
        self._dur_slider.setCursor(QCursor(Qt.CursorShape.SplitHCursor))
        self._dur_slider.valueChanged.connect(lambda v: self._on_dur(v))
        dur_card.layout().addWidget(self._dur_slider)
        vl.addWidget(dur_card)

        # ── Удержание асаны ─────────────────────────────────────────────────
        vl.addWidget(self._section("Время удержания асаны (сек)"))
        hold_card = self._card()

        hold_top = QHBoxLayout()
        self._hold_val = QLabel("30")
        self._hold_val.setObjectName("slider_value")
        hold_unit = QLabel("сек")
        hold_unit.setObjectName("slider_unit")
        hold_top.addWidget(self._hold_val)
        hold_top.addWidget(hold_unit)
        hold_top.addStretch()
        for s in [15, 30, 45, 60]:
            b = QPushButton(str(s))
            b.setObjectName("quick_btn")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, v=s: self._set_hold(v))
            hold_top.addWidget(b)
        hold_card.layout().addLayout(hold_top)

        self._hold_slider = QSlider(Qt.Orientation.Horizontal)
        self._hold_slider.setMinimum(10)
        self._hold_slider.setMaximum(120)
        self._hold_slider.setValue(30)
        self._hold_slider.setCursor(QCursor(Qt.CursorShape.SplitHCursor))
        self._hold_slider.valueChanged.connect(lambda v: self._on_hold(v))
        hold_card.layout().addWidget(self._hold_slider)
        vl.addWidget(hold_card)

        # ── Музыка ──────────────────────────────────────────────────────────
        vl.addWidget(self._section("Музыкальное сопровождение"))
        music_card = self._card()
        music_row = QHBoxLayout()
        music_row.setSpacing(8)
        self._music_btns = {}
        for track in ["Без музыки", "Спокойная", "Энергичная", "Медитация"]:
            btn = self._toggle(track)
            btn.clicked.connect(lambda _, t=track: self._set_music(t))
            self._music_btns[track] = btn
            music_row.addWidget(btn)
        music_card.layout().addLayout(music_row)

        self._auto_cb = QCheckBox("Автоматическое перелистывание")
        self._auto_cb.setChecked(True)
        self._auto_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._auto_cb.stateChanged.connect(lambda s: setattr(self, '_auto', bool(s)))
        music_card.layout().addWidget(self._auto_cb)
        vl.addWidget(music_card)
        self._set_music("Без музыки")

        # ── Фокус практики ──────────────────────────────────────────────────
        vl.addWidget(self._section("Фокус практики"))
        focus_card = self._card()
        focus_row = QHBoxLayout()
        focus_row.setSpacing(8)
        self._focus_btns = {}
        for label, key in [
            ("Сила", "strength"),
            ("Растяжка", "stretch"),
            ("Расслабление", "relax"),
            ("Баланс", "balance"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("focus_btn")
            btn.setProperty("active", "false")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, k=key, b=btn: self._toggle_focus(k, b))
            self._focus_btns[key] = btn
            focus_row.addWidget(btn)
        focus_card.layout().addLayout(focus_row)
        vl.addWidget(focus_card)

        vl.addWidget(self._select_btn)

        vl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)

        # ── Нижняя панель ───────────────────────────────────────────────────
        bottom = QWidget()
        bottom.setStyleSheet("""
            background: rgba(237,245,237,0.97);
            border-top: 1.5px solid rgba(90,125,90,0.2);
        """)
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(28, 12, 28, 16)
        bl.setSpacing(14)

        back_btn = QPushButton("Назад")
        back_btn.setObjectName("btn_back")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.clicked.connect(self.parent.show_main_menu)
        bl.addWidget(back_btn)

        start_btn = QPushButton("Начать практику")
        start_btn.setObjectName("btn_start")
        start_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        start_btn.clicked.connect(self._start)
        bl.addWidget(start_btn, stretch=2)

        root.addWidget(bottom)

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl

    def _card(self):
        card = QFrame()
        card.setObjectName("card")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(16, 14, 16, 14)
        vl.setSpacing(12)
        return card

    def _toggle(self, text):
        btn = QPushButton(text)
        btn.setObjectName("toggle_btn")
        btn.setProperty("active", "false")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn

    def _activate(self, btn, group):
        for b in group.values():
            b.setProperty("active", "false")
            b.style().unpolish(b)
            b.style().polish(b)
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def _set_level(self, key):
        self._level = key
        self._activate(self._level_btns[key], self._level_btns)

    def _set_mode(self, text):
        self._mode = text
        self._activate(self._mode_btns[text], self._mode_btns)
        self._select_btn.setVisible(text == "Своя практика")

    def _set_music(self, text):
        self._music = text
        self._activate(self._music_btns[text], self._music_btns)

    def _on_dur(self, v):
        self._duration = v
        self._dur_val.setText(str(v))

    def _set_dur(self, v):
        self._duration = v
        self._dur_slider.setValue(v)

    def _on_hold(self, v):
        self._hold = v
        self._hold_val.setText(str(v))

    def _set_hold(self, v):
        self._hold = v
        self._hold_slider.setValue(v)

    def _toggle_focus(self, key, btn):
        if key in self._filters:
            self._filters.remove(key)
            btn.setProperty("active", "false")
        else:
            self._filters.append(key)
            btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def set_selected_asanas(self, names):
        """Вызывается из AsanaSelectorScreen после выбора асан."""
        self._selected_asanas = names if names else None
        if hasattr(self, '_selected_label'):
            if self._selected_asanas:
                self._selected_label.setText(f"Выбрано асан: {len(self._selected_asanas)}")
                self._selected_label.setVisible(True)
            else:
                self._selected_label.setVisible(False)
        if hasattr(self, '_start_btn') and self._start_btn:
            self._update_start_btn()

    def _update_start_btn(self):
        if self._mode == "Своя практика" and not self._selected_asanas:
            self._start_btn.setEnabled(False)
        else:
            self._start_btn.setEnabled(True)

    def _start(self):
        selected = getattr(self, '_selected_asanas', None)
        self.parent.show_practice_run()
        self.parent.practice_screen.start(
            level=self._level,
            mode=self._mode,
            total_minutes=self._duration,
            hold_seconds=self._hold,
            filters=self._filters if self._filters else None,
            auto=self._auto,
            selected_asana_names=selected,
        )