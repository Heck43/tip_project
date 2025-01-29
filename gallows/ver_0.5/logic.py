def is_valid_guess(letter, word, guessed_letters):
    if len(letter) != 1:
        return False
    if letter in guessed_letters:
        return False
    if letter not in word:
        return False
    return True

def has_won(word, guessed_letters):
    for letter in word:
        if letter not in guessed_letters:
            return False
    return True