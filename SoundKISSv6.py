import pygame
import sys
import math
import array
import os
import random

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Создание окна
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SoundKiss")

# Цвета
DARK_BG = (25, 25, 35)
CARD_BG = (40, 40, 55)
ACCENT = (0, 200, 150)
ACCENT_HOVER = (0, 230, 180)
ACCENT_ACTIVE = (0, 180, 130)
PAUSE = (255, 184, 77)
PAUSE_HOVER = (255, 204, 107)
STOP = (255, 107, 107)
STOP_HOVER = (255, 137, 137)
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (180, 180, 200)
LOAD_BG = (86, 126, 255)
LOAD_HOVER = (106, 146, 255)
MENU_BG = (45, 45, 65)
MENU_HOVER = (65, 65, 85)
RANDOM_COLORS = [
    (255, 107, 107),    # Красный
    (255, 184, 77),     # Оранжевый
    (255, 230, 100),    # Желтый
    (0, 200, 150),      # Зеленый
    (86, 126, 255),     # Синий
    (180, 100, 255),    # Фиолетовый
    (255, 100, 200),    # Розовый
    (100, 255, 200),    # Бирюзовый
]

# Новые правильные цвета для кнопок
RANDOM_BG = (180, 100, 255)        # Фиолетовый (RGB)
RANDOM_HOVER = (200, 120, 25)     # Более светлый фиолетовый

# Состояния приложения
APP_STATES = {
    "WELCOME": 0,
    "MODE_SELECT": 1,
    "MUSIC_PLAYER": 2,
    "SOUNDPAD": 3,
    "RANDOM": 4
}
current_state = APP_STATES["WELCOME"]

# Создаем папку Sounds если ее нет
SOUNDS_DIR = "Sounds"
if not os.path.exists(SOUNDS_DIR):
    os.makedirs(SOUNDS_DIR)

# Градиентный фон (создаем один раз для оптимизации)
background = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    # Градиент от темно-синего к фиолетовому
    r = int(25 + (y / HEIGHT) * 10)
    g = int(25 + (y / HEIGHT) * 5)
    b = int(35 + (y / HEIGHT) * 20)
    pygame.draw.line(background, (r, g, b), (0, y), (WIDTH, y))

# Создание стильной кнопки
def draw_styled_button(surface, rect, color, hover_color, text, font, icon=None):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    
    # Цвет кнопки
    btn_color = hover_color if is_hover else color
    
    # Тень (используем правильный формат цвета с альфа-каналом через Surface)
    shadow_surf = pygame.Surface((rect.width, rect.height + 3), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 3, rect.width, rect.height), border_radius=12)
    surface.blit(shadow_surf, rect.topleft)
    
    # Основная кнопка
    pygame.draw.rect(surface, btn_color, rect, border_radius=12)
    
    # Граница с альфа-каналом
    border_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (255, 255, 255, 50), (0, 0, rect.width, rect.height), 2, border_radius=12)
    surface.blit(border_surf, rect.topleft)
    
    # Текст
    text_surf = font.render(text, True, TEXT_WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    
    if icon:
        # Если есть иконка, смещаем текст немного вправо
        text_rect.x += 15
        icon_surf = font.render(icon, True, TEXT_WHITE)
        icon_rect = icon_surf.get_rect(center=(rect.centerx - text_surf.get_width()//2 - 10, rect.centery))
        surface.blit(icon_surf, icon_rect)
    
    surface.blit(text_surf, text_rect)
    return is_hover

# Создание карты
def draw_card(surface, rect, color):
    # Тень
    shadow_rect = rect.copy()
    shadow_rect.y += 4
    pygame.draw.rect(surface, (50, 50, 70), shadow_rect, border_radius=15)
    
    # Карта
    pygame.draw.rect(surface, color, rect, border_radius=15)
    
    # Граница с альфа-каналом
    border_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (255, 255, 255, 30), (0, 0, rect.width, rect.height), 2, border_radius=15)
    surface.blit(border_surf, rect.topleft)

# Переменные для файлового браузера
file_browser_active = False
current_directory = os.path.expanduser("~")
files_list = []
current_selection = 0
scroll_offset = 0
soundpad_slot_to_load = 0
file_browser_mode = "music"  # "music" или "soundpad"

# Переменные для управления воспроизведением
loaded_sound = None
current_sound_name = "Выберите трек"
sound_channel = None
is_playing = False
is_paused = False
progress = 0
sound_length = 0  # Длительность звука в секундах

# Переменные для саундпада
soundpad_sounds = [None] * 20
soundpad_names = [f"Слот {i+1}" for i in range(20)]
soundpad_channels = [None] * 20  # Отдельные каналы для каждого слота саундпада

# Переменные для режима Рандом
wheel_angle = 0
wheel_spinning = False
wheel_speed = 0
selected_sector = -1
spin_start_time = 0
wheel_radius = 150
wheel_sectors = 8

# Создание кнопок
button_height = 45
button_width = 140
button_spacing = 20

# Центрированные кнопки
play_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 400, button_width, button_height)
pause_button_rect = pygame.Rect(WIDTH//2 - button_width - button_spacing//2, 455, button_width, button_height)
stop_button_rect = pygame.Rect(WIDTH//2 + button_spacing//2, 455, button_width, button_height)
load_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 510, button_width, button_height)

# Кнопки для меню
next_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 500, button_width, button_height)
player_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 300, button_width, button_height)
soundpad_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 370, button_width, button_height)
random_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 440, button_width, button_height)
back_button_rect = pygame.Rect(20, 20, 100, 35)
spin_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 500, button_width, button_height)

