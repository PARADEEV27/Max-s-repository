import pygame
import sys
import math
import array
import os

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

# Градиентный фон
def create_gradient_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        # Градиент от темно-синего к фиолетовому
        r = int(25 + (y / HEIGHT) * 10)
        g = int(25 + (y / HEIGHT) * 5)
        b = int(35 + (y / HEIGHT) * 20)
        pygame.draw.line(background, (r, g, b), (0, y), (WIDTH, y))
    return background

# Создание стильной кнопки
def draw_styled_button(surface, rect, color, hover_color, text, font, icon=None):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    
    # Цвет кнопки
    btn_color = hover_color if is_hover else color
    
    # Тень
    shadow_rect = rect.copy()
    shadow_rect.y += 3
    pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=12)
    
    # Основная кнопка
    pygame.draw.rect(surface, btn_color, rect, border_radius=12)
    pygame.draw.rect(surface, (255, 255, 255, 50), rect, 2, border_radius=12)
    
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
    pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=15)
    
    # Карта
    pygame.draw.rect(surface, color, rect, border_radius=15)
    pygame.draw.rect(surface, (255, 255, 255, 30), rect, 2, border_radius=15)

# Переменные для файлового браузера
file_browser_active = False
current_directory = os.path.expanduser("~")
files_list = []
current_selection = 0
scroll_offset = 0

# Переменные для управления воспроизведением
loaded_sound = None
current_sound_name = "Выберите трек"
sound_channel = None
is_playing = False
is_paused = False
progress = 0

# Создание фона
background = create_gradient_background()

# Создание кнопок
button_height = 45
button_width = 140
button_spacing = 20

play_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 400, button_width, button_height)
pause_button_rect = pygame.Rect(WIDTH//2 - button_width - button_spacing//2, 455, button_width, button_height)
stop_button_rect = pygame.Rect(WIDTH//2 + button_spacing//2, 455, button_width, button_height)
load_button_rect = pygame.Rect(WIDTH//2 - button_width//2, 510, button_width, button_height)

# Область для информации о треке
info_card_rect = pygame.Rect(50, 50, WIDTH-100, 120)
cover_rect = pygame.Rect(WIDTH//2 - 80, 180, 160, 160)

# Функция для получения списка файлов и папок
def get_files_list(directory):
    try:
        items = []
        # Добавляем родительскую директорию (если не корневая)
        if directory != "/":
            parent_dir = os.path.dirname(directory)
            if parent_dir != directory:  # Проверяем, что это не корневая директория
                items.append(("..", True, parent_dir))
        
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
    global loaded_sound, current_sound_name, sound_channel, is_playing, is_paused, progress
    try:
        loaded_sound = pygame.mixer.Sound(file_path)
        current_sound_name = os.path.basename(file_path)
        print(f"Звук загружен: {current_sound_name}")
        
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
            
            sound_name = current_sound_name if loaded_sound else "Базовый звук"
            print(f"Воспроизводится: {sound_name}")

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
    
    # Обновление прогресса воспроизведения
    if is_playing and sound_channel and sound_channel.get_busy():
        progress = min(progress + 0.016, 100)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
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
                            if load_sound_file(full_path):
                                file_browser_active = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесико мыши вверх
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.button == 5:  # Колесико мыши вниз
                    scroll_offset = min(len(files_list) - 10, scroll_offset + 1)
        
        else:
            # Обработка событий в основном режиме
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    play_sound()
                
                elif pause_button_rect.collidepoint(event.pos):
                    pause_sound()
                
                elif stop_button_rect.collidepoint(event.pos):
                    stop_sound()
                
                elif load_button_rect.collidepoint(event.pos):
                    file_browser_active = True
                    files_list = get_files_list(current_directory)
                    current_selection = 0
                    scroll_offset = 0
    
    # Отрисовка
    screen.blit(background, (0, 0))
    
    if file_browser_active:
        # Стильный файловый браузер
        browser_rect = pygame.Rect(30, 30, WIDTH-60, HEIGHT-60)
        draw_card(screen, browser_rect, CARD_BG)
        
        # Заголовок
        title = main_font.render("Файловый браузер", True, TEXT_WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Путь текущей директории
        path_text = small_font.render(f"Папка: {current_directory}", True, TEXT_GRAY)
        screen.blit(path_text, (50, 80))
        
        # Список файлов
        visible_files = files_list[scroll_offset:scroll_offset + 15]
        for i, (item, is_dir, full_path) in enumerate(visible_files):
            y_pos = 110 + i * 30
            
            # Подсветка выбранного элемента
            if scroll_offset + i == current_selection:
                pygame.draw.rect(screen, ACCENT, (40, y_pos-2, WIDTH-80, 28), border_radius=6)
            
            # Иконка и цвет текста
            color = TEXT_GRAY if is_dir else TEXT_WHITE
            prefix = "/ " if is_dir else "- "
            
            # Обрезаем длинные имена
            display_text = item
            if len(display_text) > 35:
                display_text = display_text[:32] + "..."
            
            text = small_font.render(prefix + display_text, True, color)
            screen.blit(text, (50, y_pos))
        
        # Инструкция
        help_text = small_font.render("↑/↓: Навигация  |  Enter: Выбрать  |  Esc: Назад", True, TEXT_GRAY)
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT-40))
    
    else:
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
        icon_text = icon_font.render(icon, True, ACCENT if is_playing else TEXT_GRAY)
        screen.blit(icon_text, (center_x - icon_text.get_width()//2, center_y - icon_text.get_height()//2))
        
        # Кнопки управления
        draw_styled_button(screen, play_button_rect, ACCENT, ACCENT_HOVER, "Играть", main_font, "")
        draw_styled_button(screen, pause_button_rect, PAUSE, PAUSE_HOVER, "Пауза", main_font, "II")
        draw_styled_button(screen, stop_button_rect, STOP, STOP_HOVER, "Стоп", main_font, "X")
        draw_styled_button(screen, load_button_rect, LOAD_BG, LOAD_HOVER, "Загрузить", main_font, "")
        
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

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение
pygame.quit()
sys.exit()