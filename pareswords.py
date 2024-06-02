import re
import argparse
import os
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import nltk
from nltk.corpus import stopwords

# Загрузим список стоп-слов
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def text_to_columns(text):
    # Приводим текст к нижнему регистру для учета регистра
    text = text.lower()
    
    # Разделяем текст на слова, удаляя знаки препинания
    words = re.findall(r'\b\w+\b', text)
    
    # Исключаем стоп-слова
    words = [word for word in words if word not in stop_words]
    
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

def translate_word(word, model, tokenizer):
    inputs = tokenizer(word, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return word, translated_text

def translate_words(words, model, tokenizer, max_workers=10):
    translations = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_word = {executor.submit(translate_word, word, model, tokenizer): word for word in words}
        for future in tqdm(as_completed(future_to_word), total=len(words), desc="Translating words"):
            word, translated_text = future.result()
            translations[word] = translated_text
    return translations

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Process a text file and count word occurrences.')
    parser.add_argument('filename', type=str, help='The path to the text file to process')
    parser.add_argument('--threads', type=int, default=4, help='The number of threads to use for translation')
    
    args = parser.parse_args()
    
    # Читаем текст из файла
    with open(args.filename, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Обрабатываем текст и получаем результат и количество уникальных слов
    result, unique_word_count = text_to_columns(text)
    
    # Загружаем модель и токенизатор для перевода
    model_name = 'Helsinki-NLP/opus-mt-en-ru'
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    
    # Получаем список уникальных слов для перевода
    unique_words = [word for word, count in result]
    
    # Переводим слова
    translations = translate_words(unique_words, model, tokenizer, max_workers=args.threads)
    
    # Формируем имя выходного файла
    base_filename = os.path.splitext(args.filename)[0]
    output_filename = f"{base_filename}_output.txt"
    
    # Записываем результат в выходной файл
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(f"{'Слово':20} {'Кол-во вхождений':20} {'Перевод'}\n")
        output_file.write("-" * 60 + "\n")
        for word, count in tqdm(result, desc="Writing to file"):
            output_file.write(f"{word:20} {count:20} {translations[word]}\n")
    
    # Выводим количество уникальных слов
    print(f"Результат сохранен в файл: {output_filename}")
    print(f"Количество уникальных слов: {unique_word_count}")

if __name__ == "__main__":
    main()
