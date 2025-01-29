import tkinter as tk
from random import choice
import sys
from words import get_random_word

class Game:
    def __init__(self, root):
        self.root = root
        self.category = None
        self.word = None
        self.attempts = 6
        self.guessed_letters = []
        self.language = "Русский"
        self.start_menu()

    def start_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True)
        self.title_label = tk.Label(self.main_frame, text="Виселица" if self.language == "Русский" else "Hangman", font=("Helvetica", 36), bg="#f0f0f0")
        self.title_label.pack(pady=20)
        self.category_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.category_frame.pack()
        self.animals_button = tk.Button(self.category_frame, text="Животные" if self.language == "Русский" else "Animals", font=("Helvetica", 18), command=lambda category="animals": self.start_game(category))
        self.animals_button.pack(side="left", padx=10)
        self.fruits_button = tk.Button(self.category_frame, text="Фрукты" if self.language == "Русский" else "Fruits", font=("Helvetica", 18), command=lambda category="fruits": self.start_game(category))
        self.fruits_button.pack(side="left", padx=10)
        self.cities_button = tk.Button(self.category_frame, text="Города" if self.language == "Русский" else "Cities", font=("Helvetica", 18), command=lambda category="cities": self.start_game(category))
        self.cities_button.pack(side="left", padx=10)
        self.multiplayer_button = tk.Button(self.main_frame, text="Мультиплеер" if self.language == "Русский" else "Multiplayer", font=("Helvetica", 18), command=self.start_multiplayer)
        self.multiplayer_button.pack(pady=20)
        self.settings_button = tk.Button(self.main_frame, text="Настройки" if self.language == "Русский" else "Settings", font=("Helvetica", 18), command=self.start_settings)
        self.settings_button.pack(pady=10)
        self.exit_button = tk.Button(self.main_frame, text="Выход" if self.language == "Русский" else "Exit", font=("Helvetica", 18), command=self.root.quit)
        self.exit_button.pack(pady=10)

    def start_game(self, category):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.category = category
        self.word = get_random_word(category, self.language)
        self.attempts = 6
        self.guessed_letters = []
        self.game_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.game_frame.pack(fill="both", expand=True)
        self.word_label = tk.Label(self.game_frame, text="", font=("Helvetica", 24), bg="#f0f0f0")
        self.word_label.pack(pady=20)
        self.attempts_label = tk.Label(self.game_frame, text="Осталось попыток: 6" if self.language == "Русский" else "Attempts left: 6", font=("Helvetica", 18), bg="#f0f0f0")
        self.attempts_label.pack()
        self.canvas = tk.Canvas(self.game_frame, width=200, height=200, bg="#f0f0f0")
        self.canvas.pack()
        self.guess_entry = tk.Entry(self.game_frame, width=20, font=("Helvetica", 18))
        self.guess_entry.pack()
        self.guess_button = tk.Button(self.game_frame, text="Угадать" if self.language == "Русский" else "Guess", font=("Helvetica", 18), command=self.guess_letter)
        self.guess_button.pack()
        self.message_label = tk.Label(self.game_frame, text="", font=("Helvetica", 18), bg="#f0f0f0")
        self.message_label.pack()
        self.display_word(self.word, self.guessed_letters)

    def start_multiplayer(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.multiplayer_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.multiplayer_frame.pack(fill="both", expand=True)
        self.word_label = tk.Label(self.multiplayer_frame, text="Игрок 1, введите слово:" if self.language == "Русский" else "Player 1, enter a word:", font=("Helvetica", 24), bg="#f0f0f0")
        self.word_label.pack(pady=20)
        self.guess_entry = tk.Entry(self.multiplayer_frame, width=20, font=("Helvetica", 18))
        self.guess_entry.pack()
        self.guess_button = tk.Button(self.multiplayer_frame, text="Угадать" if self.language == "Русский" else "Guess", font=("Helvetica", 18), command=self.guess_letter_multiplayer)
        self.guess_button.pack()

    def start_settings(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.settings_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.settings_frame.pack(fill="both", expand=True)
        self.language_label = tk.Label(self.settings_frame, text="Язык:" if self.language == "Русский" else "Language:", font=("Helvetica", 18), bg="#f0f0f0")
        self.language_label.pack()
        self.russian_button = tk.Button(self.settings_frame, text="Русский" if self.language == "Русский" else "Russian", font=("Helvetica", 18), command=lambda language="Русский": self.set_language(language))
        self.russian_button.pack(side="left", padx=10)
        self.english_button = tk.Button(self.settings_frame, text="Английский" if self.language == "Русский" else "English", font=("Helvetica", 18), command=lambda language="English": self.set_language(language))
        self.english_button.pack(side="left", padx=10)
        self.back_button = tk.Button(self.settings_frame, text="Назад" if self.language == "Русский" else "Back", font=("Helvetica", 18), command=self.start_menu)
        self.back_button.pack(pady=20)

    def set_language(self, language):
        self.language = language
        self.start_menu()

    def guess_letter(self):
        letter = self.guess_entry.get()
        self.guess_entry.delete(0, tk.END)
        if letter in self.word and letter not in self.guessed_letters:
            self.guessed_letters.append(letter)
            self.display_word(self.word, self.guessed_letters)
            if all(letter in self.guessed_letters for letter in self.word):
                self.display_win(self.word)
        elif letter in self.guessed_letters:
            self.message_label.config(text="Буква уже угадана!")
        else:
            self.attempts -= 1
            self.display_attempts(self.attempts)
            if self.attempts == 0:
                self.display_loss(self.word)

    def guess_letter_multiplayer(self):
        letter = self.guess_entry.get()
        self.guess_entry.delete(0, tk.END)
        # multiplayer logic here

    def display_word(self, word, guessed_letters):
        display = ""
        for letter in word:
            if letter in guessed_letters:
                display += letter + " "
            else:
                display += "_ "
        self.word_label.config(text=display)

    def display_attempts(self, attempts):
        self.attempts_label.config(text=f"Осталось попыток: {attempts}" if self.language == "Русский" else f"Attempts left: {attempts}")

    def display_win(self, word):
        self.word_label.config(text=f"Победа! Слово было {word}." if self.language == "Русский" else f"Win! The word was {word}.")
        self.guess_button.config(state="disabled")

    def display_loss(self, word):
        self.word_label.config(text=f"Игра окончена! Слово было {word}." if self.language == "Русский" else f"Game over! The word was {word}.")
        self.guess_button.config(state="disabled")

class Graphic:
    def __init__(self, game):
        self.game = game
        self.root = game.root
        self.word_label = None
        self.attempts_label = None
        self.canvas = None
        self.guess_entry = None
        self.guess_button = None
        self.play_again_button = None

    def display_word(self, word, guessed_letters):
        display = ""
        for letter in word:
            if letter in guessed_letters:
                display += letter + " "
            else:
                display += "_ "
        self.word_label.config(text=display)

    def display_attempts(self, attempts):
        self.attempts_label.config(text=f"У вас осталось {attempts} попыток.")
        self.draw_hangman(attempts)

    def display_win(self, word):
        self.word_label.config(text=f"Победа! Слово было {word}.")
        self.guess_button.config(state="disabled")

    def display_loss(self, word ):
        self.word_label.config(text=f"Игра окончена! Слово было {word}.")
        self.guess_button.config(state="disabled")

    def guess_letter(self):
        letter = self.guess_entry.get()
        self.guess_entry.delete(0, tk.END)
        self.game.guess_letter(letter)

    def draw_hangman(self, attempts):
        self.canvas.delete("all")
        if attempts <= 6:
            self.canvas.create_line(50, 150, 150, 150)  # основа
        if attempts <= 5:
            self.canvas.create_line(100, 150, 100, 50)  # столб
        if attempts <= 4:
            self.canvas.create_line(100, 50, 150, 50)  # перекладина
        if attempts <= 3:
            self.canvas.create_line(150, 50, 150, 70)  # веревка
        if attempts <= 2:
            self.canvas.create_oval(140, 70, 160, 90)  # голова
        if attempts <= 1:
            self.canvas.create_line(150, 90, 150, 120)  # туловище
        if attempts == 0:
            self.canvas.create_line(150, 100, 130, 110)  # левая рука
            self.canvas.create_line(150, 100, 170, 110)  # правая рука
            self.canvas.create_line(150, 120, 130, 130)  # левая нога
            self.canvas.create_line(150, 120, 170, 130)  # правая нога