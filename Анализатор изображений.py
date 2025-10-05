import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime

class ImageInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор изображений")
        self.root.geometry("600x700")
        
        # Основные элементы интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Анализатор изображений", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Кнопка загрузки
        self.load_button = tk.Button(self.root, text="Загрузить изображение", 
                                   command=self.load_image,
                                   font=("Arial", 12),
                                   bg="#4CAF50", fg="white",
                                   padx=20, pady=10)
        self.load_button.pack(pady=10)
        
        # Область для отображения изображения
        self.image_frame = tk.Frame(self.root, bg="white", relief="sunken", bd=2)
        self.image_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.image_label = tk.Label(self.image_frame, text="Изображение не загружено", 
                                   bg="white", fg="gray")
        self.image_label.pack(expand=True)
        
        # Область для информации
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.info_text = tk.Text(self.info_frame, height=15, width=70, 
                                font=("Courier New", 10),
                                relief="sunken", bd=2)
        self.info_text.pack(fill="both", expand=True)
        
        # Добавляем скроллбар для текстового поля
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
    def load_image(self):
        # Открываем диалог выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Открываем изображение с помощью PIL
                with Image.open(file_path) as img:
                    self.display_image_info(img, file_path)
                    self.display_image_preview(img)
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def display_image_preview(self, img):
        # Создаем превью изображения
        preview_size = (300, 200)
        img_copy = img.copy()
        img_copy.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        # Конвертируем для tkinter
        photo = ImageTk.PhotoImage(img_copy)
        
        # Обновляем метку с изображением
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo  # Сохраняем ссылку
    
    def display_image_info(self, img, file_path):
        # Собираем информацию об изображении
        info = self.get_image_info(img, file_path)
        
        # Очищаем текстовое поле и выводим информацию
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def get_image_info(self, img, file_path):
        # Основная информация о файле
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].upper()
        file_size = os.path.getsize(file_path)
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Информация об изображении
        width, height = img.size
        mode = img.mode
        format_info = img.format
        
        # Соотношение сторон
        aspect_ratio = width / height
        
        # Разрешение (DPI)
        if 'dpi' in img.info:
            dpi = img.info['dpi']
        else:
            dpi = "Не указано"
        
        # Цветовой режим
        color_modes = {
            '1': '1-битный (чёрно-белый)',
            'L': '8-битный (оттенки серого)',
            'P': '8-битный (палитра)',
            'RGB': '24-битный (True Color)',
            'RGBA': '32-битный (True Color + Alpha)',
            'CMYK': '32-битный (CMYK)',
            'YCbCr': '24-битный (Цветовое пространство YCbCr)',
            'LAB': '24-битный (Цветовое пространство Lab)',
            'HSV': '24-битный (Цветовое пространство HSV)'
        }
        
        color_mode = color_modes.get(mode, mode)
        
        # Дополнительная информация
        info_lines = [
            "=== ОСНОВНАЯ ИНФОРМАЦИЯ ===",
            f"Название файла: {file_name}",
            f"Расширение: {file_extension}",
            f"Размер файла: {self.format_file_size(file_size)}",
            f"Дата изменения: {file_mod_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=== ХАРАКТЕРИСТИКИ ИЗОБРАЖЕНИЯ ===",
            f"Размер: {width} × {height} пикселей",
            f"Соотношение сторон: {aspect_ratio:.2f}:1 ({width}:{height})",
            f"Общее количество пикселей: {width * height:,}",
            f"Цветовой режим: {color_mode}",
            f"Формат: {format_info if format_info else 'Не определен'}",
            f"Разрешение (DPI): {dpi}",
        ]
        
        # Добавляем информацию о прозрачности
        if hasattr(img, 'has_transparency') and img.has_transparency:
            info_lines.append("Прозрачность: Да")
        elif mode == 'RGBA':
            info_lines.append("Прозрачность: Да (Alpha канал)")
        else:
            info_lines.append("Прозрачность: Нет")
        
        # Дополнительная информация EXIF (если есть)
        try:
            exif_data = img._getexif()
            if exif_data:
                info_lines.extend(["", "=== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ==="])
                
                # Основные теги EXIF
                exif_tags = {
                    271: 'Производитель камеры',
                    272: 'Модель камеры',
                    274: 'Ориентация',
                    306: 'Дата и время съёмки',
                    36867: 'Дата и время оригинала',
                    36868: 'Дата и время оцифровки',
                    37377: 'Выдержка',
                    37378: 'Диафрагма',
                    37379: 'ISO',
                    37380: 'Вспышка',
                    37383: 'Фокусное расстояние',
                }
                
                for tag, description in exif_tags.items():
                    if tag in exif_data:
                        info_lines.append(f"{description}: {exif_data[tag]}")
        except:
            pass
        
        return "\n".join(info_lines)
    
    def format_file_size(self, size_bytes):
        """Форматирует размер файла в читаемом виде"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} ТБ"

def main():
    root = tk.Tk()
    app = ImageInfoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()