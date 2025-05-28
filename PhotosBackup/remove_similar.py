import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image

try:
    import imagehash
except ImportError:
    print("Библиотека 'imagehash' не установлена. Установите её командой 'pip install ImageHash'.")
    imagehash = None

# Удаляем импорт cv2, так как он не используется и может вызывать ошибки, если библиотека не установлена
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

def get_file_hash(file_path, chunk_size=1024 * 1024):
    """
    Получает MD5-хэш файла для проверки на дубликат.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_image_metadata(file_path):
    """
    Получает метаданные изображения (размеры, данные EXIF и хэш изображения).
    """
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif() if hasattr(img, '_getexif') else None
            width, height = img.size
            perceptual_hash = str(imagehash.average_hash(img)) if imagehash else None
            metadata = {
                'width': width,
                'height': height,
                'exif': exif_data if exif_data else {},
                'perceptual_hash': perceptual_hash  # Строковое представление хэша изображения
            }
            return metadata
    except Exception as e:
        print(f"Ошибка чтения метаданных для {file_path}: {e}")
        return None

def get_video_metadata(file_path):
    """
    Получает метаданные видео (размеры, длительность, кодек).
    """
    try:
        parser = createParser(file_path)
        if not parser:
            return None
        metadata = extractMetadata(parser)
        if metadata:
            width = metadata.get("width")
            height = metadata.get("height")
            duration = metadata.get("duration").seconds if metadata.has("duration") else 0
            return {
                'width': width if width else 0,
                'height': height if height else 0,
                'duration': duration
            }
        return None
    except Exception as e:
        print(f"Ошибка чтения метаданных видео для {file_path}: {e}")
        return None

def compare_images_by_hash(file1, file2):
    """
    Сравнивает два изображения по их перцептивному хэшу для определения схожести.
    """
    if not imagehash:
        print("Сравнение хэшей отключено, так как библиотека 'imagehash' не установлена.")
        return False

    metadata1 = get_image_metadata(file1)
    metadata2 = get_image_metadata(file2)

    if metadata1 and metadata2 and metadata1['perceptual_hash'] and metadata2['perceptual_hash']:
        hash1 = metadata1['perceptual_hash']
        hash2 = metadata2['perceptual_hash']
        difference = abs(int(hash1, 16) - int(hash2, 16))
        return difference < 5  # Порог схожести: чем меньше, тем больше вероятность, что изображения одинаковые.
    return False

def compare_files(file1, file2):
    """
    Сравнивает два файла по метаданным и хэшу: оставляет файл с наибольшим разрешением и количеством метаданных.
    """
    if file1.lower().endswith(('jpg', 'jpeg', 'png', 'heic')) and file2.lower().endswith(('jpg', 'jpeg', 'png', 'heic')):
        if compare_images_by_hash(file1, file2):
            return get_best_image(file1, file2)

    metadata1 = get_image_metadata(file1) if file1.lower().endswith(('jpg', 'jpeg', 'png', 'heic')) else get_video_metadata(file1)
    metadata2 = get_image_metadata(file2) if file2.lower().endswith(('jpg', 'jpeg', 'png', 'heic')) else get_video_metadata(file2)

    if not metadata1 or not metadata2:
        return file1 if os.path.getsize(file1) >= os.path.getsize(file2) else file2

    resolution1 = metadata1['width'] * metadata1['height'] if metadata1['width'] and metadata1['height'] else 0
    resolution2 = metadata2['width'] * metadata2['height'] if metadata2['width'] and metadata2['height'] else 0

    metadata_count1 = len(metadata1['exif']) if 'exif' in metadata1 else len(metadata1)
    metadata_count2 = len(metadata2['exif']) if 'exif' in metadata2 else len(metadata2)

    if resolution1 > resolution2:
        return file1
    elif resolution1 < resolution2:
        return file2

    return file1 if metadata_count1 >= metadata_count2 else file2

def get_best_image(file1, file2):
    """
    Выбирает лучшее изображение по разрешению и количеству метаданных.
    """
    metadata1 = get_image_metadata(file1)
    metadata2 = get_image_metadata(file2)

    if not metadata1 or not metadata2:
        return file1 if os.path.getsize(file1) >= os.path.getsize(file2) else file2

    resolution1 = metadata1['width'] * metadata1['height']
    resolution2 = metadata2['width'] * metadata2['height']

    if resolution1 > resolution2:
        return file1
    elif resolution1 < resolution2:
        return file2

    return file1 if len(metadata1['exif']) >= len(metadata2['exif']) else file2

def copy_for_testing(group_number, file_to_keep, file_to_delete):
    """
    Копирует файлы для тестирования вместо удаления.
    """
    base_dir = f"/Volumes/G-DRIVE/{group_number}"
    keep_dir = os.path.join(base_dir, "оставляемый файл")
    delete_dir = os.path.join(base_dir, "удаляемые файлы")

    os.makedirs(keep_dir, exist_ok=True)
    os.makedirs(delete_dir, exist_ok=True)

    shutil.copy2(file_to_keep, os.path.join(keep_dir, os.path.basename(file_to_keep)))
    shutil.copy2(file_to_delete, os.path.join(delete_dir, os.path.basename(file_to_delete)))

def remove_newer_duplicates(photo_dir):
    """
    Находит и копирует потенциальные дубликаты фото и видео для тестирования.
    """
    hashes = {}  # ключ - хэш, значение - список путей файлов
    total_files = sum(len(files) for _, _, files in os.walk(photo_dir))
    processed_files = 0
    duplicate_groups = 0

    supported_extensions = (
        'jpg', 'jpeg', 'png', 'heic'  # фото
    #    'mp4', 'mov', 'avi', 'mkv', 'wmv', 'm4v'  # видео
    )

    for root, _, files in os.walk(photo_dir):
        for file in files:
            if file.lower().endswith(supported_extensions):
                file_path = os.path.join(root, file)
                print(f"Анализ файла: {file_path}")
                file_hash = get_file_hash(file_path)

                if file_hash in hashes:
                    existing_file_path = hashes[file_hash]
                    file_to_keep = compare_files(existing_file_path, file_path)
                    file_to_delete = file_path if file_to_keep == existing_file_path else existing_file_path

                    duplicate_groups += 1
                    copy_for_testing(duplicate_groups, file_to_keep, file_to_delete)

                    print(f"Группа дубликатов {duplicate_groups}: оставляем {file_to_keep}, копируем дубликат {file_to_delete}")
                    hashes[file_hash] = file_to_keep
                else:
                    hashes[file_hash] = file_path

                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"Прогресс обработки: {progress:.2f}% | Групп дубликатов: {duplicate_groups}")

    print("Обработка завершена.")
    print(f"Всего групп дубликатов: {duplicate_groups}")

if __name__ == "__main__":
    photo_library_path = "/Volumes/G-DRIVE/Photos Library.photoslibrary/originals"  # Попробуем использовать путь к "originals" вместо "Masters"

    if not os.path.exists(photo_library_path):
        print("Указанная директория не существует. Убедитесь, что диск подключен и правильный путь.")
    else:
        remove_newer_duplicates(photo_library_path)

# Подсказка: чтобы уточнить структуру библиотеки, можно временно добавить print(os.listdir(photo_library_path))
