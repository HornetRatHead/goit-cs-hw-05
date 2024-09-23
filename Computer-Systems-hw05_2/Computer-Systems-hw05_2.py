import requests
import matplotlib.pyplot as plt
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import os
from pathlib import Path

def create_virtualenv(venv_name):
    if not os.path.exists(venv_name):
        subprocess.check_call([sys.executable, '-m', 'venv', venv_name])
        print(f"Створено віртуальне середовище: {venv_name}")

def install_requirements(venv_name):
    pip_path = os.path.join(venv_name, 'Scripts', 'pip') if os.name == 'nt' else os.path.join(venv_name, 'bin', 'pip')
    requirements = ['requests', 'matplotlib']  # Додайте свої бібліотеки
    for package in requirements:
        subprocess.check_call([pip_path, 'install', package])
        print(f"Встановлено: {package}")

def map_function(word):
    return word.lower(), 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

def map_reduce(text):
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))
        
    return dict(reduced_values)

def visualize_top_words(word_freq, top_n=10):
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)

    plt.bar(words, counts)
    plt.xlabel('Слова')
    plt.ylabel('Частота')
    plt.title('Топ слів')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    venv_name = "myenv"  # Назва віртуального середовища
    create_virtualenv(venv_name)
    install_requirements(venv_name)

    url = input("Введіть URL для завантаження тексту: ").strip()
    response = requests.get(url)
    if response.status_code == 200:
        text = response.text
        word_freq = map_reduce(text)
        visualize_top_words(word_freq)
    else:
        print(f"Не вдалося завантажити текст. Код статусу: {response.status_code}")
