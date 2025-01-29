def display_word(word, guessed_letters):
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter + " "
        else:
            display += "_ "
    print(display)

def display_attempts(attempts):
    print(f"You have {attempts} attempts left.")

def display_win(word):
    print(f"Congratulations! You won! The word was {word}.")

def display_loss(word):
    print(f"Game over! The word was {word}.")