# Область для информации о треке
info_card_rect = pygame.Rect(50, 50, WIDTH-100, 120)
cover_rect = pygame.Rect(WIDTH//2 - 80, 180, 160, 160)

# Функция для получения списка файлов и папок
def get_files_list(directory):
    try:
        items = []
        # Добавляем родительскую директорию (если не корневая)
        if directory != os.path.dirname(directory):
            items.append(("..", True, os.path.dirname(directory)))
        
        for item in sorted(os.listdir(directory)):
            full_path = os.path.join(directory, item)
            is_dir = os.path.isdir(full_path)
            # Показываем только папки и аудио файлы
            if is_dir or item.lower().endswith(('.wav', '.ogg', '.mp3', '.flac')):
                items.append((item, is_dir, full_path))
        
        return items
    except PermissionError:
        print("Нет доступа к директории")
        return []
    except Exception as e:
        print(f"Ошибка при чтении директории: {e}")
        return []

# Функция для загрузки звука
def load_sound_file(file_path):
    global loaded_sound, current_sound_name, sound_channel, is_playing, is_paused, progress, sound_length
    try:
        loaded_sound = pygame.mixer.Sound(file_path)
        current_sound_name = os.path.basename(file_path)
        sound_length = loaded_sound.get_length() if hasattr(loaded_sound, 'get_length') else 0
        print(f"Звук загружен: {current_sound_name}, длительность: {sound_length:.2f} сек.")
        
        # Останавливаем текущее воспроизведение
        if sound_channel:
            sound_channel.stop()
        is_playing = False
        is_paused = False
        progress = 0
        
        return True
    except Exception as e:
        print(f"Ошибка загрузки звука: {e}")
        return False

# Функция для загрузки звука в саундпад
def load_soundpad_sound(file_path, slot_index):
    try:
        soundpad_sounds[slot_index] = pygame.mixer.Sound(file_path)
        soundpad_names[slot_index] = os.path.basename(file_path)
        print(f"Звук загружен в слот {slot_index+1}: {soundpad_names[slot_index]}")
        return True
    except Exception as e:
        print(f"Ошибка загрузки звука: {e}")
        return False

# Функция для воспроизведения звука
def play_sound():
    global sound_channel, is_playing, is_paused, progress
    
    if loaded_sound or base_sound:
        if is_paused:
            # Продолжаем воспроизведение с паузы
            if sound_channel:
                sound_channel.unpause()
                is_paused = False
                is_playing = True
                print("Воспроизведение продолжено")
        else:
            # Начинаем новое воспроизведение
            if sound_channel:
                sound_channel.stop()
            
            sound_to_play = loaded_sound if loaded_sound else base_sound
            sound_channel = sound_to_play.play()
            is_playing = True
            is_paused = False
            progress = 0
            
            sound_name = current_sound_name if loaded_sound else "Базовый звук"
            print(f"Воспроизводится: {sound_name}")

# Функция для воспроизведения звука из саундпада
def play_soundpad_sound(slot_index):
    if soundpad_sounds[slot_index]:
        # Останавливаем предыдущее воспроизведение в этом слоте, если оно есть
        if soundpad_channels[slot_index] and soundpad_channels[slot_index].get_busy():
            soundpad_channels[slot_index].stop()
        
        soundpad_channels[slot_index] = soundpad_sounds[slot_index].play()
        print(f"Воспроизводится: {soundpad_names[slot_index]}")
        return soundpad_channels[slot_index]
    return None

# Функция для паузы
def pause_sound():
    global is_playing, is_paused
    
    if is_playing and sound_channel and not is_paused:
        sound_channel.pause()
        is_paused = True
        is_playing = False
        print("Воспроизведение на паузе")

# Функция для остановки
def stop_sound():
    global is_playing, is_paused, progress
    
    if sound_channel and (is_playing or is_paused):
        sound_channel.stop()
        is_playing = False
        is_paused = False
        progress = 0
        print("Воспроизведение остановлено")

# Функция для запуска колеса фортуны
def spin_wheel():
    global wheel_spinning, wheel_speed, spin_start_time
    if not wheel_spinning:
        wheel_spinning = True
        wheel_speed = random.uniform(0.5, 1.0)
        spin_start_time = pygame.time.get_ticks()

# Функция для выбора случайного звука из загруженных
def get_random_loaded_sound():
    loaded_slots = [i for i, sound in enumerate(soundpad_sounds) if sound is not None]
    if loaded_slots:
        return random.choice(loaded_slots)
    return -1

# Создание базового звука
def create_sound():
    try:
        sample_rate = 44100
        duration = 1.0
        frequency = 523.25  # Нота C5
        
        samples = array.array('h')
        for i in range(int(duration * sample_rate)):
            # Более интересный звук с обертонами
            sample = int(32767 * 0.2 * (
                math.sin(2 * math.pi * frequency * i / sample_rate) +
                0.5 * math.sin(2 * math.pi * frequency * 2 * i / sample_rate) +
                0.3 * math.sin(2 * math.pi * frequency * 3 * i / sample_rate)
            ))
            samples.append(sample)
        
        sound = pygame.mixer.Sound(buffer=samples)
        return sound
    except Exception as e:
        print(f"Не удалось создать звук: {e}")
        return None

base_sound = create_sound()

# Шрифты
try:
    title_font = pygame.font.Font(None, 32)
    main_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 22)
    icon_font = pygame.font.Font(None, 36)
