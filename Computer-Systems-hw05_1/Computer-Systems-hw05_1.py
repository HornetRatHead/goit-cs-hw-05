import subprocess
import sys
import os
from pathlib import Path

import logging

import asyncio
from aiofiles import os as aio_os
from aiofiles import open as aio_open

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_virtualenv(venv_name: str) -> None:
    if not os.path.exists(venv_name):
        subprocess.check_call([sys.executable, '-m', 'venv', venv_name])
        logger.info(f"Створено віртуальне середовище: {venv_name}")
    else:
        logger.info(f"Віртуальне середовище '{venv_name}' вже існує.")

def install_requirements(venv_name: str) -> None:
    pip_path = os.path.join(venv_name, 'Scripts', 'pip') if os.name == 'nt' else os.path.join(venv_name, 'bin', 'pip')
    requirements = ['aiofiles', 'argparse', 'logging']
    for package in requirements:
        subprocess.check_call([pip_path, 'install', package])
        logger.info(f"Встановлено: {package}")

async def copy_file(file_path: Path, dest_folder: Path) -> None:
    try:
        file_ext = file_path.suffix.lstrip('.')
        dest_dir = dest_folder / file_ext
        await aio_os.makedirs(dest_dir, exist_ok=True)

        dest_path = dest_dir / file_path.name
        async with aio_open(file_path, 'rb') as f_src, aio_open(dest_path, 'wb') as f_dest:
            while True:
                chunk = await f_src.read(512)
                if not chunk:
                    break
                await f_dest.write(chunk)

        logger.info(f'Копіювання {file_path} до {dest_path}')
    except Exception as e:
        logger.error(f'Помилка під час копіювання файлу {file_path}: {e}')

async def read_folder(source_folder: Path, dest_folder: Path) -> None:
    try:
        for root, _, files in await asyncio.to_thread(os.walk, source_folder):
            for file_name in files:
                file_path = Path(root) / file_name
                await copy_file(file_path, dest_folder)
    except Exception as e:
        logger.error(f'Помилка під час читання теки {source_folder}: {e}')

async def main(source_folder: Path, dest_folder: Path) -> None:
    await read_folder(source_folder, dest_folder)

def get_folder_path(prompt: str, default: str) -> str:
    path = input(f"{prompt} (за замовчуванням '{default}'): ").strip()
    return path if path else default

if __name__ == "__main__":
    venv_name = "myenv"
    create_virtualenv(venv_name)
    install_requirements(venv_name)

    source_folder = get_folder_path("Введіть шлях до вихідної теки для обробки файлів", "")
    if not source_folder:
        logger.error("Помилка: Вихідна тека не введена. Завершення роботи.")
        exit(1)

    dest_folder = get_folder_path("Введіть шлях до цільової теки для збереження", str(Path.cwd() / "Sorted_files"))
    asyncio.run(main(Path(source_folder), Path(dest_folder)))
