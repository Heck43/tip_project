class Dictionary:
    def __init__(self):
        self.dictionary = {"apple": "яблоко", "banana": "банан", "cherry": "вишня"}

    def get_translation(self, word):
        return self.dictionary.get(word, "Перевод не найден")