except:
    title_font = pygame.font.SysFont('arial', 32, bold=True)
    main_font = pygame.font.SysFont('arial', 28)
    small_font = pygame.font.SysFont('arial', 22)
    icon_font = pygame.font.SysFont('arial', 36)

# Главный цикл
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()
    dt = clock.get_time() / 1000.0  # Дельта времени в секундах
    
    # Обновление прогресса воспроизведения
    if is_playing and sound_channel and sound_channel.get_busy():
        if sound_length > 0:
            progress = min(progress + dt / sound_length * 100, 100)
        else:
            progress = min(progress + dt * 10, 100)  # Запасной вариант, если длительность неизвестна
    
    # Обновление колеса фортуны
    if wheel_spinning:
        wheel_angle += wheel_speed * 10
        wheel_speed *= 0.99  # Замедление
        
        if wheel_speed < 0.01:
            wheel_spinning = False
            # Определяем выбранный сектор
            selected_sector = int((wheel_angle % 360) / (360 / wheel_sectors)) % wheel_sectors
            # Воспроизводим случайный звук
            random_slot = get_random_loaded_sound()
            if random_slot != -1:
                play_soundpad_sound(random_slot)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if file_browser_active:
                # Обработка кликов в файловом браузере
                for i, (item, is_dir, full_path) in enumerate(files_list[scroll_offset:scroll_offset + 10]):
                    y_pos = 110 + i * 30
                    item_rect = pygame.Rect(40, y_pos-2, WIDTH-80, 28)
                    
                    if item_rect.collidepoint(mouse_pos):
                        current_selection = scroll_offset + i
                        
                        # Двойной клик или Enter для выбора
                        if is_dir:
                            # Переходим в директорию
                            current_directory = full_path
                            files_list = get_files_list(current_directory)
                            current_selection = 0
                            scroll_offset = 0
                        else:
                            # Загружаем файл
                            if file_browser_mode == "music":
                                if load_sound_file(full_path):
                                    file_browser_active = False
                            elif file_browser_mode == "soundpad":
                                if load_soundpad_sound(full_path, soundpad_slot_to_load):
                                    file_browser_active = False
                        break
            
            elif current_state == APP_STATES["WELCOME"]:
                if next_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["MODE_SELECT"]
            
            elif current_state == APP_STATES["MODE_SELECT"]:
                if player_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["MUSIC_PLAYER"]
                elif soundpad_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["SOUNDPAD"]
                elif random_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["RANDOM"]
                elif back_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["WELCOME"]
            
            elif current_state == APP_STATES["MUSIC_PLAYER"]:
                if back_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["MODE_SELECT"]
                elif not file_browser_active:
                    if play_button_rect.collidepoint(event.pos):
                        play_sound()
                    elif pause_button_rect.collidepoint(event.pos):
                        pause_sound()
                    elif stop_button_rect.collidepoint(event.pos):
                        stop_sound()
                    elif load_button_rect.collidepoint(event.pos):
                        file_browser_active = True
                        file_browser_mode = "music"
                        files_list = get_files_list(current_directory)
                        current_selection = 0
                        scroll_offset = 0
            
            elif current_state == APP_STATES["SOUNDPAD"]:
                if back_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["MODE_SELECT"]
                
                # Проверка нажатия на кнопки саундпада
                for i in range(20):
                    row = i // 4
                    col = i % 4
                    btn_rect = pygame.Rect(WIDTH//2 - 220 + col * 110, 120 + row * 70, 100, 60)
                    if btn_rect.collidepoint(event.pos):
                        if event.button == 1:  # ЛКМ - воспроизведение
                            play_soundpad_sound(i)
            
            elif current_state == APP_STATES["RANDOM"]:
                if back_button_rect.collidepoint(event.pos):
                    current_state = APP_STATES["MODE_SELECT"]
                elif spin_button_rect.collidepoint(event.pos):
                    spin_wheel()
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Правая кнопка мыши
            if current_state == APP_STATES["SOUNDPAD"] and not file_browser_active:
                # Проверка нажатия правой кнопкой на кнопки саундпада
                for i in range(20):
                    row = i // 4
                    col = i % 4
                    btn_rect = pygame.Rect(WIDTH//2 - 220 + col * 110, 120 + row * 70, 100, 60)
                    if btn_rect.collidepoint(event.pos):
                        file_browser_active = True
                        file_browser_mode = "soundpad"
                        soundpad_slot_to_load = i
                        # Открываем папку Sounds по умолчанию для саундпада
                        if os.path.exists(SOUNDS_DIR):
                            current_directory = SOUNDS_DIR
                        files_list = get_files_list(current_directory)
                        current_selection = 0
                        scroll_offset = 0
        
        elif file_browser_active:
            # Обработка событий в файловом браузере
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    file_browser_active = False
                elif event.key == pygame.K_UP and current_selection > 0:
                    current_selection -= 1
                    if current_selection < scroll_offset:
                        scroll_offset = current_selection
                elif event.key == pygame.K_DOWN and current_selection < len(files_list) - 1:
                    current_selection += 1
                    if current_selection >= scroll_offset + 10:
                        scroll_offset += 1
                elif event.key == pygame.K_RETURN:
                    if files_list:
                        selected_item, is_dir, full_path = files_list[current_selection]
                        if is_dir:
                            # Переходим в директорию
                            current_directory = full_path
                            files_list = get_files_list(current_directory)
                            current_selection = 0
                            scroll_offset = 0
                        else:
                            # Пытаемся загрузить звук
                            if file_browser_mode == "music":
                                if load_sound_file(full_path):
                                    file_browser_active = False
                            elif file_browser_mode == "soundpad":
                                if load_soundpad_sound(full_path, soundpad_slot_to_load):
                                    file_browser_active = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесико мыши вверх
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.button == 5:  # Колесико мыши вниз
                    scroll_offset = min(len(files_list) - 10, scroll_offset + 1)
    
    # Отрисовка
    screen.blit(background, (0, 0))
    
    if file_browser_active:
        # Стильный файловый браузер
        browser_rect = pygame.Rect(30, 30, WIDTH-60, HEIGHT-60)
        draw_card(screen, browser_rect, CARD_BG)
        
        # Заголовок
        title_text = "Файловый браузер - "
        title_text += "Музыкальный плеер" if file_browser_mode == "music" else "Саундпад"
        title = main_font.render(title_text, True, TEXT_WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Путь текульной директории
        path_text = small_font.render(f"Папка: {current_directory}", True, TEXT_GRAY)
        screen.blit(path_text, (50, 80))
        
        # Полоса прокрутки
        if len(files_list) > 10:
            scrollbar_height = 300
            scrollbar_pos = 50 + (scroll_offset / len(files_list)) * scrollbar_height
            pygame.draw.rect(screen, (80, 80, 100), (WIDTH-70, 110, 10, scrollbar_height), border_radius=5)
            pygame.draw.rect(screen, ACCENT, (WIDTH-70, 110 + scrollbar_pos, 10, 
                                            max(20, scrollbar_height * 10 / len(files_list))), border_radius=5)
        
        # Список файлов
        visible_files = files_list[scroll_offset:scroll_offset + 10]
        for i, (item, is_dir, full_path) in enumerate(visible_files):
            y_pos = 110 + i * 30
            
            # Подсветка выбранного элемента
            if scroll_offset + i == current_selection:
                pygame.draw.rect(screen, ACCENT, (40, y_pos-2, WIDTH-80, 28), border_radius=6)
            
            # Иконка и цвет текста
            color = TEXT_GRAY if is_dir else TEXT_WHITE
            prefix = "📁 " if is_dir else "🎵 "
            
            # Обрезаем длинные имена
            display_text = item
            if len(display_text) > 35:
                display_text = display_text[:32] + "..."
            
            text = small_font.render(prefix + display_text, True, color)
            screen.blit(text, (50, y_pos))
        
        # Инструкция
        help_text = small_font.render("ЛКМ: Выбрать | ↑/↓: Навигация | Enter: Выбрать | Esc: Назад", True, TEXT_GRAY)
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT-40))
    
    else:
        if current_state == APP_STATES["WELCOME"]:
            # Приветственный экран
            welcome_rect = pygame.Rect(50, 100, WIDTH-100, HEIGHT-250)
            draw_card(screen, welcome_rect, CARD_BG)
            
            # Заголовок
            title = title_font.render("SoundKiss", True, TEXT_WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 130))
            
            # Информация об авторе
            author_text = main_font.render("Приложение создал", True, TEXT_GRAY)
            screen.blit(author_text, (WIDTH//2 - author_text.get_width()//2, 180))
            
            name_text = title_font.render("Гапотченко Максим Олегович", True, ACCENT)
            screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, 220))
            
            # Кнопка "Далее"
            draw_styled_button(screen, next_button_rect, ACCENT, ACCENT_HOVER, "Далее", main_font, "→")
        
        elif current_state == APP_STATES["MODE_SELECT"]:
            # Экран выбора режима
            mode_rect = pygame.Rect(50, 100, WIDTH-100, HEIGHT-250)
            draw_card(screen, mode_rect, CARD_BG)
            
            # Заголовок
            title = title_font.render("Выберите режим", True, TEXT_WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 130))
            
            # Кнопки выбора режима
            draw_styled_button(screen, player_button_rect, ACCENT, ACCENT_HOVER, "Музыкальный плеер", main_font, "♫")
            draw_styled_button(screen, soundpad_button_rect, LOAD_BG, LOAD_HOVER, "Саундпад", main_font, "♪")
            draw_styled_button(screen, random_button_rect, RANDOM_BG, RANDOM_HOVER, "Рандом", main_font, "🎲")
            
            # Кнопка "Назад" в левом верхнем углу
            draw_styled_button(screen, back_button_rect, MENU_BG, MENU_HOVER, "Назад", small_font)
        
        elif current_state == APP_STATES["MUSIC_PLAYER"]:
            # Основной интерфейс плеера
            
            # Карта с информацией о треке
            draw_card(screen, info_card_rect, CARD_BG)
            
            # Название трека
            display_name = current_sound_name
            if len(display_name) > 25:
                display_name = display_name[:22] + "..."
            
            title_text = title_font.render(display_name, True, TEXT_WHITE)
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 70))
            
            # Статус
            if is_playing:
                status = "ВОСПРОИЗВЕДЕНИЕ"
                color = ACCENT
            elif is_paused:
                status = "II ПАУЗА"
                color = PAUSE
            else:
                status = "ОСТАНОВЛЕНО"
                color = TEXT_GRAY
            
            status_text = main_font.render(status, True, color)
            screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, 105))
            
            # Визуализатор обложки
            draw_card(screen, cover_rect, (50, 50, 70))
            
            # Анимированные волны в центре обложки
            time = pygame.time.get_ticks() / 1000
            center_x, center_y = cover_rect.center
            
            # Рисуем анимированные звуковые волны
            for i in range(3):
                radius = 30 + abs(math.sin(time * 2 + i) * 15)
                alpha = 150 - i * 40
                wave_color = (ACCENT[0], ACCENT[1], ACCENT[2], alpha) if is_playing else (TEXT_GRAY[0], TEXT_GRAY[1], TEXT_GRAY[2], alpha)
                
                wave_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, wave_color, (radius, radius), radius, 3)
                screen.blit(wave_surf, (center_x - radius, center_y - radius))
            
            # Иконка в центре
            icon = "OFF" if not is_playing else "ON"
            icon_text = icon_font.render(icon, True, ACCENT if is_playing else TEXT_WHITE)
            screen.blit(icon_text, (center_x - icon_text.get_width()//2, center_y - icon_text.get_height()//2))
            
            # Кнопки управления
            draw_styled_button(screen, play_button_rect, ACCENT, ACCENT_HOVER, "Играть", main_font, "")
            draw_styled_button(screen, pause_button_rect, PAUSE, PAUSE_HOVER, "Пауза", main_font, "II")
            draw_styled_button(screen, stop_button_rect, STOP, STOP_HOVER, "Стоп", main_font, "X")
            draw_styled_button(screen, load_button_rect, LOAD_BG, LOAD_HOVER, "Загрузить", main_font, "")
            
            # Кнопка "Назад" в левом верхнем углу
            draw_styled_button(screen, back_button_rect, MENU_BG, MENU_HOVER, "Назад", small_font)
            
            # Прогресс-бар
            if loaded_sound or base_sound:
                progress_width = WIDTH - 100
                progress_rect = pygame.Rect(50, 570, progress_width, 6)
                
                # Фон прогресс-бара
                pygame.draw.rect(screen, (60, 60, 80), progress_rect, border_radius=3)
                
                # Заполненная часть
                if progress > 0:
                    fill_width = int(progress_width * (progress / 100))
                    fill_rect = pygame.Rect(50, 570, fill_width, 6)
                    pygame.draw.rect(screen, ACCENT, fill_rect, border_radius=3)
                
                # Ползунок
                slider_pos = 50 + int(progress_width * (progress / 100))
                pygame.draw.circle(screen, TEXT_WHITE, (slider_pos, 573), 8)
                pygame.draw.circle(screen, ACCENT, (slider_pos, 573), 6)
        
        elif current_state == APP_STATES["SOUNDPAD"]:
            # Интерфейс саундпада
            title = title_font.render("Саундпад", True, TEXT_WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            # Кнопка "Назад" в левом верхнем углу
            draw_styled_button(screen, back_button_rect, MENU_BG, MENU_HOVER, "Назад", small_font)
            
            # Информация о папке Sounds
            info_text = small_font.render(f"Звуки хранятся в папке: {SOUNDS_DIR}", True, TEXT_GRAY)
            screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 80))
            
            # Создание кнопок саундпада (центрированных)
            for i in range(20):
                row = i // 4
                col = i % 4
                btn_rect = pygame.Rect(WIDTH//2 - 220 + col * 110, 120 + row * 70, 100, 60)
                
                # Определяем цвет кнопки
                if soundpad_sounds[i]:
                    btn_color = ACCENT
                    hover_color = ACCENT_HOVER
                else:
                    btn_color = MENU_BG
                    hover_color = MENU_HOVER
                
                # Рисуем кнопку
                mouse_pos = pygame.mouse.get_pos()
                is_hover = btn_rect.collidepoint(mouse_pos)
                current_color = hover_color if is_hover else btn_color
                
                pygame.draw.rect(screen, current_color, btn_rect, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255, 50), btn_rect, 2, border_radius=10)
                
                # Отображаем название звука (обрезаем если слишком длинное)
                sound_name = soundpad_names[i]
                if len(sound_name) > 12:
                    sound_name = sound_name[:9] + "..."
                
                text = small_font.render(sound_name, True, TEXT_WHITE)
                screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - 8))
                
                # Номер слота
                slot_text = small_font.render(f"{i+1}", True, TEXT_GRAY)
                screen.blit(slot_text, (btn_rect.centerx - slot_text.get_width()//2, btn_rect.centery + 10))
            
            # Инструкция
            help_text = small_font.render("ЛКМ: воспроизвести | ПКМ: загрузить звук", True, TEXT_GRAY)
            screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT-40))
        
        elif current_state == APP_STATES["RANDOM"]:
            # Интерфейс режима Рандом
            title = title_font.render("Колесо Фортуны", True, TEXT_WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            # Кнопка "Назад" в левом верхнем углу
            draw_styled_button(screen, back_button_rect, MENU_BG, MENU_HOVER, "Назад", small_font)
            
            # Информация
            info_text = small_font.render("Крутите колесо для случайного звука!", True, TEXT_GRAY)
            screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 80))
            
            # Рисуем колесо фортуны
            wheel_center = (WIDTH//2, 250)
            
            # Отрисовка колеса
            for i in range(wheel_sectors):
                start_angle = math.radians(i * (360 / wheel_sectors) + wheel_angle)
                end_angle = math.radians((i + 1) * (360 / wheel_sectors) + wheel_angle)
                
                # Рисуем сектор
                points = [wheel_center]
                for angle in [start_angle + j * 0.1 for j in range(int((end_angle - start_angle) / 0.1) + 1)]:
                    x = wheel_center[0] + wheel_radius * math.cos(angle)
                    y = wheel_center[1] + wheel_radius * math.sin(angle)
                    points.append((x, y))
                
                pygame.draw.polygon(screen, RANDOM_COLORS[i % len(RANDOM_COLORS)], points)
            
            # Центр колеса
            pygame.draw.circle(screen, TEXT_WHITE, wheel_center, 20)
            pygame.draw.circle(screen, (0, 0, 0), wheel_center, 18)
            
            # Указатель
            pointer_points = [
                (WIDTH//2, 100),
                (WIDTH//2 - 15, 130),
                (WIDTH//2 + 15, 130)
            ]
            pygame.draw.polygon(screen, ACCENT, pointer_points)
            
            # Статистика загруженных звуков
            loaded_count = sum(1 for sound in soundpad_sounds if sound is not None)
            stats_text = small_font.render(f"Загружено звуков: {loaded_count}/20", True, TEXT_GRAY)
            screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 350))
            
            # Кнопка вращения
            draw_styled_button(screen, spin_button_rect, RANDOM_BG, RANDOM_HOVER, "Крутить!", main_font, "🎰")
            
            # Результат
            if selected_sector != -1 and not wheel_spinning:
                result_text = main_font.render("Случайный звук воспроизведен!", True, ACCENT)
                screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 400))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение
pygame.quit()
sys.exit()