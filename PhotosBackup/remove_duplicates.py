import os
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(file_path, chunk_size=1024 * 1024):
    """
    Получает MD5-хэш файла для проверки на дубликат.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_newer_duplicates(photo_dir):
    """
    Находит и удаляет дубликаты фото и видео файлов в заданной директории по мере их обнаружения.
    """
    hashes = {}  # ключ - хэш, значение - путь файла и время создания
    total_files = sum(len(files) for _, _, files in os.walk(photo_dir))
    processed_files = 0
    deleted_files = 0

    supported_extensions = (
    #    'jpg', 'jpeg', 'png', 'heic',  # фото
        'mp4', 'mov', 'avi', 'mkv', 'wmv', 'm4v'  # видео
    )

    for root, _, files in os.walk(photo_dir):
        for file in files:
            if file.lower().endswith(supported_extensions):
                file_path = os.path.join(root, file)
                print(f"Анализ файла: {file_path}")
                file_hash = get_file_hash(file_path)
                creation_time = os.path.getctime(file_path)

                if file_hash in hashes:
                    # Найден дубликат, удаляем более новый файл
                    existing_file_path, existing_creation_time = hashes[file_hash]
                    if creation_time < existing_creation_time:
                        print(f"Удален дубликат: {existing_file_path}, оставлен: {file_path}")
                        os.remove(existing_file_path)
                        hashes[file_hash] = (file_path, creation_time)
                    else:
                        print(f"Удален дубликат: {file_path}, оставлен: {existing_file_path}")
                        os.remove(file_path)
                    deleted_files += 1
                else:
                    hashes[file_hash] = (file_path, creation_time)

                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"Прогресс обработки: {progress:.2f}% | Удалено дубликатов: {deleted_files}")

    print("Удаление завершено.")
    print(f"Всего удалено файлов: {deleted_files}")

if __name__ == "__main__":
    photo_library_path = "/Volumes/G-DRIVE/Photos Library.photoslibrary/originals"  # Попробуем использовать путь к "originals" вместо "Masters"

    if not os.path.exists(photo_library_path):
        print("Указанная директория не существует. Убедитесь, что диск подключен и правильный путь.")
    else:
        remove_newer_duplicates(photo_library_path)

# Подсказка: чтобы уточнить структуру библиотеки, можно временно добавить print(os.listdir(photo_library_path))
