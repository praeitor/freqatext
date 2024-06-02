import re
import argparse
import os
from translate import Translator

def text_to_columns(text):
    # Приводим текст к нижнему регистру для учета регистра
    text = text.lower()
    
    # Разделяем текст на слова, удаляя знаки препинания
    words = re.findall(r'\b\w+\b', text)
    
    # Подсчитываем количество вхождений каждого слова
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    
    # Преобразуем в список кортежей и сортируем по количеству вхождений от большего к меньшему,
    # и по алфавиту при одинаковом количестве вхождений
    word_count_list = sorted(word_count.items(), key=lambda item: (-item[1], item[0]))
    
    # Возвращаем результат и количество уникальных слов
    return word_count_list, len(word_count)

def translate_words(words):
    translator = Translator(to_lang="ru")
    translations = {}
    for word in words:
        translated = translator.translate(word)
        translations[word] = translated
    return translations

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Process a text file and count word occurrences.')
    parser.add_argument('filename', type=str, help='The path to the text file to process')
    
    args = parser.parse_args()
    
    # Читаем текст из файла
    with open(args.filename, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Обрабатываем текст и получаем результат и количество уникальных слов
    result, unique_word_count = text_to_columns(text)
    
    # Получаем список уникальных слов для перевода
    unique_words = [word for word, count in result]
    
    # Переводим слова
    translations = translate_words(unique_words)
    
    # Формируем имя выходного файла
    base_filename = os.path.splitext(args.filename)[0]
    output_filename = f"{base_filename}_output.txt"
    
    # Записываем результат в выходной файл
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(f"{'Слово':20} {'Кол-во вхождений':20} {'Перевод'}\n")
        output_file.write("-" * 60 + "\n")
        for word, count in result:
            output_file.write(f"{word:20} {count:20} {translations[word]}\n")
    
    # Выводим количество уникальных слов
    print(f"Результат сохранен в файл: {output_filename}")
    print(f"Количество уникальных слов: {unique_word_count}")

if __name__ == "__main__":
    main()
