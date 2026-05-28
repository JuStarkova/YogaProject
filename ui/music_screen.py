from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSlider,
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os

TRACKS = [
    # Спокойная
    {"title": "Спокойное утро",        "mood": "Спокойная",  "duration": "5:00", "filename": "calm_morning.mp3"},
    {"title": "Мягкий поток",          "mood": "Спокойная",  "duration": "5:30", "filename": "soft_flow.mp3"},
    {"title": "Тихий рассвет",         "mood": "Спокойная",  "duration": "6:00", "filename": "quiet_dawn.mp3"},
    {"title": "Речной берег",          "mood": "Спокойная",  "duration": "7:00", "filename": "river_bank.mp3"},
    {"title": "Утренняя роса",         "mood": "Спокойная",  "duration": "5:20", "filename": "morning_dew.mp3"},
    {"title": "Лесная прогулка",       "mood": "Спокойная",  "duration": "6:30", "filename": "forest_walk.mp3"},
    # Медитация
    {"title": "Медитация",             "mood": "Медитация",  "duration": "7:00", "filename": "meditation.mp3"},
    {"title": "Природа и тишина",      "mood": "Медитация",  "duration": "6:00", "filename": "nature.mp3"},
    {"title": "Глубокое расслабление", "mood": "Медитация",  "duration": "8:00", "filename": "deep_relax.mp3"},
    {"title": "Тибетские чаши",        "mood": "Медитация",  "duration": "9:00", "filename": "tibetan_bowls.mp3"},
    {"title": "Дыхание океана",        "mood": "Медитация",  "duration": "8:30", "filename": "ocean_breath.mp3"},
    {"title": "Внутренний покой",      "mood": "Медитация",  "duration": "10:00","filename": "inner_peace.mp3"},
    {"title": "Звуки дождя",           "mood": "Медитация",  "duration": "7:30", "filename": "rain_sounds.mp3"},
    # Энергичная
    {"title": "Энергия утра",          "mood": "Энергичная", "duration": "4:30", "filename": "morning_energy.mp3"},
    {"title": "Солнечный поток",       "mood": "Энергичная", "duration": "5:00", "filename": "sun_flow.mp3"},
    {"title": "Виньяса",               "mood": "Энергичная", "duration": "4:00", "filename": "vinyasa.mp3"},
    {"title": "Огонь внутри",          "mood": "Энергичная", "duration": "5:30", "filename": "inner_fire.mp3"},
    {"title": "Ритм земли",            "mood": "Энергичная", "duration": "4:45", "filename": "earth_rhythm.mp3"},
    {"title": "Пробуждение",           "mood": "Энергичная", "duration": "5:15", "filename": "awakening.mp3"},
]

MOOD_COLORS = {
    "Спокойная":  ("#dbeeff", "#1a5c9a"),
    "Медитация":  ("#ede8ff", "#4a2ea0"),
    "Энергичная": ("#fff0d8", "#a05a00"),
}


def _play_btn_style(active=False):
    if active:
        return """
            QPushButton {
                background: #a0524f; color: white;
                border-radius: 14px; font-size: 14px;
                font-weight: 700; border: none; padding: 9px 18px;
                min-width: 88px;
            }
            QPushButton:hover { background: #8a3f3c; }
        """
    return """
        QPushButton {
            background: #7a5c3a; color: white;
            border-radius: 14px; font-size: 14px;
            font-weight: 700; border: none; padding: 9px 18px;
            min-width: 88px;
        }
        QPushButton:hover { background: #5e4328; }
    """


def _filter_btn_style(active=False):
    if active:
        return """
            QPushButton {
                background: #7a5c3a; color: white;
                border-radius: 10px; font-size: 14px;
                font-weight: 700; border: 2px solid #7a5c3a;
                padding: 9px 20px;
            }
        """
    return """
        QPushButton {
            background: white; color: #2b2b2b;
            border-radius: 10px; font-size: 14px;
            font-weight: 600; border: 2px solid #c0b090;
            padding: 9px 20px;
        }
        QPushButton:hover { background: #f5ede0; border: 2px solid #7a5c3a; }
    """


class MusicScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setStyleSheet("""
            MusicScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:0.4, y2:1,
                    stop:0 #fdf8f2, stop:1 #f0e8dc
                );
            }
        """)

        self._current_index = None
        self._active_filter = None
        self._track_cards = []
        self._filter_btns = {}

        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.7)
        
        # Фикс автоматического переключения: отслеживаем завершение медиафайла, а не смену состояний плеера
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.durationChanged.connect(self._on_duration_changed)

        self._progress_timer = QTimer()
        self._progress_timer.setInterval(500)
        self._progress_timer.timeout.connect(self._update_progress)

        self._base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Шапка
        header = QWidget()
        header.setStyleSheet("background: rgba(253,248,242,0.97); border-bottom: 1.5px solid #e0d0bc;")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(28, 16, 28, 12)
        hl.setSpacing(10)

        title_row = QHBoxLayout()
        title = QLabel("Музыка для практики")
        title.setStyleSheet("font-family: Georgia, serif; font-size: 24px; font-weight: bold; color: #2b2b2b;")
        title_row.addWidget(title)
        title_row.addStretch()

        # Фикс кнопки Назад: перенаправляем на экран настройки практики
        back_btn = QPushButton("Назад")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #a0524f; color: white;
                border-radius: 10px; padding: 9px 22px;
                font-size: 14px; font-weight: 700; border: none;
            }
            QPushButton:hover { background: #8a3f3c; }
        """)
        back_btn.clicked.connect(self.parent.show_main_menu)
        title_row.addWidget(back_btn)
        hl.addLayout(title_row)

        # Фильтры
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        for label, key in [("Все", None), ("Спокойная", "Спокойная"),
                            ("Медитация", "Медитация"), ("Энергичная", "Энергичная")]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(_filter_btn_style(active=(key is None)))
            btn.clicked.connect(lambda _, k=key, b=btn: self._apply_filter(k, b))
            self._filter_btns[key] = btn
            filter_row.addWidget(btn)

        filter_row.addStretch()
        hl.addLayout(filter_row)
        root.addWidget(header)

        # Список
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(24, 14, 24, 14)
        self._list_layout.setSpacing(8)

        self._populate_list(TRACKS)
        scroll.setWidget(self._list_widget)
        root.addWidget(scroll)

        # Нижний плеер
        self._player_bar = QWidget()
        self._player_bar.setStyleSheet("""
            background: white;
            border-top: 2px solid #e0d0bc;
        """)
        self._player_bar.setVisible(False)
        pb = QVBoxLayout(self._player_bar)
        pb.setContentsMargins(24, 8, 24, 12)
        pb.setSpacing(6)

        # Прогресс
        progress_row = QHBoxLayout()
        self._pos_label = QLabel("0:00")
        self._pos_label.setStyleSheet("font-size: 12px; color: #888; min-width: 35px;")
        self._progress_slider = QSlider(Qt.Orientation.Horizontal)
        self._progress_slider.setRange(0, 1000)
        self._progress_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 5px; background: #e0d0bc; border-radius: 2px; }
            QSlider::handle:horizontal { width: 14px; height: 14px; background: #7a5c3a; border-radius: 7px; margin: -5px 0; }
            QSlider::sub-page:horizontal { background: #7a5c3a; border-radius: 2px; }
        """)
        self._progress_slider.sliderMoved.connect(self._seek)
        self._dur_label = QLabel("0:00")
        self._dur_label.setStyleSheet("font-size: 12px; color: #888; min-width: 35px; qproperty-alignment: AlignRight;")
        progress_row.addWidget(self._pos_label)
        progress_row.addWidget(self._progress_slider)
        progress_row.addWidget(self._dur_label)
        pb.addLayout(progress_row)

        # Контролы
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        info_col = QVBoxLayout()
        self._now_title = QLabel("Ничего не играет")
        self._now_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #2b2b2b;")
        self._now_mood = QLabel("")
        self._now_mood.setStyleSheet("font-size: 12px; color: #888;")
        info_col.addWidget(self._now_title)
        info_col.addWidget(self._now_mood)
        ctrl_row.addLayout(info_col)
        ctrl_row.addStretch()

        ctrl_btn_style = """
            QPushButton {
                background: #f0e8dc; color: #2b2b2b;
                border: 1.5px solid #c0b090; border-radius: 10px;
                font-size: 15px; font-weight: 700; padding: 7px 14px;
            }
            QPushButton:hover { background: #e0d0bc; }
        """

        self._prev_ctrl = QPushButton("|<")
        self._prev_ctrl.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_ctrl.setStyleSheet(ctrl_btn_style)
        self._prev_ctrl.clicked.connect(self._prev_track)

        self._play_ctrl = QPushButton("||")
        self._play_ctrl.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_ctrl.setStyleSheet("""
            QPushButton {
                background: #7a5c3a; color: white;
                border-radius: 16px; font-size: 16px;
                padding: 8px 18px; border: none; font-weight: bold;
            }
            QPushButton:hover { background: #5e4328; }
        """)
        self._play_ctrl.clicked.connect(self._toggle_play)

        self._next_ctrl = QPushButton(">|")
        self._next_ctrl.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_ctrl.setStyleSheet(ctrl_btn_style)
        self._next_ctrl.clicked.connect(self._next_track)

        ctrl_row.addWidget(self._prev_ctrl)
        ctrl_row.addWidget(self._play_ctrl)
        ctrl_row.addWidget(self._next_ctrl)
        ctrl_row.addSpacing(16)

        vol_label = QLabel("Громкость")
        vol_label.setStyleSheet("font-size: 12px; color: #888;")
        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setFixedWidth(100)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(70)
        self._vol_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 5px; background: #e0d0bc; border-radius: 2px; }
            QSlider::handle:horizontal { width: 14px; height: 14px; background: #7a5c3a; border-radius: 7px; margin: -5px 0; }
            QSlider::sub-page:horizontal { background: #7a5c3a; border-radius: 2px; }
        """)
        self._vol_slider.valueChanged.connect(self._change_volume)
        ctrl_row.addWidget(vol_label)
        ctrl_row.addWidget(self._vol_slider)

        pb.addLayout(ctrl_row)
        root.addWidget(self._player_bar)

    # ── Список ─────────────────────────────────────────────────────────────

    def _populate_list(self, tracks):
        for i in reversed(range(self._list_layout.count())):
            item = self._list_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        self._track_cards.clear()

        for track in tracks:
            real_idx = TRACKS.index(track)
            card = self._make_card(track, real_idx)
            self._track_cards.append((real_idx, card))
            self._list_layout.addWidget(card)

        self._list_layout.addStretch()

    def _make_card(self, track, real_idx):
        card = QFrame()
        # Стандартный стиль карточки — БЕЗ жесткой коричневой обводки
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.82);
                border-radius: 12px;
                border: 1px solid #e0d0bc;
            }
        """)

        hl = QHBoxLayout(card)
        hl.setContentsMargins(16, 12, 16, 12)
        hl.setSpacing(14)

        num = QLabel(str(real_idx + 1))
        num.setFixedWidth(22)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet("font-size: 13px; color: #aaa; border: none; background: transparent;")
        hl.addWidget(num)

        info = QVBoxLayout()
        info.setSpacing(4)

        title_lbl = QLabel(track["title"])
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1a1a1a; border: none; background: transparent;")
        info.addWidget(title_lbl)

        mood_row = QHBoxLayout()
        mood_row.setSpacing(8)
        bg, fg = MOOD_COLORS.get(track["mood"], ("#eee", "#555"))
        mood_lbl = QLabel(track["mood"])
        mood_lbl.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 7px;"
            f" padding: 2px 10px; font-size: 12px; font-weight: 700; border: none;"
        )
        dur_lbl = QLabel(track["duration"])
        dur_lbl.setStyleSheet("font-size: 12px; color: #888; border: none; background: transparent;")
        mood_row.addWidget(mood_lbl)
        mood_row.addWidget(dur_lbl)
        mood_row.addStretch()
        info.addLayout(mood_row)

        hl.addLayout(info)
        hl.addStretch()

        play_btn = QPushButton("Играть")
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setStyleSheet(_play_btn_style(active=False))
        play_btn.clicked.connect(lambda _, i=real_idx: self._toggle_track(i))
        hl.addWidget(play_btn)

        card._play_btn = play_btn
        card._track_idx = real_idx
        return card

    # ── Воспроизведение ────────────────────────────────────────────────────

    def _toggle_track(self, idx):
        if self._current_index == idx:
            if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self._player.pause()
            else:
                self._player.play()
        else:
            self._play_track(idx)

    def _play_track(self, idx):
        track = TRACKS[idx]
        path = os.path.join(self._base_dir, "assets", "music", track["filename"])
        self._current_index = idx

        if not os.path.exists(path):
            self._now_title.setText(f"Файл не найден: {track['filename']}")
            self._now_mood.setText("Добавьте файл в assets/music/")
            self._player_bar.setVisible(True)
            self._update_card_states()
            return

        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()

        self._now_title.setText(track["title"])
        self._now_mood.setText(track["mood"] + "  •  " + track["duration"])
        self._player_bar.setVisible(True)

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            if self._current_index is None and TRACKS:
                self._play_track(0)
            else:
                self._player.play()

    # Фикс перелистывания: перелистываем строго внутри отфильтрованного (видимого на экране) списка
    def _prev_track(self):
        if self._current_index is None or not self._track_cards:
            return
        displayed_indices = [real_idx for real_idx, _ in self._track_cards]
        if self._current_index in displayed_indices:
            current_pos = displayed_indices.index(self._current_index)
            next_pos = (current_pos - 1) % len(displayed_indices)
            self._play_track(displayed_indices[next_pos])
        else:
            self._play_track(displayed_indices[-1])

    def _next_track(self):
        if self._current_index is None or not self._track_cards:
            return
        displayed_indices = [real_idx for real_idx, _ in self._track_cards]
        if self._current_index in displayed_indices:
            current_pos = displayed_indices.index(self._current_index)
            next_pos = (current_pos + 1) % len(displayed_indices)
            self._play_track(displayed_indices[next_pos])
        else:
            self._play_track(displayed_indices[0])

    def _seek(self, value):
        dur = self._player.duration()
        if dur > 0:
            self._player.setPosition(int(dur * value / 1000))

    def _change_volume(self, value):
        self._audio_output.setVolume(value / 100.0)

    # Фикс автоматического перехода: срабатывает строго по окончанию файла
    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._current_index is not None:
            self._next_track()

    # Синхронизация состояний интерфейса при воспроизведении/паузе
    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_ctrl.setText("||")
            self._progress_timer.start()
        else:
            self._play_ctrl.setText("▶")
            self._progress_timer.stop()
        self._update_card_states()

    def _on_duration_changed(self, dur):
        if dur > 0:
            m, s = dur // 60000, (dur % 60000) // 1000
            self._dur_label.setText(f"{m}:{s:02d}")

    def _update_progress(self):
        pos = self._player.position()
        dur = self._player.duration()
        if dur > 0:
            self._progress_slider.setValue(int(pos * 1000 / dur))
            m, s = pos // 60000, (pos % 60000) // 1000
            self._pos_label.setText(f"{m}:{s:02d}")

    # Фикс индикации нажатия кнопки: подсвечиваем активную карточку мягким фоном и меняем кнопку, без коричневых рамок
    def _update_card_states(self):
        is_playing = self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        for real_idx, card in self._track_cards:
            btn = card._play_btn
            if real_idx == self._current_index:
                btn.setText("Стоп" if is_playing else "Играть")
                btn.setStyleSheet(_play_btn_style(active=is_playing))
                card.setStyleSheet("""
                    QFrame {
                        background: #f5ede0;
                        border-radius: 12px;
                        border: 1px solid #c0b090;
                    }
                """)
            else:
                btn.setText("Играть")
                btn.setStyleSheet(_play_btn_style(active=False))
                card.setStyleSheet("""
                    QFrame {
                        background: rgba(255,255,255,0.82);
                        border-radius: 12px;
                        border: 1px solid #e0d0bc;
                    }
                """)

    # ── Фильтры ────────────────────────────────────────────────────────────

    def _apply_filter(self, mood, btn):
        for k, b in self._filter_btns.items():
            b.setStyleSheet(_filter_btn_style(active=(k == mood)))
        filtered = TRACKS if mood is None else [t for t in TRACKS if t["mood"] == mood]
        self._populate_list(filtered)
        self._update_card_states()