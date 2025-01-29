import logic
import graphic
import words

def start_game():
    word = words.get_random_word()
    attempts = 6
    guessed_letters = []
    while attempts > 0:
        graphic.display_word(word, guessed_letters)
        letter = input("Guess a letter: ")
        if logic.is_valid_guess(letter, word, guessed_letters):
            guessed_letters.append(letter)
            if logic.has_won(word, guessed_letters):
                graphic.display_win(word)
                break
        else:
            attempts -= 1
            graphic.display_attempts(attempts)
    if attempts == 0:
        graphic.display_loss(word)

def play_again():
    response = input("Play again? (y/n): ")
    if response.lower() == "y":
        start_game()
    else:
        print("Goodbye!")