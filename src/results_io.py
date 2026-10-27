"""Збереження результатів експериментів у CSV."""
# csv - стандартна бібліотека для роботи з таблицями у форматі CSV
import csv
import os


def write_csv(path, rows, fieldnames):
    """Записує список словників у CSV-файл; папка створюється за потреби."""
    folder = os.path.dirname(path)  # папка, у якій лежатиме файл
    if folder:  # порожній рядок означає поточну папку, її створювати не треба
        os.makedirs(folder, exist_ok=True)  # створюємо папку, якщо її ще немає
    # newline="" потрібен, щоб у CSV не з'являлися зайві порожні рядки
    with open(path, "w", newline="", encoding="utf-8") as file:
        # DictWriter записує словники у стовпці з назвами fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # перший рядок таблиці: назви стовпців
        for row in rows:
            writer.writerow(row)  # кожен словник стає рядком таблиці
