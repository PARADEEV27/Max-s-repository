import os
import sys
import random
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
try:
    # Ensure Qt knows where to look for its plugins (including the xcb platform plugin)
    from PyQt5 import Qt as _QtModule
    from PyQt5.QtCore import QLibraryInfo
    candidates = []
    try:
        # System Qt plugins dir
        sys_plugins = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        if sys_plugins:
            candidates.append(Path(sys_plugins))
    except Exception:
        pass
    try:
        # PyQt5 wheel-bundled plugins locations
        pyqt_dir = Path(_QtModule.__file__).resolve().parent
        for sub in ("Qt5/plugins", "Qt/plugins", "plugins"):
            p = pyqt_dir / sub
            if p.exists():
                candidates.append(p)
    except Exception:
        pass
    # Prefer a path containing 'platforms'
    chosen = None
    for base in candidates:
        platforms = base / "platforms"
        if platforms.exists():
            chosen = platforms
            break
    if chosen and not os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"):
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(chosen)
    if not os.environ.get("QT_QPA_PLATFORM"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"
except Exception:
    pass

class SeekSlider(QtWidgets.QSlider):
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        # Запрещаем взаимодействие с ползунком
        event.ignore()
        # Можно просто вызвать родительский метод без дополнительной логики
        super().mousePressEvent(event)


try:
    import pygame
    pygame.mixer.init()
except Exception:
    pygame = None

try:
    from mutagen import File as MutagenFile
except Exception:
    MutagenFile = None


APP_TITLE = "SoundKISS beta"
WORKDIR = Path(__file__).resolve().parent
ASSET_IMAGE_MAIN = WORKDIR / "image1.png"
ASSET_IMAGE_FALLBACK = WORKDIR / "image2.png"
print(f"Путь к fallback обложке: {ASSET_IMAGE_FALLBACK}")
print(f"Файл существует: {ASSET_IMAGE_FALLBACK.exists()}")
ASSET_IMAGE_GAME = WORKDIR / "image3.png"
ASSET_IMAGE_FARM = WORKDIR / "image4.png"  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
ASSET_SFX_POP = WORKDIR / "bulp.mp3"
ASSET_SFX_WHEEL = WORKDIR / "koleso.mp3"
ASSET_MUSIC_BUBBLE = WORKDIR / "Bubble_rain_game.mp3"
SOUNDS_DIR = WORKDIR / "Sounds"
SECRET_MUSIC_DIR = WORKDIR / "SecretMusic"  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
ASSET_IMAGE_PIANO = WORKDIR / "piano_image.png"  # ← ДОБАВИТЬ ЭТУ СТРОКУ
ASSET_IMAGE_XYLOPHONE = WORKDIR / "xylophone_image.png"  # ← ДОБАВИТЬ ЭТУ СТРОКУ

def load_qpixmap(path: Path) -> QtGui.QPixmap:
    print(f"Загрузка изображения: {path}")
    if path.exists():
        pixmap = QtGui.QPixmap(str(path))
        if not pixmap.isNull():
            print("Изображение загружено успешно")
            return pixmap
        else:
            print("Ошибка: изображение не загружено (неверный формат?)")
    else:
        print(f"Ошибка: файл не существует: {path}")
    
    # Создаем простую картинку если файл не найден
    pixmap = QtGui.QPixmap(300, 300)
    pixmap.fill(QtGui.QColor("#444"))
    painter = QtGui.QPainter(pixmap)
    painter.setPen(QtGui.QPen(QtGui.QColor("#fff")))
    painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, f"{path.name}\n(файл не найден)")
    painter.end()
    return pixmap

class ConfirmExitDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Question)
        self.setWindowTitle("Выход")
        self.setText("Вы уверены, что хотите выйти?")
        yes_btn = self.addButton("Да, выйти", QtWidgets.QMessageBox.AcceptRole)
        _ = self.addButton("Нет, остаться", QtWidgets.QMessageBox.RejectRole)
        self.setDefaultButton(yes_btn)

