import pygame
import sys
import math
import array
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Создание окна
WIDTH, HEIGHT = 400, 400  # Увеличили высоту для элементов управления
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SoundKiss")

# Цвета
BACKGROUND = (30, 30, 40)
BUTTON_COLOR = (0, 200, 100)
BUTTON_HOVER = (0, 230, 120)
BUTTON_ACTIVE = (0, 180, 80)
PAUSE_COLOR = (200, 150, 0)
PAUSE_HOVER = (230, 170, 0)
STOP_COLOR = (200, 50, 50)
STOP_HOVER = (230, 70, 70)
TEXT_COLOR = (255, 255, 255)
LOAD_BUTTON_COLOR = (70, 130, 200)
LOAD_BUTTON_HOVER = (90, 150, 230)

# Переменные для файлового браузера
file_browser_active = False
current_directory = os.path.expanduser("~")
files_list = []
current_selection = 0
scroll_offset = 0

# Переменные для управления воспроизведением
loaded_sound = None
current_sound_name = "Базовый звук"
sound_channel = None
is_playing = False
is_paused = False

# Загрузка фонового изображения
def load_background_image(image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Файл {image_path} не найден!")
            return None
        
        background = pygame.image.load(image_path)
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        print(f"Фоновое изображение загружено: {image_path}")
        return background
        
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")
        return None

# Укажите путь к вашему изображению
IMAGE_PATH = "/home/max/Документы/Programs/SoundKiISS/kissback.jpeg"

# Загружаем фоновое изображение
background_image = load_background_image(IMAGE_PATH)

# Создание кнопок
play_button_rect = pygame.Rect(100, 100, 200, 40)
pause_button_rect = pygame.Rect(100, 150, 95, 40)
stop_button_rect = pygame.Rect(205, 150, 95, 40)
load_button_rect = pygame.Rect(100, 200, 200, 40)
is_play_hover = False
is_pause_hover = False
is_stop_hover = False
is_load_hover = False

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
            if is_dir or item.lower().endswith(('.wav', '.ogg', '.mp3')):
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
    global loaded_sound, current_sound_name, sound_channel, is_playing, is_paused
    try:
        loaded_sound = pygame.mixer.Sound(file_path)
        current_sound_name = os.path.basename(file_path)
        print(f"Звук загружен: {current_sound_name}")
        
        # Останавливаем текущее воспроизведение
        if sound_channel:
            sound_channel.stop()
        is_playing = False
        is_paused = False
        
        return True
    except Exception as e:
        print(f"Ошибка загрузки звука: {e}")
        return False

# Функция для воспроизведения звука
def play_sound():
    global sound_channel, is_playing, is_paused
    
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
    global is_playing, is_paused
    
    if sound_channel and (is_playing or is_paused):
        sound_channel.stop()
        is_playing = False
        is_paused = False
        print("Воспроизведение остановлено")

# Создание базового звука
def create_sound():
    try:
        sample_rate = 44100
        duration = 0.5
        frequency = 440
        
        samples = array.array('h')
        for i in range(int(duration * sample_rate)):
            sample = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(sample)
        
        sound = pygame.mixer.Sound(buffer=samples)
        return sound
    except Exception as e:
        print(f"Не удалось создать звук: {e}")
        return None

base_sound = create_sound()

# Шрифты
try:
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    file_font = pygame.font.Font(None, 20)
except:
    font = pygame.font.SysFont('arial', 36)
    small_font = pygame.font.SysFont('arial', 24)
    file_font = pygame.font.SysFont('arial', 20)

# Главный цикл
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Проверяем наведение на кнопки
    is_play_hover = play_button_rect.collidepoint(mouse_pos) and not file_browser_active
    is_pause_hover = pause_button_rect.collidepoint(mouse_pos) and not file_browser_active
    is_stop_hover = stop_button_rect.collidepoint(mouse_pos) and not file_browser_active
    is_load_hover = load_button_rect.collidepoint(mouse_pos) and not file_browser_active
    
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
    if background_image:
        screen.blit(background_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill(BACKGROUND)
    
    if file_browser_active:
        # Рисуем файловый браузер
        browser_rect = pygame.Rect(20, 20, WIDTH-40, HEIGHT-40)
        pygame.draw.rect(screen, (50, 50, 60), browser_rect)
        pygame.draw.rect(screen, (100, 100, 120), browser_rect, 2)
        
        # Заголовок
        title_text = f"Папка: {current_directory}"
        title = small_font.render(title_text, True, TEXT_COLOR)
        screen.blit(title, (browser_rect.x + 10, browser_rect.y + 10))
        
        # Список файлов
        visible_files = files_list[scroll_offset:scroll_offset + 12]
        for i, (item, is_dir, full_path) in enumerate(visible_files):
            y_pos = browser_rect.y + 40 + i * 25
            
            # Подсветка выбранного элемента
            if scroll_offset + i == current_selection:
                pygame.draw.rect(screen, (80, 80, 100), 
                                (browser_rect.x + 5, y_pos - 2, browser_rect.width - 10, 24))
            
            # Иконка и цвет текста
            color = (200, 200, 255) if is_dir else TEXT_COLOR
            prefix = "📁 " if is_dir else "🎵 " if item.lower().endswith(('.wav', '.ogg', '.mp3')) else "📄 "
            
            # Обрезаем длинные имена
            display_text = item
            if len(display_text) > 30:
                display_text = display_text[:27] + "..."
            
            text = file_font.render(prefix + display_text, True, color)
            screen.blit(text, (browser_rect.x + 10, y_pos))
        
        # Инструкция
        help_text = small_font.render("Up/Down: Выбор,   Enter: Открыть,  Esc: Отмена", True, (0, 0, 0))
        screen.blit(help_text, (browser_rect.x - 10 , browser_rect.y + browser_rect.height - 1))
    
    else:
        # Основной интерфейс
        # Кнопка воспроизведения
        play_button_color = BUTTON_ACTIVE if pygame.mouse.get_pressed()[0] and is_play_hover else BUTTON_HOVER if is_play_hover else BUTTON_COLOR
        pygame.draw.rect(screen, play_button_color, play_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), play_button_rect, 2, border_radius=8)
        
        # Кнопка паузы
        pause_button_color = PAUSE_HOVER if is_pause_hover else PAUSE_COLOR
        if pygame.mouse.get_pressed()[0] and is_pause_hover:
            pause_button_color = (180, 130, 0)
        pygame.draw.rect(screen, pause_button_color, pause_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), pause_button_rect, 2, border_radius=8)
        
        # Кнопка остановки
        stop_button_color = STOP_HOVER if is_stop_hover else STOP_COLOR
        if pygame.mouse.get_pressed()[0] and is_stop_hover:
            stop_button_color = (180, 30, 30)
        pygame.draw.rect(screen, stop_button_color, stop_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), stop_button_rect, 2, border_radius=8)
        
        # Кнопка загрузки
        load_button_color = LOAD_BUTTON_COLOR
        if is_load_hover:
            load_button_color = LOAD_BUTTON_HOVER
        if pygame.mouse.get_pressed()[0] and is_load_hover:
            load_button_color = (60, 110, 180)
        pygame.draw.rect(screen, load_button_color, load_button_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), load_button_rect, 2, border_radius=8)
        
        # Текст на кнопках
        play_text = small_font.render("> ВОСПРОИВЕСТИ", True, TEXT_COLOR)
        play_text_rect = play_text.get_rect(center=play_button_rect.center)
        screen.blit(play_text, play_text_rect)
        
        pause_text = small_font.render("II ПАУЗА", True, TEXT_COLOR)
        pause_text_rect = pause_text.get_rect(center=pause_button_rect.center)
        screen.blit(pause_text, pause_text_rect)
        
        stop_text = small_font.render("X СТОП", True, TEXT_COLOR)
        stop_text_rect = stop_text.get_rect(center=stop_button_rect.center)
        screen.blit(stop_text, stop_text_rect)
        
        load_text = small_font.render("+ ЗАГРУЗИТЬ ЗВУК", True, TEXT_COLOR)
        load_text_rect = load_text.get_rect(center=load_button_rect.center)
        screen.blit(load_text, load_text_rect)
        
        # Информация о текущем звуке
        if loaded_sound:
            sound_info = small_font.render(f"Текущий: {current_sound_name}", True, (200, 200, 100))
        else:
            sound_info = small_font.render("Текущий: Базовый звук", True, (200, 200, 100))
        screen.blit(sound_info, (WIDTH//2 - sound_info.get_width()//2, 250))
        
        # Статус воспроизведения
        if is_playing:
            status_text = small_font.render("Статус: Воспроизведение", True, (100, 255, 100))
        elif is_paused:
            status_text = small_font.render("Статус: Пауза", True, (255, 200, 100))
        else:
            status_text = small_font.render("Статус: Остановлено", True, (255, 100, 100))
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, 280))
        
        # Инструкция
        info_text = small_font.render("Управление воспроизведением", True, (220, 220, 220))
        screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 50))
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение
pygame.quit()
sys.exit()