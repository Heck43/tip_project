import tkinter as tk
from game import Game
import sys

def main():
    root = tk.Tk()
    root.title("Виселица" if True else "Hangman")
    game = Game(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (root.quit(), root.destroy()))
    root.mainloop()
    sys.exit()

if __name__ == "__main__":
    main()