class MainMenu(QtWidgets.QWidget):
    navigateTo = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # Добавляем фокус

        left_buttons = QtWidgets.QVBoxLayout()
        left_buttons.setSpacing(12)
        left_buttons.addStretch()

        self.player_btn = QtWidgets.QPushButton("Музыкальный плеер")
        self.soundpad_btn = QtWidgets.QPushButton("Саундпад")
        self.game_btn = QtWidgets.QPushButton("Игры")
        for b in (self.player_btn, self.soundpad_btn, self.game_btn):
            b.setMinimumHeight(64)
            b.setStyleSheet("font-size: 16px;")
            b.setFocusPolicy(QtCore.Qt.NoFocus)  # Отключаем фокус для кнопок
        for btn in (self.player_btn, self.soundpad_btn, self.game_btn):
            btn.setMinimumHeight(44)
            left_buttons.addWidget(btn)
        left_buttons.addStretch()

        self.player_btn.clicked.connect(lambda: self.navigateTo.emit("player"))
        self.soundpad_btn.clicked.connect(lambda: self.navigateTo.emit("soundpad"))
        self.game_btn.clicked.connect(lambda: self.navigateTo.emit("wheel"))

        right = QtWidgets.QVBoxLayout()
        hero = QtWidgets.QLabel()
        hero.setPixmap(load_qpixmap(ASSET_IMAGE_MAIN).scaled(640, 360, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        hero.setAlignment(QtCore.Qt.AlignCenter)
        right.addWidget(hero, 1)

        credit = QtWidgets.QLabel("prod. by Gapotchenko Max.")
        credit.setAlignment(QtCore.Qt.AlignCenter)
        right.addWidget(credit)

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addStretch()
        exit_btn = QtWidgets.QPushButton("Выйти")
        exit_btn.setFocusPolicy(QtCore.Qt.NoFocus)  # Отключаем фокус для кнопки выхода
        top_bar.addWidget(exit_btn)
        exit_btn.clicked.connect(self.confirm_exit)

        main = QtWidgets.QGridLayout(self)
        main.addLayout(top_bar, 0, 0, 1, 2)
        main.addLayout(left_buttons, 1, 0)
        main.addLayout(right, 1, 1)
        main.setColumnStretch(-3, 10)

        # Rainbow hover effect for "Игра"
        self.game_btn.installEventFilter(self)
        self._rainbow_timer = QtCore.QTimer(self)
        self._rainbow_timer.timeout.connect(self._tick_rainbow)
        self._hue = 0

    def eventFilter(self, obj, event):
        if obj is self.game_btn:
            if event.type() == QtCore.QEvent.Enter:
                self._rainbow_timer.start(50)
            elif event.type() == QtCore.QEvent.Leave:
                self._rainbow_timer.stop()
                self.game_btn.setStyleSheet("")
        return super().eventFilter(obj, event)

    def _tick_rainbow(self):
        self._hue = (self._hue + 5) % 360
        color = QtGui.QColor()
        color.setHsv(self._hue, 255, 255)
        self.game_btn.setStyleSheet(f"background-color: {color.name()}; color: black; font-weight: bold;")

    def confirm_exit(self):
        dlg = ConfirmExitDialog(self)
        if dlg.exec_() == QtWidgets.QMessageBox.AcceptRole:
            QtWidgets.QApplication.quit()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # Игнорируем все клавиши, включая пробел и стрелки
        event.ignore()

class BackTopBar(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self, title: str):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        back_btn = QtWidgets.QPushButton("Назад")
        back_btn.setFocusPolicy(QtCore.Qt.NoFocus)  # Отключаем фокус
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(back_btn)
        layout.addStretch(1)
        layout.addWidget(title_lbl)
        layout.addStretch(10)
        back_btn.clicked.connect(self.goBack.emit)

class MusicPlayerWidget(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.playlist: list[Path] = []
        self.current_index: int = -1
        self.random_mode: bool = False
        self.user_stopped: bool = False
        self.paused: bool = False
        self.current_length_s: float | None = None
        self.current_track_path: Path | None = None
        self.last_position: float = 0.0
        self.is_active = False
        self.was_playing_before_exit = False

        top = BackTopBar("Музыкальный плеер")
        top.goBack.connect(self._on_go_back)

        # Left: tracklist + search + load button
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Поиск треков...")
        self.search_edit.textChanged.connect(self._filter_tracks)

        self.track_list = QtWidgets.QListWidget()
        self.track_list.itemDoubleClicked.connect(self._play_selected)

        # Кнопки управления плейлистом
        load_btn = QtWidgets.QPushButton("Загрузить треки")
        load_btn.clicked.connect(self._add_tracks)
        
        library_btn = QtWidgets.QPushButton("Встроенная музыка")
        library_btn.clicked.connect(self._load_library_music)
        
        clear_btn = QtWidgets.QPushButton("Очистить")
        clear_btn.clicked.connect(self._clear_playlist)

        # Layout для кнопок
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(load_btn)
        button_layout.addWidget(library_btn)
        button_layout.addWidget(clear_btn)

        left = QtWidgets.QVBoxLayout()
        left.addWidget(self.search_edit)
        left.addWidget(self.track_list, 1)
        left.addLayout(button_layout)

        # Right: modern player card with cover + title + time + controls + volume
        right = QtWidgets.QVBoxLayout()
        
        # Создаем карточку плеера
        player_card = QtWidgets.QFrame()
        player_card.setStyleSheet("""
            QFrame {
                background:#ffffff; 
                border:1px solid #e5e7eb; 
                border-radius:12px;
                padding: 20px;
            }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(player_card)
        
        # Обложка
        self.cover_label = QtWidgets.QLabel()
        self.cover_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cover_label.setMinimumSize(250, 250)
        self.cover_label.setMaximumSize(250, 250)
        self.cover_label.setStyleSheet("""
            QLabel {
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f3f4f6, stop:1 #e5e7eb);
            }
        """)
        
        # Устанавливаем начальную обложку
        self._set_default_cover()
        card_layout.addWidget(self.cover_label, 0, QtCore.Qt.AlignCenter)
        
        # Название трека
        self.track_title = QtWidgets.QLabel("—")
        self.track_title.setAlignment(QtCore.Qt.AlignCenter)
        self.track_title.setStyleSheet("font-size:18px; font-weight:600; color:#111827; margin: 10px 0;")
        self.track_title.setWordWrap(True)
        card_layout.addWidget(self.track_title)

        # Временная шкала
        timeline = QtWidgets.QHBoxLayout()
        self.time_current = QtWidgets.QLabel("0:00")
        self.time_current.setStyleSheet("color:#374151; font-size:14px; min-width: 40px;")
        self.time_total = QtWidgets.QLabel("0:00")
        self.time_total.setStyleSheet("color:#374151; font-size:14px; min-width: 40px;")
        self.position_slider = SeekSlider(QtCore.Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px; 
                background: #e5e7eb; 
                border-radius: 3px; 
            }
            QSlider::handle:horizontal { 
                width: 16px; 
                background: #3b82f6; 
                margin: -5px 0; 
                border-radius: 8px; 
                border: 1px solid #1d4ed8;
            }
        """)
        timeline.addWidget(self.time_current)
        timeline.addWidget(self.position_slider, 1)
        timeline.addWidget(self.time_total)
        card_layout.addLayout(timeline)

        # Кнопки управления
        controls = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("⏮")
        self.play_btn = QtWidgets.QPushButton("⏯")
        self.stop_btn = QtWidgets.QPushButton("⏹")
        self.next_btn = QtWidgets.QPushButton("⏭")
        self.shuffle_btn = QtWidgets.QPushButton("🔀")
        
        for b in (self.prev_btn, self.play_btn, self.stop_btn, self.next_btn, self.shuffle_btn):
            b.setMinimumHeight(48)
            b.setMinimumWidth(60)
            b.setStyleSheet("""
                QPushButton { 
                    font-size: 16px; 
                    background:#f3f4f6; 
                    color:#111827; 
                    border:1px solid #e5e7eb; 
                    border-radius:10px; 
                    padding: 8px;
                }
                QPushButton:hover { 
                    background:#e5e7eb; 
                }
            """)
            controls.addWidget(b)
        card_layout.addLayout(controls)

        # Громкость
        volume_layout = QtWidgets.QHBoxLayout()
        vol_lbl = QtWidgets.QPushButton("Громкость:")
        vol_lbl.setStyleSheet("color:#374151; font-size:14px; border: none; background: none;")
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self._set_volume)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px; 
                background: #e5e7eb; 
                border-radius: 3px; 
            }
            QSlider::handle:horizontal { 
                width: 16px; 
                background: #3b82f6; 
                margin: -5px 0; 
                border-radius: 8px; 
                border: 1px solid #1d4ed8;
            }
        """)
        volume_layout.addWidget(vol_lbl)
        volume_layout.addWidget(self.volume_slider)
        card_layout.addLayout(volume_layout)

        right.addWidget(player_card)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        body = QtWidgets.QHBoxLayout()
        body.addLayout(left, 2)
        body.addLayout(right, 3)
        layout.addLayout(body, 1)

        # Wire controls
        self.prev_btn.clicked.connect(self._play_prev)
        self.play_btn.clicked.connect(self._toggle_play)
        self.next_btn.clicked.connect(self._play_next)
        self.stop_btn.clicked.connect(self._stop)
        self.shuffle_btn.clicked.connect(self._toggle_shuffle)

        # Timers for position update
        self._position_timer = QtCore.QTimer(self)
        self._position_timer.timeout.connect(self._update_position)
        self._position_timer.start(200)

    def _load_library_music(self):
        """Загружает музыку из папки library"""
        library_dir = WORKDIR / "library"
        if not library_dir.exists():
            QtWidgets.QMessageBox.information(
                self, 
                "Папка не найдена", 
                f"Папка 'library' не найдена по пути:\n{library_dir}\n\nСоздайте папку 'library' и добавьте в нее музыкальные файлы."
            )
            return
        
        # Ищем аудиофайлы
        audio_extensions = ("*.mp3", "*.wav", "*.ogg", "*.flac", "*.m4a", "*.aac")
        found_files = []
        for ext in audio_extensions:
            found_files.extend(library_dir.glob(f"**/{ext}"))
            found_files.extend(library_dir.glob(ext))
        
        if not found_files:
            QtWidgets.QMessageBox.information(
                self,
                "Музыка не найдена",
                f"В папке 'library' не найдено аудиофайлов.\n\nПоддерживаемые форматы: MP3, WAV, OGG, FLAC, M4A, AAC"
            )
            return
        
        # Добавляем файлы в плейлист
        added_count = 0
        for file_path in found_files:
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                added_count += 1
        
        # Обновляем список и выбираем первый трек если плейлист был пуст
        self._refresh_tracklist()
        if self.current_index == -1 and self.playlist:
            self.current_index = 0
        
        # Показываем сообщение о результате
        QtWidgets.QMessageBox.information(
            self,
            "Музыка загружена",
            f"Загружено треков: {added_count}\n\nОбщее количество треков в плейлисте: {len(self.playlist)}"
        )

    def _clear_playlist(self):
        """Очищает весь плейлист"""
        if not self.playlist:
            QtWidgets.QMessageBox.information(self, "Плейлист пуст", "Плейлист уже пуст.")
            return
        
        # Подтверждение очистки
        reply = QtWidgets.QMessageBox.question(
            self,
            "Очистка плейлиста",
            f"Вы уверены, что хотите удалить все треки из плейлиста?\n\nКоличество треков: {len(self.playlist)}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Останавливаем воспроизведение
            self._stop()
            
            # Очищаем плейлист
            self.playlist.clear()
            self.current_index = -1
            self.current_track_path = None
            
            # Обновляем интерфейс
            self._refresh_tracklist()
            self.track_title.setText("—")
            self._set_default_cover()
            self.position_slider.setValue(0)
            self.time_current.setText("0:00")
            self.time_total.setText("0:00")
            
            QtWidgets.QMessageBox.information(self, "Плейлист очищен", "Все треки удалены из плейлиста.")

    def _on_go_back(self):
        """Обработчик выхода из плеера"""
        # Сохраняем состояние перед выходом
        if pygame is not None and self.current_track_path:
            try:
                # Сохраняем текущую позицию
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms > 0:
                    self.last_position = pos_ms / 1000.0
                    print(f"Сохранена позиция: {self.last_position:.1f} сек")
                
                # Сохраняем состояние воспроизведения
                self.was_playing_before_exit = pygame.mixer.music.get_busy() and not self.paused
                print(f"Состояние воспроизведения: {self.was_playing_before_exit}")
                
            except Exception as e:
                print(f"Ошибка при сохранении состояния: {e}")
        
        self.is_active = False
        self._stop_all_music()
        self.goBack.emit()

    def _stop_all_music(self):
        """Полная остановка всей музыки"""
        if pygame is not None:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
            except Exception as e:
                print(f"Ошибка при остановке музыки: {e}")

    def _set_default_cover(self):
        """Устанавливает стандартную обложку"""
        print("Установка стандартной обложки")
        pixmap = load_qpixmap(ASSET_IMAGE_FALLBACK)
        if pixmap.isNull():
            pixmap = QtGui.QPixmap(250, 250)
            pixmap.fill(QtGui.QColor("#3b82f6"))
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QPen(QtGui.QColor("white")))
            painter.setFont(QtGui.QFont("Arial", 16))
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "Обложка\nне найдена")
            painter.end()
        
        scaled_pixmap = pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.cover_label.setPixmap(scaled_pixmap)
        self.cover_label.update()  

    def _update_cover_art(self, path: Path):
        """Обновляет обложку трека"""
        print(f"Попытка загрузить обложку для: {path.name}")
        
        pixmap = None
        
        if MutagenFile is not None:
            try:
                audio = MutagenFile(str(path))
                if audio is not None:
                    cover_data = None
                    
                    if hasattr(audio, 'tags') and audio.tags:
                        for tag_key in audio.tags.keys():
                            if 'APIC' in tag_key or 'COVER' in tag_key.upper():
                                try:
                                    tag_value = audio.tags[tag_key]
                                    if hasattr(tag_value, 'data'):
                                        cover_data = tag_value.data
                                        break
                                except Exception:
                                    pass
                    
                    if not cover_data and hasattr(audio, 'pictures'):
                        pictures = getattr(audio, 'pictures', [])
                        for picture in pictures:
                            try:
                                if hasattr(picture, 'data') and picture.data:
                                    cover_data = picture.data
                                    break
                            except Exception:
                                pass
                    
                    if cover_data:
                        image = QtGui.QImage()
                        if image.loadFromData(cover_data):
                            pixmap = QtGui.QPixmap.fromImage(image)
                
            except Exception:
                pass
        
        if pixmap is None or pixmap.isNull():
            self._set_default_cover()
        else:
            try:
                scaled_pixmap = pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.cover_label.setPixmap(scaled_pixmap)
                self.cover_label.update()
            except Exception:
                self._set_default_cover()
                
    def _update_position(self):
        """Обновляет позицию воспроизведения"""
        if pygame is None or not self.playlist or not self.is_active:
            return
        
        try:
            pos_ms = pygame.mixer.music.get_pos()
            
            if pos_ms >= 0 and self.current_length_s:
                current_pos_sec = pos_ms / 1000.0
                
                if current_pos_sec < self.current_length_s:
                    frac = current_pos_sec / self.current_length_s
                    
                    self.position_slider.blockSignals(True)
                    self.position_slider.setValue(int(frac * 1000))
                    self.position_slider.blockSignals(False)
                    
                    minutes = int(current_pos_sec) // 60
                    seconds = int(current_pos_sec) % 60
                    self.time_current.setText(f"{minutes}:{seconds:02d}")
                    
                    # Сохраняем текущую позицию
                    self.last_position = current_pos_sec
                else:
                    if not self.paused and not self.user_stopped:
                        self._play_next()
            elif pos_ms == -1 and not self.paused and not self.user_stopped:
                if not pygame.mixer.music.get_busy():
                    self._play_next()
                    
        except Exception as e:
            print(f"Position update error: {e}")

    def _play_current(self, from_position: float = None):
        """Воспроизведение текущего трека с возможностью начала с определенной позиции"""
        if pygame is None or not self.playlist:
            return
            
        if not (0 <= self.current_index < len(self.playlist)):
            self.current_index = 0
            
        path = self.playlist[self.current_index]
        self.current_track_path = path
        
        # Определяем позицию для начала воспроизведения
        start_position = from_position if from_position is not None else self.last_position
        
        try:
            # Полностью останавливаем предыдущую музыку
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Загружаем и воспроизводим трек
            pygame.mixer.music.load(str(path))
            
            if start_position > 0:
                print(f"Воспроизведение с позиции: {start_position:.1f} сек")
                pygame.mixer.music.play(start=start_position)
            else:
                print("Воспроизведение с начала")
                pygame.mixer.music.play()
                
            pygame.mixer.music.set_volume(self.volume_slider.value() / 100.0)
            
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            return
            
        # Обновляем интерфейс
        self.track_title.setText(path.stem)
        self._update_cover_art(path)
        self.user_stopped = False
        self.paused = False
        
        # Обновляем позицию слайдера
        if start_position > 0 and self.current_length_s:
            frac = start_position / self.current_length_s
            self.position_slider.setValue(int(frac * 1000))
            
            minutes = int(start_position) // 60
            seconds = int(start_position) % 60
            self.time_current.setText(f"{minutes}:{seconds:02d}")
        else:
            self.position_slider.setValue(0)
            self.time_current.setText("0:00")
            self.last_position = 0.0
        
        # Получаем длину трека
        self.current_length_s = None
        if MutagenFile is not None:
            try:
                mf = MutagenFile(str(path))
                if mf is not None and getattr(mf, 'info', None) is not None:
                    self.current_length_s = float(getattr(mf.info, 'length', 0.0)) or None
                    total = int(self.current_length_s or 0)
                    minutes = total // 60
                    seconds = total % 60
                    self.time_total.setText(f"{minutes}:{seconds:02d}")
            except Exception as e:
                print(f"Ошибка получения длины трека: {e}")

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            self._toggle_play()
            event.accept()
        else:
            event.ignore()

    def _add_tracks(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите аудио", str(WORKDIR), "Audio files (*.mp3 *.wav *.ogg)")
        for f in files:
            path = Path(f)
            if path not in self.playlist:
                self.playlist.append(path)
        self._refresh_tracklist()
        self.current_index = 0 if self.playlist else -1

    def _refresh_tracklist(self):
        self.track_list.clear()
        query = self.search_edit.text().strip().lower()
        ranked: list[tuple[int, Path]] = []
        for p in self.playlist:
            name = p.stem.lower()
            score = name.count(query) if query else 0
            ranked.append((score, p))
        ranked.sort(key=lambda x: (-x[0], x[1].name.lower()))
        for _, p in ranked:
            self.track_list.addItem(p.name)

    def _filter_tracks(self, _text: str):
        self._refresh_tracklist()

    def _play_selected(self):
        row = self.track_list.currentRow()
        if 0 <= row < len(self.playlist):
            name = self.track_list.item(row).text()
            for i, p in enumerate(self.playlist):
                if p.name == name:
                    self.current_index = i
                    break
            self.last_position = 0.0  # Сбрасываем позицию при выборе нового трека
            self._play_current()

    def _set_volume(self, value: int):
        if pygame is not None:
            pygame.mixer.music.set_volume(value / 100.0)

    def _toggle_play(self):
        if pygame is None:
            return
        
        if pygame.mixer.music.get_busy():
            # Музыка играет - ставим на паузу
            pygame.mixer.music.pause()
            self.paused = True
            print("Музыка поставлена на паузу")
        else:
            # Музыка не играет - возобновляем или начинаем заново
            if self.current_track_path and self.playlist:
                try:
                    if self.paused:
                        # Была на паузе - возобновляем
                        pygame.mixer.music.unpause()
                        self.paused = False
                        print("Музыка возобновлена")
                    else:
                        # Не было на паузе - начинаем текущий трек с сохраненной позиции
                        self._play_current(self.last_position)
                        print(f"Начато воспроизведение с позиции {self.last_position:.1f} сек")
                except Exception as e:
                    print(f"Ошибка при возобновлении: {e}")
                    # Если возникла ошибка, перезагружаем трек
                    self._play_current(self.last_position)
            else:
                # Нет текущего трека - начинаем первый
                if self.playlist:
                    self.current_index = max(self.current_index, 0)
                    self.last_position = 0.0
                    self._play_current()
                    print("Начато воспроизведение первого трека")

    def _play_prev(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.last_position = 0.0  # Сбрасываем позицию при переключении трека
        self._play_current()

    def _play_next(self):
        if not self.playlist:
            return
        if self.random_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.last_position = 0.0  # Сбрасываем позицию при переключении трека
        self._play_current()

    def _toggle_shuffle(self):
        if not self.playlist:
            return
        self.random_mode = True
        self.shuffle_btn.setStyleSheet("font-weight: bold;")
        self.current_index = random.randint(0, len(self.playlist) - 1)
        self.last_position = 0.0  # Сбрасываем позицию при переключении трека
        self._play_current()

    def _stop(self):
        if pygame is None:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.user_stopped = True
        self.paused = False
        self.track_title.setText("—")
        self.position_slider.setValue(0)
        self.time_current.setText("0:00")
        self.current_track_path = None
        self.last_position = 0.0  # Сбрасываем позицию
        print("Музыка остановлена")

    def showEvent(self, event):
        """Вызывается когда виджет показывается"""
        super().showEvent(event)
        self.is_active = True
        self.setFocus()
        print("Плеер активирован")
        
        # Автоматически возобновляем воспроизведение, если оно было активнодо выхода
        if self.was_playing_before_exit and self.current_track_path and self.playlist:
            print("Автоматическое возобновление воспроизведения")
            QtCore.QTimer.singleShot(100, self._resume_playback)

    def _resume_playback(self):
        """Возобновляет воспроизведение после активации плеера"""
        if self.current_track_path and self.playlist:
            self._play_current(self.last_position)
            print(f"Возобновлено воспроизведение с позиции {self.last_position:.1f} сек")

    def hideEvent(self, event):
        """Вызывается когда виджет скрывается"""
        super().hideEvent(event)
        
        # Сохраняем состояние перед скрытием
        if pygame is not None and self.current_track_path:
            try:
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms > 0:
                    self.last_position = pos_ms / 1000.0
                    print(f"Сохранена позиция: {self.last_position:.1f} сек")
                
                self.was_playing_before_exit = pygame.mixer.music.get_busy() and not self.paused
                print(f"Состояние воспроизведения: {self.was_playing_before_exit}")
                
            except Exception as e:
                print(f"Ошибка при сохранении состояния: {e}")
        
        self.is_active = False
        self._stop_all_music()
        print("Плеер деактивирован, музыка остановлена")
                 
class SoundButton(QtWidgets.QPushButton):
    def __init__(self, title: str, path: Path | None):
        super().__init__(title)
        self.path = path
        self.pinned = False

class SoundpadWidget(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.buttons: list[SoundButton] = []
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Поиск звуков...")
        self.search_edit.textChanged.connect(self._refilter)

        top = BackTopBar("Саундпад")
        top.goBack.connect(self.goBack.emit)

        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.grid_widget)
        self.scroll.setWidgetResizable(True)

        load_many = QtWidgets.QPushButton("Загрузить")
        load_many.setFocusPolicy(QtCore.Qt.NoFocus)
        load_many.clicked.connect(self._load_many)

        stop_all = QtWidgets.QPushButton("Стоп (Пробел)")
        stop_all.setFocusPolicy(QtCore.Qt.NoFocus)
        stop_all.clicked.connect(self._stop_all)

        bar = QtWidgets.QHBoxLayout()
        bar.addWidget(self.search_edit)
        bar.addWidget(load_many)
        bar.addWidget(stop_all)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addLayout(bar)
        layout.addWidget(self.scroll, 1)
        hint = QtWidgets.QLabel("Подсказка: Shift + ЛКМ — закрепить звук • Shift + ПКМ — удалить звук")
        hint.setAlignment(QtCore.Qt.AlignCenter)
        hint.setStyleSheet("color:#6b7280; font-size: 14px;")
        layout.addWidget(hint)

        self._load_initial_buttons()

    def _load_initial_buttons(self):
        """Загружает начальные кнопки из папки Sounds"""
        self.buttons.clear()
        if SOUNDS_DIR.exists():
            count = 0
            for f in sorted(SOUNDS_DIR.iterdir()):
                if f.suffix.lower() in (".mp3", ".wav", ".ogg"):
                    self.buttons.append(self._create_button(f.stem, f))
                    count += 1
                    if count >= 15:
                        break
        self._relayout()

    def _create_button(self, title: str, path: Path | None) -> SoundButton:
        btn = SoundButton(title, path)
        btn.setMinimumSize(120, 60)
        btn.setStyleSheet("font-size: 14px;")
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFocusPolicy(QtCore.Qt.NoFocus)
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(lambda pos, b=btn: self._on_right_click(b, pos))
        btn.clicked.connect(lambda _=False, b=btn: self._play_button(b))
        btn.installEventFilter(self)
        return btn

    def eventFilter(self, obj, event):
        if isinstance(obj, SoundButton):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.ShiftModifier:
                    # Shift + ЛКМ - закрепить/открепить
                    obj.pinned = not obj.pinned
                    obj.setStyleSheet("background: #ffd54f;" if obj.pinned else "")
                    self._relayout()
                    return True
                    
        return super().eventFilter(obj, event)

    def _on_right_click(self, btn: SoundButton, pos: QtCore.QPoint):
        """Обработчик правого клика на кнопке"""
        if not btn.path:
            return
            
        # Создаем контекстное меню
        menu = QtWidgets.QMenu(self)
        
        # Пункт меню для удаления
        delete_action = QtWidgets.QAction(f"Удалить '{btn.text()}'", self)
        delete_action.triggered.connect(lambda: self._delete_sound(btn))
        menu.addAction(delete_action)
        
        # Показываем меню в позиции клика
        menu.exec_(btn.mapToGlobal(pos))

    def _delete_sound(self, btn: SoundButton):
        """Удаление звука с подтверждением"""
        if not btn.path:
            return
            
        # Проверяем, зажат ли Shift
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            # Shift зажат - показываем диалог подтверждения
            reply = QtWidgets.QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы точно хотите удалить звук '{btn.text()}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                self._perform_deletion(btn)
        else:
            # Shift не зажат - просто удаляем
            self._perform_deletion(btn)

    def _perform_deletion(self, btn: SoundButton):
        """Выполняет фактическое удаление звука"""
        if not btn.path or not btn.path.exists():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Файл не найден!")
            return
            
        try:
            # Удаляем файл
            btn.path.unlink()
            
            # Удаляем кнопку из списка
            if btn in self.buttons:
                self.buttons.remove(btn)
                
            # Обновляем layout
            self._relayout()
            
            QtWidgets.QMessageBox.information(self, "Успех", f"Звук '{btn.text()}' успешно удален!")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось удалить файл: {str(e)}")

    def _play_button(self, btn: SoundButton):
        """Воспроизведение звука"""
        if pygame is None:
            return
        if btn.path and btn.path.exists():
            try:
                snd = pygame.mixer.Sound(str(btn.path))
                snd.play()
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Ошибка", f"Не удалось воспроизвести звук: {str(e)}")

    def _stop_all(self):
        """Остановка всех звуков"""
        if pygame is None:
            return
        try:
            pygame.mixer.stop()
            # Дополнительно останавливаем все каналы
            for i in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(i).stop()
        except Exception as e:
            print(f"Ошибка остановки звуков: {e}")

    def _load_many(self):
        """Загрузка нескольких звуков"""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите звуки", str(WORKDIR), "Audio files (*.mp3 *.wav *.ogg)")
        for f in files:
            p = Path(f)
            # Проверяем, нет ли уже такого звука
            if not any(b.path and b.path == p for b in self.buttons):
                self.buttons.append(self._create_button(p.stem, p))
        self._relayout()

    def _refilter(self, _text: str):
        """Фильтрация звуков по поиску"""
        self._relayout()

    def _relayout(self):
        """Перерисовка сетки кнопок"""
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w is not None:
                self.grid_layout.removeWidget(w)
                w.setParent(None)
                
        # Filter and sort: pinned first (max 5), then by search match
        query = self.search_edit.text().strip().lower()
        pinned = [b for b in self.buttons if b.pinned][:5]
        others = [b for b in self.buttons if not b.pinned]
        
        def score(b: SoundButton) -> int:
            return b.text().lower().count(query) if query else 0
            
        others.sort(key=lambda b: (-score(b), b.text().lower()))
        ordered = pinned + others
        
        # Place in grid
        cols = 4
        for idx, btn in enumerate(ordered):
            r = idx // cols
            c = idx % cols
            self.grid_layout.addWidget(btn, r, c)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            self._stop_all()
            
class WheelWidget(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()
    openGames = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.items: list[Path] = []
        self.current_angle = 0.0
        self.spin_timer = QtCore.QTimer(self)
        self.spin_timer.timeout.connect(self._spin_tick)
        self._spinning = False

        top = BackTopBar("Колесо фортуны")
        top.goBack.connect(self.goBack.emit)

        for i in range(top.layout().count()):
            widget = top.layout().itemAt(i).widget()
            if isinstance(widget, QtWidgets.QPushButton):
                widget.setFocusPolicy(QtCore.Qt.NoFocus)

        main_grid = QtWidgets.QGridLayout()
        
        self.wheel_view = QtWidgets.QLabel()
        self.wheel_view.setFixedSize(380, 380)
        self.wheel_view.setAlignment(QtCore.Qt.AlignCenter)
        self.wheel_view.setStyleSheet("background: #111; border: 1px solid #333; border-radius: 190px;")
        main_grid.addWidget(self.wheel_view, 0, 0, QtCore.Qt.AlignCenter)
        
        img = QtWidgets.QLabel()
        img.setPixmap(load_qpixmap(ASSET_IMAGE_GAME).scaled(340, 340, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        img.setAlignment(QtCore.Qt.AlignCenter)
        main_grid.addWidget(img, 0, 1, QtCore.Qt.AlignCenter)
        
        self.spin_btn = QtWidgets.QPushButton("Крутить")
        self.spin_btn.setMinimumWidth(200)
        self.spin_btn.setMinimumHeight(50)
        self.spin_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spin_btn.clicked.connect(self._spin)
        main_grid.addWidget(self.spin_btn, 1, 0, QtCore.Qt.AlignCenter)
        
        games_btn = QtWidgets.QPushButton("ЕЩЁ ИГРЫ")
        games_btn.setMinimumHeight(50)
        games_btn.setMinimumWidth(200)
        games_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        games_btn.clicked.connect(self.openGames.emit)
        main_grid.addWidget(games_btn, 1, 1, QtCore.Qt.AlignCenter)
        
        self.result_lbl = QtWidgets.QLabel("—")
        self.result_lbl.setAlignment(QtCore.Qt.AlignCenter)
        main_grid.addWidget(self.result_lbl, 2, 0, 1, 2, QtCore.Qt.AlignCenter)
        
        main_grid.setRowStretch(0, 3)
        main_grid.setRowStretch(1, 1)
        main_grid.setRowStretch(2, 1)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)

        load_btn = QtWidgets.QPushButton("Загрузить звуки (до 30)")
        load_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        load_btn.clicked.connect(self._load_items)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addLayout(main_grid, 1)
        layout.addWidget(load_btn)

        self._redraw_wheel()

    def _load_items(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите звуки/песни", str(WORKDIR), "Audio files (*.mp3 *.wav *.ogg)")
        paths = [Path(f) for f in files][:30]
        self.items = paths
        self._redraw_wheel()

    def _redraw_wheel(self):
        size = self.wheel_view.size()
        pix = QtGui.QPixmap(size)
        pix.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pix)
        rect = QtCore.QRectF(0, 0, size.width(), size.height())
        painter.translate(size.width() / 2, size.height() / 2)
        painter.rotate(self.current_angle)
        painter.translate(-size.width() / 2, -size.height() / 2)
        count = max(1, len(self.items))
        for i in range(count):
            hue = int(360 * i / count)
            color = QtGui.QColor()
            color.setHsv(hue, 180, 255)
            painter.setBrush(color)
            painter.setPen(QtGui.QPen(QtGui.QColor("#222")))
            start_angle = int(16 * 360 * i / count)
            span_angle = int(16 * 360 / count)
            painter.drawPie(rect, start_angle, span_angle)
        painter.setPen(QtGui.QPen(QtGui.QColor("white")))
        painter.drawText(rect, QtCore.Qt.AlignCenter, "Колесо")
        painter.end()
        self.wheel_view.setPixmap(pix)

    def _spin(self):
        if not self.items or self._spinning:
            return
        
        # Останавливаем предыдущие звуки перед новым вращением
        if pygame is not None:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        
        sfx_len_ms = 1200
        if pygame is not None and ASSET_SFX_WHEEL.exists():
            try:
                snd = pygame.mixer.Sound(str(ASSET_SFX_WHEEL))
                sfx_len_ms = int(snd.get_length() * 1000)
                snd.play()
            except Exception:
                pass
        
        self._spinning = True
        self.spin_timer.start(20)
        QtCore.QTimer.singleShot(max(800, sfx_len_ms), self._spin_end)

    def _spin_tick(self):
        self.current_angle = (self.current_angle + 8.0) % 360.0
        self._redraw_wheel()

    def _spin_end(self):
        self.spin_timer.stop()
        self._spinning = False
        if not self.items:
            return
        idx = random.randint(0, len(self.items) - 1)
        chosen = self.items[idx]
        self.result_lbl.setText(chosen.stem)
        if pygame is not None:
            try:
                # Останавливаем предыдущую музыку перед воспроизведением новой
                pygame.mixer.music.stop()
                pygame.mixer.music.load(str(chosen))
                pygame.mixer.music.play()
            except Exception:
                pass

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        event.ignore()

class GamesMenu(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()
    openBalls = QtCore.pyqtSignal()
    openNotes = QtCore.pyqtSignal()
    openGuess = QtCore.pyqtSignal()
    openFarm = QtCore.pyqtSignal()
    openSimulator = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        top = BackTopBar("Игры")
        top.goBack.connect(self.goBack.emit)

        left_img = QtWidgets.QLabel()
        left_img.setPixmap(load_qpixmap(ASSET_IMAGE_GAME).scaled(450, 450, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        left_img.setAlignment(QtCore.Qt.AlignCenter)

        right = QtWidgets.QVBoxLayout()
        b1 = QtWidgets.QPushButton("Дождь мелодии")
        b2 = QtWidgets.QPushButton("Ноты")
        b3 = QtWidgets.QPushButton("Угадай песню")
        b4 = QtWidgets.QPushButton("Музыкальная ферма")
        b5 = QtWidgets.QPushButton("Симулятор")
        
        for b in (b1, b2, b3, b4, b5):
            b.setMinimumHeight(64)
            b.setStyleSheet("font-size: 16px;")
            b.setFocusPolicy(QtCore.Qt.NoFocus)  # Отключаем фокус для кнопок
            right.addWidget(b)
        right.addStretch()

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(top, 0, 0, 1, 2)
        layout.addWidget(left_img, 1, 0)
        right_box = QtWidgets.QWidget()
        right_box.setLayout(right)
        layout.addWidget(right_box, 1, 1)

        b1.clicked.connect(self.openBalls.emit)
        b2.clicked.connect(self.openNotes.emit)
        b3.clicked.connect(self.openGuess.emit)
        b4.clicked.connect(self.openFarm.emit)
        b5.clicked.connect(self.openSimulator.emit)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # Игнорируем все клавиши, включая пробел и стрелки
        event.ignore()
class MelodyRainGame(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.score = 0
        self.notes: list[QtCore.QRectF] = []
        self.velocities: list[QtCore.QPointF] = []
        self.melody_sequence = []
        self.current_note_index = 0
        self.melody_completed = False
        self.game_active = False

        top = BackTopBar("Дождь мелодии")
        top.goBack.connect(self._exit_game)

        self.canvas = QtWidgets.QLabel()
        self.canvas.setMinimumSize(800, 520)
        self.canvas.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0f172a, stop:1 #1e1b4b);")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addWidget(self.canvas, 1)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.setInterval(30)

        self._create_melody()

        controls = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Старт")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setStyleSheet("font-size: 16px; background:#10b981; color:white;")
        self.start_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.start_btn.clicked.connect(self._start_game)
        
        self.stop_btn = QtWidgets.QPushButton("Стоп")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setStyleSheet("font-size: 16px; background:#ef4444; color:white;")
        self.stop_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.stop_btn.clicked.connect(self._stop_game)
        
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)
        
        self.status_label = QtWidgets.QLabel("Соберите ноты чтобы услышать мелодию!")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #000000; font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)

        self.melody_hint = QtWidgets.QLabel("🎵 Мелодия: 'Весенняя рапсодия' 🎵")
        self.melody_hint.setAlignment(QtCore.Qt.AlignCenter)
        self.melody_hint.setStyleSheet("color: #fbbf24; font-size: 16px; font-weight: bold; padding: 10px; background: rgba(30, 41, 59, 0.8); border-radius: 10px;")
        layout.addWidget(self.melody_hint)

    def _create_melody(self):
        self.melody_sequence = ["C", "D", "E", "F", "G", "F", "E", "D", "C"]
        self.current_note_index = 0

    def _play_note(self, note: str):
        if pygame is None:
            return
            
        frequencies = {
            "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, 
            "G": 392.00, "A": 440.00, "B": 493.88
        }
        
        try:
            import numpy as np
            sr = 22050
            duration = 0.8
            
            t = np.linspace(0, duration, int(sr * duration), False)
            wave = (0.5 * np.sin(2 * np.pi * frequencies[note] * t) * 
                   np.exp(-2 * t) * 
                   (1 + 0.3 * np.sin(2 * np.pi * frequencies[note] * 2 * t)))
            
            wave = wave / np.max(np.abs(wave))
            arr = (wave * 32767).astype(np.int16)
            
            snd = pygame.mixer.Sound(buffer=arr.tobytes())
            snd.set_volume(0.7)
            snd.play()
            
        except Exception as e:
            print(f"Error playing note: {e}")

    def _complete_melody(self):
        self.melody_completed = True
        self.game_active = False
        self.timer.stop()
        
        self.notes.clear()
        self.velocities.clear()
        
        self.status_label.setText("🎉 ПОЗДРАВЛЯЕМ! Вы собрали всю мелодию! 🎉")
        self.status_label.setStyleSheet("color: #10b981; font-size: 18px; font-weight: bold; padding: 10px;")
        
        self._play_complete_melody()
        
        QtCore.QTimer.singleShot(2000, self._show_congratulations)

    def _show_congratulations(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Поздравление!")
        msg.setText(f"🎵 ВЫСШИЙ РЕЗУЛЬТАТ! 🎵\n\nВы успешно собрали мелодию 'Весенняя рапсодия'!\n\nСчёт: {self.score} очков")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.buttonClicked.connect(self._restart_after_win)
        msg.exec_()

    def _restart_after_win(self):
        self.status_label.setText("Готовы к новой мелодии? Нажмите 'Старт'!")
        self.status_label.setStyleSheet("color: #e2e8f0; font-size: 14px; padding: 10px;")
        self.melody_completed = False
        self.current_note_index = 0
        self.score = 0

    def _play_complete_melody(self):
        for i, note in enumerate(self.melody_sequence):
            QtCore.QTimer.singleShot(i * 600, lambda n=note: self._play_note(n))

    def _stop_game(self):
        if not self.game_active:
            return
            
        self.timer.stop()
        self.game_active = False
        
        if not self.melody_completed:
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Игра остановлена")
            msg.setText(f"Игра прервана!\n\nВаш счёт: {self.score}\nПрогресс: {self.current_note_index}/{len(self.melody_sequence)}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
        
        self._exit_game()

    def _exit_game(self):
        """Выход из игры с остановкой звуков"""
        self.timer.stop()
        self.game_active = False
        
        # Останавливаем все звуки
        if pygame is not None:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
            except Exception:
                pass
                
        self.goBack.emit()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space and self.game_active:
            self._pause_menu()
        elif event.key() == QtCore.Qt.Key_Escape:
            self._exit_game()
        else:
            event.ignore()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if not self.game_active or self.melody_completed:
            return
            
        canvas_pos = self.canvas.mapFromParent(event.pos())
        if not self.canvas.rect().contains(canvas_pos):
            return
            
        pos = canvas_pos
        
        note_hit = False
        hit_index = -1
        
        for i in range(len(self.notes) - 1, -1, -1):
            r = self.notes[i]
            if r.contains(pos):
                note_hit = True
                hit_index = i
                break
        
        if note_hit and hit_index >= 0:
            note_color = self._get_note_color(hit_index)
            current_note_name = self._get_note_by_color(note_color)
            
            if self.current_note_index < len(self.melody_sequence):
                expected_note = self.melody_sequence[self.current_note_index]
                
                if current_note_name == expected_note:
                    self.score += 10
                    self.current_note_index += 1
                    self._play_note(current_note_name)
                    
                    if self.current_note_index < len(self.melody_sequence):
                        next_note = self.melody_sequence[self.current_note_index]
                        ru_notes = {"C":"до", "D":"ре", "E":"ми", "F":"фа", "G":"соль", "A":"ля", "B":"си"}
                        self.status_label.setText(f"Отлично! Следующая нота: {ru_notes.get(next_note, next_note)}")
                    else:
                        self._complete_melody()
                else:
                    self.score = max(0, self.score - 5)
                    self.status_label.setText("Не та нота! Следуйте последовательности.")
                
                if hit_index < len(self.notes) and hit_index < len(self.velocities):
                    del self.notes[hit_index]
                    del self.velocities[hit_index]

    def _get_note_color(self, index):
        note_colors = [
            QtGui.QColor("#ef4444"), QtGui.QColor("#f97316"), QtGui.QColor("#f59e0b"),
            QtGui.QColor("#22c55e"), QtGui.QColor("#06b6d4"), QtGui.QColor("#3b82f6"),
            QtGui.QColor("#8b5cf6"),
        ]
        return note_colors[index % len(note_colors)]

    def _get_note_by_color(self, color):
        color_to_note = {
            "#ef4444": "C", "#f97316": "D", "#f59e0b": "E",
            "#22c55e": "F", "#06b6d4": "G", "#3b82f6": "A",
            "#8b5cf6": "B",
        }
        if isinstance(color, QtGui.QColor):
            return color_to_note.get(color.name(), "C")
        return color_to_note.get(color, "C")

    def _pause_menu(self):
        if not self.game_active:
            return
            
        self.timer.stop()
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Пауза", 
            f"Счёт: {self.score}\nПрогресс мелодии: {self.current_note_index}/{len(self.melody_sequence)}\nПродолжить игру?", 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.timer.start()
        else:
            self._stop_game()

    def _spawn_note(self):
        if not self.game_active or self.melody_completed:
            return
            
        w = self.canvas.width()
        x = random.randint(20, max(20, w - 60))
        r = QtCore.QRectF(x, -50, 40, 40)
        self.notes.append(r)
        self.velocities.append(QtCore.QPointF(0, random.uniform(0.8, 1.0)))

    def _start_game(self):
        self.score = 0
        self.notes.clear()
        self.velocities.clear()
        self.current_note_index = 0
        self.melody_completed = False
        self.game_active = True
        self.status_label.setText("Соберите ноты чтобы услышать мелодию! Первая нота: до")
        self.status_label.setStyleSheet("color: #000000; font-size: 14px; padding: 10px;")
        self.timer.start()

    def _tick(self):
        if not self.game_active or self.melody_completed:
            return
            
        if random.random() < 0.03:
            self._spawn_note()
            
        h = self.canvas.height()
        i = 0
        while i < len(self.notes):
            r = self.notes[i]
            v = self.velocities[i]
            r.translate(v)
            
            if r.top() > h:
                del self.notes[i]
                del self.velocities[i]
            else:
                i += 1
        
        self._draw()

    def _draw(self):
        pix = QtGui.QPixmap(self.canvas.size())
        pix.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.fillRect(pix.rect(), QtGui.QColor("#0f172a"))
        
        painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff")))
        for _ in range(50):
            x = random.randint(0, pix.width())
            y = random.randint(0, pix.height())
            size = random.randint(1, 3)
            painter.drawEllipse(x, y, size, size)
        
        if self.game_active and not self.melody_completed:
            for i, r in enumerate(self.notes):
                color = self._get_note_color(i)
                
                gradient = QtGui.QRadialGradient(r.center(), r.width() / 2)
                gradient.setColorAt(0, QtGui.QColor(color).lighter(150))
                gradient.setColorAt(1, color)
                
                painter.setBrush(QtGui.QBrush(gradient))
                painter.setPen(QtGui.QPen(QtGui.QColor("white"), 2))
                painter.drawEllipse(r)
                
                note_name = self._get_note_by_color(color)
                ru_notes = {"C":"Д", "D":"Р", "E":"М", "F":"Ф", "G":"С", "A":"Л", "B":"С"}
                painter.setPen(QtGui.QPen(QtGui.QColor("black")))
                painter.drawText(r, QtCore.Qt.AlignCenter, ru_notes.get(note_name, note_name))
        
        platform_color = QtGui.QColor("#334155")
        painter.setBrush(platform_color)
        painter.drawRoundedRect(0, pix.height() - 20, pix.width(), 20, 10, 10)
        
        painter.setPen(QtGui.QPen(QtGui.QColor("white")))
        painter.drawText(10, 30, f"Счёт: {self.score}")
        
        progress = self.current_note_index / len(self.melody_sequence) * 100
        painter.drawText(10, 60, f"Мелодия: {progress:.0f}%")
        
        bar_width = 200
        bar_height = 10
        bar_x = pix.width() - bar_width - 10
        bar_y = 30
        
        painter.setBrush(QtGui.QColor("#374151"))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 5, 5)
        
        filled_width = int(bar_width * progress / 100)
        painter.setBrush(QtGui.QColor("#10b981"))
        painter.drawRoundedRect(bar_x, bar_y, filled_width, bar_height, 5, 5)
        
        if self.melody_completed:
            painter.setPen(QtGui.QPen(QtGui.QColor("#10b981")))
            painter.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Bold))
            painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "🎉 ПОБЕДА! 🎉")
        
        painter.end()
        self.canvas.setPixmap(pix)

class MusicFarmGame(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.money = 0
        self.click_value = 1
        self.auto_clicker_level = 0
        self.bonus_level = 0
        self.unlocked_tracks = []
        self.all_tracks = self._load_secret_tracks()
        self.auto_clicker_income = 0
        self.game_paused = True
        
        # Таймеры
        self.auto_click_timer = QtCore.QTimer(self)
        self.auto_click_timer.timeout.connect(self._auto_click)
        self.bonus_timer = QtCore.QTimer(self)
        self.bonus_timer.timeout.connect(self._give_bonus)
        
        self._load_game_state()

        top = BackTopBar("Музыкальная ферма")
        top.goBack.connect(self._exit_game)

        # Основной layout
        main_layout = QtWidgets.QHBoxLayout()

        # Левая часть - магазин треков
        left_shop = QtWidgets.QVBoxLayout()
        shop_label = QtWidgets.QLabel("🎵 Магазин треков 🎵")
        shop_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e40af;")
        left_shop.addWidget(shop_label)

        self.track_shop = QtWidgets.QListWidget()
        self._update_track_shop()
        left_shop.addWidget(self.track_shop)

        left_shop_widget = QtWidgets.QWidget()
        left_shop_widget.setLayout(left_shop)
        left_shop_widget.setStyleSheet("background: #f0f9ff; border: 2px solid #bae6fd; border-radius: 10px; padding: 10px;")
        left_shop_widget.setMaximumWidth(300)

        # Центральная часть - ферма
        center_farm = QtWidgets.QVBoxLayout()
        center_farm.setAlignment(QtCore.Qt.AlignCenter)

        # Счетчик денег
        self.money_label = QtWidgets.QLabel(f"💰 ${self.money}")
        self.money_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #16a34a;")
        center_farm.addWidget(self.money_label)

        # Изображение фермы (кликабельное)
        self.farm_image = QtWidgets.QLabel()
        self.farm_image.setPixmap(load_qpixmap(ASSET_IMAGE_FARM).scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.farm_image.setAlignment(QtCore.Qt.AlignCenter)
        self.farm_image.setStyleSheet("border: 3px solid #f59e0b; border-radius: 15px; padding: 10px;")
        self.farm_image.mousePressEvent = self._on_farm_click
        center_farm.addWidget(self.farm_image)

        # Информация о клике
        click_info = QtWidgets.QLabel("Кликай на изображение для заработка!")
        click_info.setStyleSheet("color: #6b7280; font-size: 14px;")
        center_farm.addWidget(click_info)

        # Правая часть - улучшения + сброс
        right_upgrades = QtWidgets.QVBoxLayout()
        upgrades_label = QtWidgets.QLabel("⚡ Улучшения ⚡")
        upgrades_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #dc2626;")
        right_upgrades.addWidget(upgrades_label)

        # Улучшение на клик
        self.upgrade_click_btn = QtWidgets.QPushButton(f"Улучшение клика\n+1$ за клик\nЦена: {self._get_click_upgrade_price()}$")
        self.upgrade_click_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.upgrade_click_btn.clicked.connect(self._upgrade_click)
        right_upgrades.addWidget(self.upgrade_click_btn)

        # Автокликер
        self.auto_clicker_btn = QtWidgets.QPushButton(f"Автокликер\nУровень: {self.auto_clicker_level}\nЦена: {self._get_auto_clicker_price()}$")
        self.auto_clicker_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.auto_clicker_btn.clicked.connect(self._upgrade_auto_clicker)
        right_upgrades.addWidget(self.auto_clicker_btn)

        # Бонус за время
        self.bonus_btn = QtWidgets.QPushButton(f"Бонус за 2 минуты\nДоход автокликера ×{self.bonus_level}\nЦена: {self._get_bonus_price()}$")
        self.bonus_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.bonus_btn.clicked.connect(self._upgrade_bonus)
        right_upgrades.addWidget(self.bonus_btn)

        # Кнопка сброса игры
        reset_btn = QtWidgets.QPushButton("🔄 Сбросить игру")
        reset_btn.setStyleSheet("background: #ef4444; color: white; font-weight: bold; padding: 12px; border-radius: 8px;")
        reset_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        reset_btn.clicked.connect(self._reset_game_confirmation)
        right_upgrades.addWidget(reset_btn)

        right_upgrades.addStretch()

        right_upgrades_widget = QtWidgets.QWidget()
        right_upgrades_widget.setLayout(right_upgrades)
        right_upgrades_widget.setStyleSheet("background: #fef2f2; border: 2px solid #fecaca; border-radius: 10px; padding: 10px;")
        right_upgrades_widget.setMaximumWidth(300)

        # Собираем основной layout
        main_layout.addWidget(left_shop_widget)
        main_layout.addLayout(center_farm)
        main_layout.addWidget(right_upgrades_widget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addLayout(main_layout)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self._exit_game()
        else:
            # Игнорируем все клавиши, включая пробел
            event.ignore()

    def showEvent(self, event):
        """Вызывается когда виджет показывается"""
        super().showEvent(event)
        self.resume_game()

    def hideEvent(self, event):
        """Вызывается когда виджет скрывается"""
        super().hideEvent(event)
        self.pause_game()

    def pause_game(self):
        """Приостанавливает игру"""
        if not self.game_paused:
            self.game_paused = True
            self.auto_click_timer.stop()
            self.bonus_timer.stop()
            self._save_game_state()
            print("Музыкальная ферма: игра приостановлена")

    def resume_game(self):
        """Возобновляет игру"""
        if self.game_paused:
            self.game_paused = False
            self.auto_click_timer.start(1000)
            self.bonus_timer.start(120000)
            print("Музыкальная ферма: игра возобновлена")

    def _load_secret_tracks(self):
        """Загружает секретные треки из папки"""
        tracks = []
        if SECRET_MUSIC_DIR.exists():
            for f in SECRET_MUSIC_DIR.iterdir():
                if f.suffix.lower() in (".mp3", ".wav", ".ogg"):
                    tracks.append(f)
        return tracks

    def _load_game_state(self):
        """Загружает сохраненное состояние игры"""
        try:
            save_file = WORKDIR / "farm_save.txt"
            if save_file.exists():
                with open(save_file, 'r') as f:
                    data = f.read().splitlines()
                    if len(data) >= 4:
                        self.money = int(data[0])
                        self.click_value = int(data[1])
                        self.auto_clicker_level = int(data[2])
                        self.bonus_level = int(data[3])
                        if len(data) > 4 and data[4]:
                            self.unlocked_tracks = data[4].split(',')
        except:
            pass

    def _save_game_state(self):
        """Сохраняет состояние игры"""
        try:
            save_file = WORKDIR / "farm_save.txt"
            with open(save_file, 'w') as f:
                f.write(f"{self.money}\n")
                f.write(f"{self.click_value}\n")
                f.write(f"{self.auto_clicker_level}\n")
                f.write(f"{self.bonus_level}\n")
                f.write(f"{','.join(self.unlocked_tracks)}\n")
        except:
            pass

    def _on_farm_click(self, event):
        """Обработчик клика по ферме"""
        self.money += self.click_value
        self._update_display()
        self._play_click_sound()

    def _play_click_sound(self):
        """Воспроизводит звук клика"""
        if pygame is not None:
            try:
                import numpy as np
                sr = 22050
                duration = 0.1
                t = np.linspace(0, duration, int(sr * duration), False)
                wave = (0.3 * np.sin(2 * np.pi * 800 * t) * np.exp(-10 * t)).astype(np.float32)
                arr = (wave * 32767).astype(np.int16)
                snd = pygame.mixer.Sound(buffer=arr.tobytes())
                snd.set_volume(0.3)
                snd.play()
            except:
                pass

    def _auto_click(self):
        """Автоматический клик"""
        if self.auto_clicker_level > 0:
            self.money += self.auto_clicker_level
            self._update_display()

    def _give_bonus(self):
        """Выдает бонус за время"""
        if self.bonus_level > 0:
            bonus = self.bonus_level * 50
            self.money += bonus
            self._show_bonus_message(bonus)
            self._update_display()

    def _show_bonus_message(self, amount):
        """Показывает сообщение о бонусе"""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("🎉 Бонус!")
        msg.setText(f"Вы получили бонус: ${amount}!")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def _get_click_upgrade_price(self):
        return self.click_value * 10

    def _get_auto_clicker_price(self):
        return (self.auto_clicker_level + 1) * 100

    def _get_bonus_price(self):
        return (self.bonus_level + 1) * 500

    def _upgrade_click(self):
        price = self._get_click_upgrade_price()
        if self.money >= price:
            self.money -= price
            self.click_value += 1
            self._update_display()
            self._update_buttons()

    def _upgrade_auto_clicker(self):
        price = self._get_auto_clicker_price()
        if self.money >= price:
            self.money -= price
            self.auto_clicker_level += 1
            self._update_display()
            self._update_buttons()

    def _upgrade_bonus(self):
        price = self._get_bonus_price()
        if self.money >= price:
            self.money -= price
            self.bonus_level += 1
            self._update_display()
            self._update_buttons()

    def _update_display(self):
        """Обновляет отображение"""
        self.money_label.setText(f"💰 ${self.money}")
        self._save_game_state()

    def _update_buttons(self):
        """Обновляет кнопки улучшений"""
        self.upgrade_click_btn.setText(f"Улучшение клика\n+1$ за клик\nЦена: {self._get_click_upgrade_price()}$")
        self.auto_clicker_btn.setText(f"Автокликер\nУровень: {self.auto_clicker_level}\nЦена: {self._get_auto_clicker_price()}$")
        self.bonus_btn.setText(f"Бонус за 2 минуты\nДоход автокликера ×{self.bonus_level}\nЦена: {self._get_bonus_price()}$")

    def _update_track_shop(self):
        """Обновляет магазин треков"""
        self.track_shop.clear()
        for i, track in enumerate(self.all_tracks):
            track_name = track.stem
            is_unlocked = track_name in self.unlocked_tracks
            price = (i + 1) * 1000
            
            if is_unlocked:
                item_text = f"✅ {track_name} (куплено)"
            else:
                item_text = f"🔒 Заблокировано {i + 1} - ${price}"
            
            item = QtWidgets.QListWidgetItem(item_text)
            if not is_unlocked:
                item.setData(QtCore.Qt.UserRole, (track, price, i + 1))
            else:
                item.setData(QtCore.Qt.UserRole, (track, 0, i + 1))
            self.track_shop.addItem(item)
        
        self.track_shop.itemDoubleClicked.connect(self._on_track_click)

    def _on_track_click(self, item):
        """Обработчик клика по треку в магазине"""
        track_data = item.data(QtCore.Qt.UserRole)
        if track_data:
            track, price, track_number = track_data
            if price == 0:  # Трек уже разблокирован
                self._play_unlocked_track(track)
            else:  # Трек заблокирован
                if self.money >= price:
                    self.money -= price
                    self.unlocked_tracks.append(track.stem)
                    self._update_display()
                    self._update_track_shop()
                    self._play_unlocked_track(track)
                else:
                    QtWidgets.QMessageBox.warning(self, "Недостаточно средств", 
                                                f"Вам нужно еще ${price - self.money}!")

    def _play_unlocked_track(self, track):
        """Воспроизводит разблокированный трек"""
        if pygame is not None:
            try:
                pygame.mixer.music.load(str(track))
                pygame.mixer.music.play()
                QtWidgets.QMessageBox.information(self, "Поздравляем!", 
                                                f"Трек '{track.stem}' разблокирован и воспроизводится!")
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
                QtWidgets.QMessageBox.information(self, "Поздравляем!", 
                                                f"Трек '{track.stem}' разблокирован!")

    def _reset_game_confirmation(self):
        """Подтверждение сброса игры"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Сброс игры", 
            "Вы уверены, что хотите сбросить игру?\nВесь прогресс будет потерян!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self._reset_game()

    def _reset_game(self):
        """Полный сброс игры"""
        # Сбрасываем все переменные
        self.money = 0
        self.click_value = 1
        self.auto_clicker_level = 0
        self.bonus_level = 0
        self.unlocked_tracks = []
        
        # Удаляем файл сохранения
        try:
            save_file = WORKDIR / "farm_save.txt"
            if save_file.exists():
                save_file.unlink()
        except:
            pass
        
        # Обновляем интерфейс
        self._update_display()
        self._update_buttons()
        self._update_track_shop()
        
        # Останавливаем музыку
        if pygame is not None:
            pygame.mixer.music.stop()
        
        QtWidgets.QMessageBox.information(self, "Игра сброшена", "Игра успешно сброшена! Начинаем заново!")

    def _exit_game(self):
        """Выход из игры"""
        if pygame is not None:
            pygame.mixer.music.stop()
        self.goBack.emit()

class PianoXylophoneSimulator(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # Для обработки клавиатуры
        self.current_instrument = "piano"  # piano или xylophone
        
        top = BackTopBar("Симулятор пианино и ксилофона")
        top.goBack.connect(self.goBack.emit)

        # Выбор инструмента
        instrument_layout = QtWidgets.QHBoxLayout()
        self.piano_btn = QtWidgets.QPushButton("🎹 Пианино")
        self.xylophone_btn = QtWidgets.QPushButton("🎵 Ксилофон")
        
        for btn in (self.piano_btn, self.xylophone_btn):
            btn.setMinimumHeight(50)
            btn.setStyleSheet("font-size: 16px;")
            instrument_layout.addWidget(btn)
        
        self.piano_btn.clicked.connect(lambda: self._switch_instrument("piano"))
        self.xylophone_btn.clicked.connect(lambda: self._switch_instrument("xylophone"))
        
        # Изображение инструмента
        self.instrument_image = QtWidgets.QLabel()
        self.instrument_image.setAlignment(QtCore.Qt.AlignCenter)
        self.instrument_image.setMinimumSize(600, 300)
        
        # Клавиши пианино (визуальное представление)
        self.keys_widget = QtWidgets.QWidget()
        self.keys_layout = QtWidgets.QHBoxLayout(self.keys_widget)
        self.keys_layout.setSpacing(2)
        
        # Создаем клавиши пианино
        self.piano_keys = {}
        self._create_piano_keys()
        
        # Подсказки для клавиатуры
        hints_label = QtWidgets.QLabel(
            "Управление: A S D F G H J (белые клавиши) • W E T Y U (черные клавиши)\n"
            "Или кликайте мышкой по клавишам на экране"
        )
        hints_label.setAlignment(QtCore.Qt.AlignCenter)
        hints_label.setStyleSheet("color: #6b7280; font-size: 14px; background: #f3f4f6; padding: 10px; border-radius: 5px;")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addLayout(instrument_layout)
        layout.addWidget(self.instrument_image)
        layout.addWidget(self.keys_widget)
        layout.addWidget(hints_label)
        
        self._switch_instrument("piano")  # Устанавливаем начальный инструмент

    def _create_piano_keys(self):
        """Создает визуальные клавиши пианино"""
        # Белые клавиши
        white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        white_keys = ['A', 'S', 'D', 'F', 'G', 'H', 'J']  # Клавиши клавиатуры
        
        # Черные клавиши
        black_notes = ['C#', 'D#', 'F#', 'G#', 'A#']
        black_keys = ['W', 'E', 'T', 'Y', 'U']  # Клавиши клавиатуры
        
        # Соответствие белых нот индексам черных клавиш
        white_to_black_index = {
            'C': 0,  # После C идет C#
            'D': 1,  # После D идет D#
            'F': 2,  # После F идет F#
            'G': 3,  # После G идет G#
            'A': 4   # После A идет A#
        }
        
        for i, (note, key) in enumerate(zip(white_notes, white_keys)):
            btn = QtWidgets.QPushButton(f"{note}\n({key})")
            btn.setMinimumSize(60, 150)
            btn.setStyleSheet("""
                QPushButton { 
                    background: white; 
                    border: 2px solid #ccc; 
                    border-radius: 0 0 5px 5px;
                    font-size: 12px;
                    color: black;
                }
                QPushButton:pressed { 
                    background: #e0e0e0; 
                }
            """)
            btn.setProperty("note", note)
            btn.setProperty("key", key)
            btn.setProperty("type", "white")
            btn.clicked.connect(lambda checked, n=note: self._play_note(n))
            self.keys_layout.addWidget(btn)
            self.piano_keys[key] = btn
            
            # Добавляем черную клавишу после определенных белых клавиш
            if note in white_to_black_index:
                black_index = white_to_black_index[note]
                if black_index < len(black_notes):
                    black_btn = QtWidgets.QPushButton(f"{black_notes[black_index]}\n({black_keys[black_index]})")
                    black_btn.setMinimumSize(40, 100)
                    black_btn.setStyleSheet("""
                        QPushButton { 
                            background: black; 
                            border: 1px solid #333; 
                            border-radius: 0 0 3px 3px;
                            font-size: 10px;
                            color: white;
                        }
                        QPushButton:pressed { 
                            background: #444; 
                        }
                    """)
                    black_btn.setProperty("note", black_notes[black_index])
                    black_btn.setProperty("key", black_keys[black_index])
                    black_btn.setProperty("type", "black")
                    black_btn.clicked.connect(lambda checked, n=black_notes[black_index]: self._play_note(n))
                    
                    # Позиционируем черную клавишу над белой
                    spacer = QtWidgets.QSpacerItem(40, 100, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                    self.keys_layout.addItem(spacer)
                    self.piano_keys[black_keys[black_index]] = black_btn

    def _switch_instrument(self, instrument):
        """Переключает между пианино и ксилофоном"""
        self.current_instrument = instrument
        
        if instrument == "piano":
            self.piano_btn.setStyleSheet("background: #3b82f6; color: white; font-size: 16px;")
            self.xylophone_btn.setStyleSheet("font-size: 16px;")
            self.keys_widget.show()
            pixmap = load_qpixmap(ASSET_IMAGE_PIANO).scaled(600, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        else:
            self.xylophone_btn.setStyleSheet("background: #3b82f6; color: white; font-size: 16px;")
            self.piano_btn.setStyleSheet("font-size: 16px;")
            self.keys_widget.hide()
            pixmap = load_qpixmap(ASSET_IMAGE_XYLOPHONE).scaled(600, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        self.instrument_image.setPixmap(pixmap)

    def _play_note(self, note):
        """Воспроизводит ноту для текущего инструмента"""
        if pygame is None:
            return
            
        # Частоты для нот (октава 4)
        frequencies = {
            'C': 261.63, 'C#': 277.18,
            'D': 293.66, 'D#': 311.13,
            'E': 329.63,
            'F': 349.23, 'F#': 369.99,
            'G': 392.00, 'G#': 415.30,
            'A': 440.00, 'A#': 466.16,
            'B': 493.88
        }
        
        if note not in frequencies:
            return
            
        try:
            import numpy as np
            sr = 22050  # частота дискретизации
            
            # Разные характеристики звука для разных инструментов
            if self.current_instrument == "piano":
                # Звук пианино - с быстрым атаком и затуханием
                duration = 1.0
                t = np.linspace(0, duration, int(sr * duration), False)
                
                # Более сложная форма волны для пианино
                wave = (0.7 * np.sin(2 * np.pi * frequencies[note] * t) *
                       np.exp(-4 * t) *  # быстрое затухание
                       (1 + 0.2 * np.sin(2 * np.pi * frequencies[note] * 2 * t) +
                        0.1 * np.sin(2 * np.pi * frequencies[note] * 3 * t)))
                
            else:  # xylophone
                # Звук ксилофона - более короткий и звонкий
                duration = 0.5
                t = np.linspace(0, duration, int(sr * duration), False)
                
                # Ксилофон имеет более простой звук с гармониками
                wave = (0.8 * np.sin(2 * np.pi * frequencies[note] * t) *
                       np.exp(-6 * t) *  # очень быстрое затухание
                       (1 + 0.3 * np.sin(2 * np.pi * frequencies[note] * 3 * t)))
            
            # Нормализуем и конвертируем в 16-битный звук
            wave = wave / np.max(np.abs(wave))
            arr = (wave * 32767).astype(np.int16)
            
            snd = pygame.mixer.Sound(buffer=arr.tobytes())
            snd.set_volume(0.7)
            snd.play()
            
            # Визуальная обратная связь - подсветка клавиши
            self._highlight_key(note)
            
        except Exception as e:
            print(f"Ошибка воспроизведения ноты: {e}")

    def _highlight_key(self, note):
        """Подсвечивает нажатую клавишу"""
        # Находим клавишу по ноте
        for key, btn in self.piano_keys.items():
            if btn.property("note") == note:
                # Временно меняем цвет
                original_style = btn.styleSheet()
                if btn.property("type") == "white":
                    btn.setStyleSheet("background: #ffd54f; border: 2px solid #ccc; border-radius: 0 0 5px 5px; font-size: 12px; color: black;")
                else:
                    btn.setStyleSheet("background: #ffb74d; border: 1px solid #333; border-radius: 0 0 3px 3px; font-size: 10px; color: white;")
                
                # Возвращаем исходный цвет через 200 мс
                QtCore.QTimer.singleShot(200, lambda b=btn, style=original_style: b.setStyleSheet(style))
                break

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш клавиатуры"""
        key = event.text().upper() if event.text() else ""
        
        # Соответствие клавиш нотам
        key_to_note = {
            'A': 'C', 'W': 'C#',
            'S': 'D', 'E': 'D#',
            'D': 'E',
            'F': 'F', 'T': 'F#',
            'G': 'G', 'Y': 'G#',
            'H': 'A', 'U': 'A#',
            'J': 'B'
        }
        
        if key in key_to_note:
            self._play_note(key_to_note[key])
        elif event.key() == QtCore.Qt.Key_Escape:
            self.goBack.emit()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        """Устанавливаем фокус при показе"""
        super().showEvent(event)
        self.setFocus()

class GuessSongGame(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tracks: list[Path] = []
        self.current_answer: Path | None = None

        top = BackTopBar("Угадайка")
        top.goBack.connect(self.goBack.emit)

        title = QtWidgets.QLabel("Угадай песню")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.position = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.buttons = [QtWidgets.QPushButton("") for _ in range(4)]
        grid = QtWidgets.QGridLayout()
        for i, b in enumerate(self.buttons):
            r, c = divmod(i, 2)
            grid.addWidget(b, r, c)
            b.setFocusPolicy(QtCore.Qt.NoFocus)
            b.clicked.connect(self._make_handler(b))

        load_btn = QtWidgets.QPushButton("Загрузить песни")
        load_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        load_btn.clicked.connect(self._load_tracks)
        
        self.start_btn = QtWidgets.QPushButton("Начать")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setStyleSheet("font-size: 16px; background:#374151; color:#ffffff;")
        self.start_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.start_btn.clicked.connect(self._start_round)
        
        self.stop_btn = QtWidgets.QPushButton("Стоп")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setStyleSheet("font-size: 16px;")
        self.stop_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.stop_btn.clicked.connect(self._stop_game)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(load_btn)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)
        layout.addWidget(title)
        layout.addWidget(self.position)
        
        options_box = QtWidgets.QFrame()
        options_box.setStyleSheet("QFrame{background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:16px;} QPushButton{font-size:17px; padding:14px 16px;}")
        options_box.setLayout(grid)
        layout.addWidget(options_box)

    def _stop_game(self):
        """Остановка игры с очисткой звуков"""
        if pygame is not None:
            pygame.mixer.music.stop()
        self.current_answer = None
        self.goBack.emit()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self._stop_game()
        else:
            event.ignore()

    def _load_tracks(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите песни", str(WORKDIR), "Audio files (*.mp3 *.wav *.ogg)")
        if files:
            self.tracks = [Path(f) for f in files]
            if len(self.tracks) >= 2:
                self.start_btn.setStyleSheet("font-size: 16px; background:#34d399; color:#0b0f14; font-weight:bold;")
                QtWidgets.QMessageBox.information(self, "Успех", f"Загружено {len(self.tracks)} треков. Можно начинать игру!")
            else:
                self.start_btn.setStyleSheet("font-size: 16px; background:#374151; color:#ffffff;")
                QtWidgets.QMessageBox.warning(self, "Недостаточно треков", 
                                           "Для игры нужно загрузить минимум 2 трека!\n"
                                           f"Сейчас загружено: {len(self.tracks)}")

    def _start_round(self):
        if len(self.tracks) < 2:
            QtWidgets.QMessageBox.warning(self, "Недостаточно треков", 
                                       "Для начала игры нужно загрузить минимум 2 трека!\n"
                                       f"Сейчас загружено: {len(self.tracks)}")
            return
            
        if pygame is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "PyGame не инициализирован!")
            return
            
        correct = random.choice(self.tracks)
        options = set([correct])
        
        while len(options) < min(4, len(self.tracks)):
            options.add(random.choice(self.tracks))
            
        options = list(options)
        random.shuffle(options)
        
        for b, p in zip(self.buttons, options):
            b.setText(p.stem)
            b.setProperty("path", str(p))
            
        self.current_answer = correct
        
        try:
            pygame.mixer.music.load(str(correct))
            pygame.mixer.music.play()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка воспроизведения", f"Не удалось воспроизвести трек: {e}")

    def _make_handler(self, btn: QtWidgets.QPushButton):
        def handler():
            if self.current_answer is None:
                QtWidgets.QMessageBox.information(self, "Информация", "Сначала нажмите 'Начать'!")
                return
                
            chosen = Path(btn.property("path") or "")
            if chosen.name == self.current_answer.name:
                QtWidgets.QMessageBox.information(self, "Результат", "Верно! 🎉 Игра продолжается.")
                self._start_round()
            else:
                # Останавливаем музыку при неправильном ответе
                if pygame is not None:
                    pygame.mixer.music.stop()
                reply = QtWidgets.QMessageBox.question(self, "Неверно", 
                                                    "Вы проиграли. 😔\n\nПопробовать снова?", 
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self._start_round()
                else:
                    # Останавливаем звуки при выходе
                    if pygame is not None:
                        pygame.mixer.music.stop()
                    self.goBack.emit()
        return handler
          
class NotesGame(QtWidgets.QWidget):
    goBack = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        
        top = BackTopBar("Ноты")
        top.goBack.connect(self._exit_game)

        self.canvas = QtWidgets.QLabel()
        self.canvas.setStyleSheet("background:#0e1a0e;")
        self.canvas.setMinimumSize(400, 300)
        
        self.platform_w = 160
        self.platform_x = 400
        
        self.notes: list[dict] = []
        self.score = 0
        self.target = 100
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.setInterval(30)

        self.miss_sound = None
        if pygame and ASSET_SFX_POP.exists():
            try:
                self.miss_sound = pygame.mixer.Sound(str(ASSET_SFX_POP))
            except Exception:
                pass

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(top)
        layout.addWidget(self.canvas, 1)
        
        controls = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Старт")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setStyleSheet("font-size: 16px;")
        self.start_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.start_btn.clicked.connect(self._start)
        
        self.stop_btn = QtWidgets.QPushButton("Стоп")
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setStyleSheet("font-size: 16px;")
        self.stop_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.stop_btn.clicked.connect(self._exit_game)
        
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)

        self._draw()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if not self.canvas:
            return
            
        canvas_pos = self.canvas.mapFromParent(event.pos())
        if not self.canvas.rect().contains(canvas_pos):
            return
            
        canvas_width = self.canvas.width()
        self.platform_x = max(self.platform_w // 2, 
                             min(canvas_pos.x(), 
                                 canvas_width - self.platform_w // 2))
        self._draw()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self._exit_game()
        else:
            event.ignore()

    def _start(self):
        self.score = 0
        self.notes.clear()
        self.timer.start(30)

    def _spawn_note(self):
        if not self.canvas:
            return
            
        w = self.canvas.width()
        x = random.randint(50, max(50, w - 50))
        note = random.choice(["C", "D", "E", "F", "G", "A", "B"])
        self.notes.append({"x": x, "y": -30, "note": note, "missed": False})

    def _play_note(self, note: str):
        freq = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, 
               "G": 392.00, "A": 440.00, "B": 493.88}
        try:
            import numpy as np
            sr = 22050
            t = np.linspace(0, 0.35, int(sr * 0.35), False)
            wave = (0.5 * np.sin(2 * np.pi * freq[note] * t)).astype(np.float32)
            arr = (wave * 32767).astype(np.int16)
            snd = pygame.mixer.Sound(buffer=arr.tobytes())
            snd.play()
        except Exception:
            pass

    def _play_miss_sound(self):
        if self.miss_sound:
            try:
                self.miss_sound.play()
            except Exception:
                pass

    def _tick(self):
        if not self.canvas:
            return
            
        spawn_chance = 0.03
        if random.random() < spawn_chance:
            self._spawn_note()
            
        h = self.canvas.height()
        platform_y = h - 60
        
        for item in list(self.notes):
            speed = 4
            item["y"] += speed
            
            if (platform_y - 25 <= item["y"] <= platform_y + 15 and 
                abs(item["x"] - self.platform_x) <= self.platform_w / 2):
                self.score += 1
                self._play_note(item["note"])
                self.notes.remove(item)
                
                if self.score >= self.target:
                    self._win_game()
                    return
                    
            elif item["y"] > h and not item["missed"]:
                item["missed"] = True
                self.score = max(0, self.score - 0.5)
                self._play_miss_sound()
                self.notes.remove(item)
                
        self._draw()

    def _win_game(self):
        self.timer.stop()
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Победа!")
        msg.setText(f"🎉 Поздравляем! 🎉\n\nВы поймали {self.target} нот!\n\nИгра завершена.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.buttonClicked.connect(self._exit_game)
        msg.exec_()

    def _exit_game(self):
        """Выход из игры с остановкой звуков"""
        self.timer.stop()
        if pygame is not None:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
            except Exception:
                pass
        self.goBack.emit()

    def _draw(self):
        if not self.canvas or self.canvas.size().isEmpty():
            return
            
        try:
            pix = QtGui.QPixmap(self.canvas.size())
            pix.fill(QtGui.QColor("#0e1a0e"))
            p = QtGui.QPainter(pix)
            p.setRenderHint(QtGui.QPainter.Antialiasing)
            
            canvas_width = self.canvas.width()
            canvas_height = self.canvas.height()
            
            self.platform_w = max(120, min(200, canvas_width // 5))
            
            for item in self.notes:
                color_map = {
                    "C": QtGui.QColor("#ef4444"), "D": QtGui.QColor("#f97316"),
                    "E": QtGui.QColor("#f59e0b"), "F": QtGui.QColor("#22c55e"),
                    "G": QtGui.QColor("#06b6d4"), "A": QtGui.QColor("#3b82f6"),
                    "B": QtGui.QColor("#8b5cf6"),
                }
                ru_map = {"C":"до", "D":"ре", "E":"ми", "F":"фа", "G":"соль", "A":"ля", "B":"си"}
                
                note_size = max(20, min(40, canvas_width // 25))
                p.setBrush(color_map.get(item["note"], QtGui.QColor("#66bb6a")))
                p.setPen(QtCore.Qt.NoPen)
                p.drawEllipse(QtCore.QRectF(item["x"] - note_size/2, item["y"] - note_size/2, note_size, note_size))
                
                p.setPen(QtGui.QPen(QtGui.QColor("#111827")))
                font_size = max(8, note_size // 3)
                p.setFont(QtGui.QFont("Arial", font_size))
                p.drawText(QtCore.QRectF(item["x"] - note_size, item["y"] - note_size - 10, 
                                       note_size * 2, 20), 
                         QtCore.Qt.AlignCenter, ru_map.get(item["note"], item["note"]))
            
            platform_height = max(15, canvas_height // 30)
            p.setBrush(QtGui.QColor("#eeeeee"))
            p.drawRoundedRect(QtCore.QRectF(self.platform_x - self.platform_w/2, 
                                          canvas_height - 60, 
                                          self.platform_w, platform_height), 8, 8)
            
            p.setPen(QtGui.QPen(QtGui.QColor("white")))
            font_size = max(14, canvas_width // 70)
            p.setFont(QtGui.QFont("Arial", font_size, QtGui.QFont.Bold))
            p.drawText(20, 30, f"Счёт: {self.score}/{self.target}")
            
            progress_width = canvas_width - 40
            progress_height = max(8, canvas_height // 80)
            progress_x = 20
            progress_y = 50
            
            p.setBrush(QtGui.QColor("#374151"))
            p.drawRoundedRect(progress_x, progress_y, progress_width, progress_height, 4, 4)
            
            progress = min(1.0, self.score / self.target)
            filled_width = int(progress_width * progress)
            p.setBrush(QtGui.QColor("#10b981"))
            p.drawRoundedRect(progress_x, progress_y, filled_width, progress_height, 4, 4)
            
            hint_text = "Управление: двигайте мышью по полю • ESC: выход"
            p.setFont(QtGui.QFont("Arial", max(10, canvas_width // 100)))
            p.drawText(10, canvas_height - 10, hint_text)
            
            p.end()
            self.canvas.setPixmap(pix)
        except Exception as e:
            print(f"Ошибка отрисовки: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.canvas and self.platform_x == 0:
            self.platform_x = self.canvas.width() // 2
        self._draw()

class RootWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 700)
        
        self.setStyleSheet("""
            QPushButton:focus { outline: none; }
            QPushButton { background:#e5e7eb; color:#111827; border:1px solid #d1d5db; border-radius:10px; padding:10px 14px; }
            QPushButton:hover { background:#dbe1e7; }
        """)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenu()
        self.player = MusicPlayerWidget()
        self.soundpad = SoundpadWidget()
        self.wheel = WheelWidget()
        self.games = GamesMenu()
        self.melody_rain = MelodyRainGame()
        self.notes = NotesGame()
        self.guess = GuessSongGame()
        self.music_farm = MusicFarmGame()
        self.simulator = PianoXylophoneSimulator()

        for w in [self.main_menu, self.player, self.soundpad, self.wheel, self.games, 
                 self.melody_rain, self.notes, self.guess, self.music_farm, self.simulator]:
            self.stack.addWidget(w)

        self._setup_connections()
        self._goto("main")

    def _setup_connections(self):
        """Настройка соединений для навигации"""
        self.main_menu.navigateTo.connect(self._goto)
        self.player.goBack.connect(lambda: self._goto("main"))
        self.soundpad.goBack.connect(lambda: self._goto("main"))
        self.wheel.goBack.connect(lambda: self._goto("main"))
        self.wheel.openGames.connect(lambda: self._goto("games"))
        self.games.goBack.connect(lambda: self._goto("wheel"))
        self.games.openBalls.connect(lambda: self._goto("melody_rain"))
        self.games.openNotes.connect(lambda: self._goto("notes"))
        self.games.openGuess.connect(lambda: self._goto("guess"))
        self.melody_rain.goBack.connect(lambda: self._goto("games"))
        self.notes.goBack.connect(lambda: self._goto("games"))
        self.guess.goBack.connect(lambda: self._goto("games"))
        self.games.openFarm.connect(lambda: self._goto("music_farm"))
        self.music_farm.goBack.connect(lambda: self._goto("games"))
        self.games.openSimulator.connect(lambda: self._goto("simulator"))
        self.simulator.goBack.connect(lambda: self._goto("games"))

    def _stop_all_sounds(self):
        """Останавливает все звуки и музыку"""
        if pygame is not None:
            try:
                # Останавливаем музыку
                pygame.mixer.music.stop()
                # Останавливаем все звуковые эффекты
                pygame.mixer.stop()
                # Дополнительно: останавливаем все каналы
                for i in range(pygame.mixer.get_num_channels()):
                    pygame.mixer.Channel(i).stop()
            except Exception as e:
                print(f"Ошибка при остановке звуков: {e}")

    def _goto(self, where: str):
        """Переход между экранами с остановкой звуков"""
        # Останавливаем все звуки перед переходом
        self._stop_all_sounds()
        
        mapping = {
            "main": self.main_menu,
            "player": self.player,
            "soundpad": self.soundpad,
            "wheel": self.wheel,
            "games": self.games,
            "melody_rain": self.melody_rain,
            "notes": self.notes,
            "guess": self.guess,
            "music_farm": self.music_farm,
            "simulator": self.simulator,
        }

        target_widget = mapping.get(where, self.main_menu)
        self.stack.setCurrentWidget(target_widget)

        # Управление паузой для музыкальной фермы
        if hasattr(self, 'music_farm'):
            if where == "music_farm":
                self.music_farm.resume_game()
            else:
                self.music_farm.pause_game()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # Обработка клавиш для музыкального плеера
        current_widget = self.stack.currentWidget()
        if current_widget == self.player:
            if event.key() == QtCore.Qt.Key_Left:
                self.player._seek_backward()
                event.accept()
                return
            elif event.key() == QtCore.Qt.Key_Right:
                self.player._seek_forward()
                event.accept()
                return
            elif event.key() == QtCore.Qt.Key_Space:
                self.player._toggle_play()
                event.accept()
                return
        
        if event.key() == QtCore.Qt.Key_Escape:
            # Используем наш метод для остановки звуков
            self._stop_all_sounds()
            
            curr = self.stack.currentWidget()
            if curr in (self.player, self.soundpad, self.wheel, self.simulator):
                self._goto("main")
            elif curr in (self.games, self.melody_rain, self.notes, self.guess, self.music_farm):
                self._goto("wheel")
            else:
                dlg = ConfirmExitDialog(self)
                if dlg.exec_() == QtWidgets.QMessageBox.AcceptRole:
                    QtWidgets.QApplication.quit()
            event.accept()
        else:
            event.ignore()

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RootWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


