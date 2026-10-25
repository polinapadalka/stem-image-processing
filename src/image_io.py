"""Читання, підготовка та збереження зображень."""
# os потрібен для роботи з файлами й папками
import os

# Image - клас бібліотеки Pillow: відкриває, змінює й зберігає зображення
from PIL import Image

# розширення файлів, які програма вважає зображеннями
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")


def load_image(path):
    """Відкриває зображення в режимі RGB; повертає None, якщо файл не вдалося прочитати."""
    # try/except потрібен, щоб програма не падала на порожніх і пошкоджених файлах
    try:
        image = Image.open(path)  # відкриваємо файл
        image.load()  # читаємо файл повністю, щоб одразу виявити пошкодження
        return image.convert("RGB")  # робимо зображення трьохканальним: R, G, B
    except (OSError, ValueError):
        return None  # файл не відкрився: замість аварії повертаємо None


def square_resize(image, size):
    """Вирізає квадрат із центру зображення й зменшує його до size x size пікселів."""
    width, height = image.size  # ширина і висота зображення
    side = min(width, height)  # сторона квадрата дорівнює меншій зі сторін
    left = (width - side) // 2  # відступ зліва, щоб квадрат був по центру
    top = (height - side) // 2  # відступ зверху за тим самим принципом
    # crop вирізає область: (ліва межа, верхня, права, нижня)
    cropped = image.crop((left, top, left + side, top + side))
    return cropped.resize((size, size))  # зменшуємо квадрат до потрібного розміру


def list_images(folder):
    """Повертає відсортований список шляхів до зображень у папці."""
    # якщо папки немає, повертаємо порожній список замість помилки
    if not os.path.isdir(folder):
        return []
    paths = []  # сюди збираємо шляхи до зображень
    # sorted робить порядок файлів завжди однаковим
    for name in sorted(os.listdir(folder)):
        # беремо лише файли з потрібним розширенням (великі й малі літери однакові)
        if name.lower().endswith(SUPPORTED_EXTENSIONS):
            paths.append(os.path.join(folder, name))  # склеюємо папку й назву файлу
    return paths


def save_image(image, path):
    """Зберігає зображення; якщо папки немає, створює її."""
    folder = os.path.dirname(path)  # папка, у яку треба зберегти файл
    if folder:  # порожній рядок означає поточну папку, її створювати не треба
        os.makedirs(folder, exist_ok=True)  # exist_ok=True: не помилка, якщо папка вже є
    image.save(path)  # формат визначається за розширенням файлу