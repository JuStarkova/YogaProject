import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, QTimer

from logic.practice_generator import generate_practice


class PracticeScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setStyleSheet("""
            PracticeScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f0e8,
                    stop:1 #c8dcc8
                );
            }
        """)

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(6)
        self.setLayout(root)

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        top_panel = QHBoxLayout()

        self.counter_label = QLabel("0 / 0")
        self.counter_label.setStyleSheet("font-size: 14px; color: #2b3d2b; font-weight: 600;")

        self.phase_label = QLabel("")
        self.phase_label.setStyleSheet("font-size: 14px; color: #5a7d5a; font-weight: 500;")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("00:30")
        self.timer_label.setStyleSheet("font-size: 28px; color: #3d5a3d; font-weight: bold; font-family: monospace;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_panel.addWidget(self.counter_label)
        top_panel.addWidget(self.phase_label)
        top_panel.addWidget(self.timer_label)
        root.addLayout(top_panel)

        # === КАРТИНКА АСАНЫ ===
        self.image_label = QLabel()
        self.image_label.setMinimumSize(280, 280)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.2);
        """)
        root.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_ru_label = QLabel("")
        self.name_ru_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #2b3d2b; margin-top: 2px;")
        self.name_ru_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.name_ru_label)

        self.name_en_label = QLabel("")
        self.name_en_label.setStyleSheet("font-size: 15px; font-style: italic; color: #5a7d5a;")
        self.name_en_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.name_en_label)

        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 13px; color: #2b3d2b; padding: 0 15px; line-height: 120%;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.desc_label)

        # === НАВИГАЦИЯ (Компактные кнопки) ===
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nav_style = """
            QPushButton {
                font-size: 16px; border-radius: 12px; 
                background-color: #5a7d5a; color: white; font-weight: 600;
            }
            QPushButton:hover { background-color: rgba(90, 125, 90, 0.8); }
        """

        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedSize(50, 36)
        self.prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_btn.setStyleSheet(nav_style)
        self.prev_btn.clicked.connect(self.prev_asana)

        self.next_btn = QPushButton(">")
        self.next_btn.setFixedSize(50, 36)
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.setStyleSheet(nav_style)
        self.next_btn.clicked.connect(self.next_asana)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        root.addLayout(nav_layout)

        # === КНОПКИ УПРАВЛЕНИЯ ===
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pause_btn = QPushButton("Пауза")
        self.pause_btn.setFixedSize(110, 36)
        self.pause_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pause_btn.setStyleSheet(self._pause_style())
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.back_btn = QPushButton("Завершить")
        self.back_btn.setFixedSize(110, 36)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setStyleSheet(self._red_style())
        self.back_btn.clicked.connect(self.stop_practice_manually)

        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.back_btn)
        root.addLayout(control_layout)

        # === СОСТОЯНИЕ ===
        self.practice = []
        self.index = 0
        self.time_left = 0
        self.hold_seconds = 30
        self.is_paused = False
        self.auto_mode = True
        self.finish_widget = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

    def _pause_style(self):
        return """
            QPushButton {
                font-size: 14px; border-radius: 12px;
                background-color: rgba(255,255,255,0.6); color: #2b3d2b; font-weight: 500;
                border: 1.5px solid rgba(90,125,90,0.3);
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.85); }
        """

    def _continue_style(self):
        return """
            QPushButton {
                font-size: 14px; border-radius: 12px;
                background-color: #5a7d5a; color: white; font-weight: 500;
            }
            QPushButton:hover { background-color: rgba(90, 125, 90, 0.8); }
        """

    def _red_style(self):
        return """
            QPushButton {
                font-size: 14px; border-radius: 12px;
                background-color: #a0524f; color: white; font-weight: 500;
            }
            QPushButton:hover { background-color: rgba(160,82,79,0.8); }
        """

    def start(self, level, mode, total_minutes, hold_seconds, filters, auto, selected_asana_names=None):
        self.hold_seconds = hold_seconds
        self.auto_mode = auto

        if self.finish_widget:
            self.finish_widget.hide()

        self._show_elements()
        self.back_btn.setText("Завершить")
        self.back_btn.setStyleSheet(self._red_style())
        try:
            self.back_btn.clicked.disconnect()
        except Exception:
            pass
        self.back_btn.clicked.connect(self.stop_practice_manually)
        self.back_btn.show()

        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Пауза")
        self.pause_btn.setStyleSheet(self._pause_style())

        # selected_asana_names учитываем ТОЛЬКО в режиме "Своя практика"
        if mode == "Своя практика" and selected_asana_names:
            from utils.data_loader import load_asanas
            all_asanas = load_asanas()
            # Сохраняем порядок как задал пользователь
            name_map = {a.get("name"): a for a in all_asanas}
            chosen = [name_map[n] for n in selected_asana_names if n in name_map]
            if len(chosen) >= 3:
                self.practice = chosen
            else:
                self.practice = generate_practice(level, total_minutes, hold_seconds, filters)
        elif mode == "Готовая практика":
            self.practice = generate_practice(level, total_minutes, hold_seconds)
        else:
            self.practice = generate_practice(level, total_minutes, hold_seconds, filters)

        if not self.practice:
            return

        # Гарантированный запуск музыки строго ПЕРЕД началом первой асаны
        self.manage_music()

        self.index = 0
        self.is_paused = False
        self.show_asana()
        
        # Устанавливаем время один раз для стартовой асаны
        self.time_left = self.hold_seconds
        self._update_timer()
        
        self.timer.start(1000)

    def manage_music(self):
        """Запуск музыки при старте комплекса"""
        try:
            if not hasattr(self.parent, 'practice_setup') or not hasattr(self.parent, 'music_screen'):
                return
                
            setup = self.parent.practice_setup
            music_screen = self.parent.music_screen
            
            if hasattr(setup, '_music') and setup._music != "Без музыки" and hasattr(music_screen, '_player'):
                from PyQt6.QtMultimedia import QMediaPlayer
                if music_screen._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    from ui.music_screen import TRACKS
                        
                    for i, track in enumerate(TRACKS):
                        if track.get("mood") == setup._music:
                            if hasattr(music_screen, '_play_track'):
                                music_screen._play_track(i)
                            elif hasattr(music_screen, 'play_track'):
                                music_screen.play_track(i)
                            break
        except Exception as e:
            print(f"Фоновая музыка не запустилась: {e}")

    def stop_music(self):
        """Полная остановка трека при выходе или завершении комплекса"""
        try:
            if hasattr(self.parent, 'music_screen') and hasattr(self.parent.music_screen, '_player'):
                self.parent.music_screen._player.stop()
        except Exception as e:
            print(f"Не удалось остановить музыку: {e}")

    def _show_elements(self):
        for w in [self.counter_label, self.phase_label, self.timer_label,
                  self.image_label, self.name_ru_label, self.name_en_label,
                  self.desc_label, self.prev_btn, self.next_btn,
                  self.pause_btn, self.back_btn]:
            w.show()

    def show_asana(self):
        if not self.practice:
            return

        asana = self.practice[self.index]
        total = len(self.practice)
        self.counter_label.setText(f"{self.index + 1} / {total}")

        warmup_end = max(1, int(total * 0.15))
        cool_start = total - max(1, int(total * 0.15))

        if self.index < warmup_end:
            phase = "Разминка"
        elif self.index >= cool_start:
            phase = "Заминка"
        else:
            phase = "Основная часть"
        self.phase_label.setText(phase)

        self.name_ru_label.setText(asana.get("ru_name", asana.get("name", "")))
        self.name_en_label.setText(asana.get("name", ""))
        self.desc_label.setText(asana.get("description", ""))

        image_name = asana.get("image", "")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "assets", "images", image_name) if image_name else ""

        pixmap = QPixmap(image_path)
        target = min(self.width() - 80, 320)
        if not pixmap.isNull():
            self.image_label.setPixmap(
                pixmap.scaled(target, target, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.image_label.setText("Изображение отсутствует")

    def tick(self):
        if self.is_paused:
            return
        self.time_left -= 1
        self._update_timer()
        if self.time_left <= 0:
            if self.auto_mode:
                self.next_asana()
            else:
                self.time_left = self.hold_seconds
                self._update_timer()

    def _update_timer(self):
        m, s = self.time_left // 60, self.time_left % 60
        self.timer_label.setText(f"{m:02d}:{s:02d}")
        c = "#a0524f" if self.time_left <= 5 else "#3d5a3d"
        self.timer_label.setStyleSheet(f"font-size: 28px; color: {c}; font-weight: bold; font-family: monospace;")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.setText("Продолжить")
            self.pause_btn.setStyleSheet(self._continue_style())
            try: self.parent.music_screen._player.pause()
            except Exception: pass
        else:
            self.pause_btn.setText("Пауза")
            self.pause_btn.setStyleSheet(self._pause_style())
            try: self.parent.music_screen._player.play()
            except Exception: pass

    def next_asana(self):
        if self.index < len(self.practice) - 1:
            self.index += 1
            self.show_asana()
            self.time_left = self.hold_seconds
            self._update_timer()
        else:
            self.finish_practice()

    def prev_asana(self):
        if self.index > 0:
            self.index -= 1
            self.show_asana()
            self.time_left = self.hold_seconds
            self._update_timer()

    # ── ЗАВЕРШЕНИЕ И ВЫХОД ──────────────────────────────────────────────────

    def stop_practice_manually(self):
        """Вызывается при нажатии на кнопку 'Завершить' во время выполнения"""
        self.timer.stop()
        self.stop_music()  # Музыка гасится при принудительном выходе
        self.finish_practice()  # Переходим к окну итогов

    def finish_practice(self):
        """Перевод экрана в режим отображения итоговой карточки"""
        self.timer.stop()
        self.stop_music()  # Музыка гасится при успешном завершении комплекса

        total_asanas = len(self.practice)
        minutes_done = max(1, (total_asanas * self.hold_seconds) // 60)
        hold_sec = self.hold_seconds

        for w in [self.counter_label, self.phase_label, self.timer_label,
                  self.image_label, self.name_ru_label, self.name_en_label,
                  self.desc_label, self.prev_btn, self.next_btn,
                  self.pause_btn, self.back_btn]:
            w.hide()

        if self.finish_widget:
            self.finish_widget.deleteLater()
            self.finish_widget = None

        self._build_finish_overlay(total_asanas, minutes_done, hold_sec)
        self.finish_widget.setGeometry(0, 0, self.width(), self.height())
        self.finish_widget.show()
        self.finish_widget.raise_()

    def _build_finish_overlay(self, total_asanas, minutes_done, hold_sec):
        overlay = QWidget(self)
        overlay.setStyleSheet("background: rgba(240, 245, 240, 0.98);")
        self.finish_widget = overlay

        outer = QVBoxLayout(overlay)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(30, 20, 30, 20)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet("QFrame { background: white; border-radius: 24px; border: none; }")
        
        cl = QVBoxLayout(card)
        cl.setSpacing(14)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Практика завершена!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-family: Georgia, serif;
            font-size: 24px; font-weight: bold;
            color: #2b3d2b; background: transparent; border: none;
        """)
        cl.addWidget(title)

        sub = QLabel("Отличная работа!  Practice complete")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("font-size: 13px; color: #5a7d5a; font-style: italic; background: transparent; border: none;")
        cl.addWidget(sub)

        # Модуль статистики (без рамок)
        stats = QFrame()
        stats.setStyleSheet("background: transparent; border: none;")
        sl = QHBoxLayout(stats)
        sl.setContentsMargins(0, 10, 0, 10)
        sl.setSpacing(0)

        def stat_block(number, label):
            w = QWidget()
            w.setStyleSheet("background: transparent; border: none;")
            vl = QVBoxLayout(w)
            vl.setSpacing(1)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n = QLabel(str(number))
            n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n.setStyleSheet("font-size: 26px; font-weight: bold; color: #2b3d2b; border: none;")
            l = QLabel(label)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setStyleSheet("font-size: 12px; color: #7a9a7a; font-weight: 500; border: none;")
            vl.addWidget(n)
            vl.addWidget(l)
            return w

        def divider():
            d = QLabel("  ·  ")
            d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            d.setStyleSheet("color: #c8dcc8; font-size: 22px; font-weight: bold; border: none; background: transparent;")
            return d

        sl.addWidget(stat_block(total_asanas, "асан"))
        sl.addWidget(divider())
        sl.addWidget(stat_block(f"~{minutes_done}", "минут"))
        sl.addWidget(divider())
        sl.addWidget(stat_block(hold_sec, "сек/поза"))
        cl.addWidget(stats)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: none; border-top: 1px solid rgba(90,125,90,0.1); background: transparent;")
        cl.addWidget(sep)

        desc = QLabel(
            "Возвращайтесь к занятиям регулярно для\n"
            "достижения наилучших результатов."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 13px; color: #4a5c4a; background: transparent; border: none;")
        cl.addWidget(desc)

        btn_again = QPushButton("Практиковаться снова")
        btn_again.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_again.setFixedSize(220, 38)
        btn_again.setStyleSheet("""
            QPushButton {
                background-color: #5a7d5a; color: white;
                border-radius: 12px; font-size: 14px; font-weight: 600; border: none;
            }
            QPushButton:hover { background-color: rgba(90,125,90,0.85); }
        """)
        btn_again.clicked.connect(self.go_back_to_setup)
        cl.addWidget(btn_again)

        btn_menu = QPushButton("В главное меню")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.setFixedSize(220, 38)
        btn_menu.setStyleSheet("""
            QPushButton {
                background-color: #a0524f; color: white;
                border-radius: 12px; font-size: 14px; font-weight: 600; border: none;
            }
            QPushButton:hover { background-color: rgba(160,82,79,0.85); }
        """)
        btn_menu.clicked.connect(self.parent.show_main_menu)
        cl.addWidget(btn_menu)

        outer.addWidget(card)

    def go_back_to_setup(self):
        if self.finish_widget:
            self.finish_widget.hide()
        self._show_elements()
        self.pause_btn.setEnabled(True)
        self.parent.show_practice_setup()

    def go_back(self):
        self.timer.stop()
        self.stop_music()
        if self.finish_widget:
            self.finish_widget.hide()
        self._show_elements()
        # Сбрасываем выбранные асаны после завершения практики
        if hasattr(self.parent, 'practice_setup'):
            self.parent.practice_setup.set_selected_asanas(None)
        self.parent.show_practice_setup()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.finish_widget and self.finish_widget.isVisible():
            self.finish_widget.setGeometry(0, 0, self.width(), self.height())