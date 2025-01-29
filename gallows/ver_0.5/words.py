import random

# Словарь с задаваемыми словами
words = {
    "animals": {
        "Русский": ["кот", "собака", "птица", "рыба", "слон"],
        "English": ["cat", "dog", "bird", "fish", "elephant"]
    },
    "fruits": {
        "Русский": ["яблоко", "банан", "апельсин", "виноград", "манго"],
        "English": ["apple", "banana", "orange", "grape", "mango"]
    },
    "cities": {
        "Русский": ["москва", "лондон", "париж", "берлин", "рим"],
        "English": ["moscow", "london", "paris", "berlin", "rome"]
    }
}

def get_random_word(category, language):
    """
    Возвращает случайное слово из заданной категории.
    
    :param category: Категория слов (animals, fruits, cities)
    :param language: Язык (Русский, English)
    :return: Случайное слово из категории
    """
    return random.choice(words[category][language])