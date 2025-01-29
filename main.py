import tkinter as tk

class КонвертерЧисел:
    def __init__(self, master):
        self.master = master
        master.title("Конвертер Чисел")

        # Создаем фреймы для ввода и вывода
        self.input_frame = tk.Frame(master)
        self.input_frame.pack()
        self.output_frame = tk.Frame(master)
        self.output_frame.pack()

        # Создаем поля ввода и метки
        self.десятичная_метка = tk.Label(self.input_frame, text="Десятичное:")
        self.десятичная_метка.pack(side=tk.LEFT)
        self.десятичное_поле = tk.Entry(self.input_frame)
        self.десятичное_поле.pack(side=tk.LEFT)

        self.двоичная_метка = tk.Label(self.input_frame, text="Двоичное:")
        self.двоичная_метка.pack(side=tk.LEFT)
        self.двоичное_поле = tk.Entry(self.input_frame)
        self.двоичное_поле.pack(side=tk.LEFT)

        self.шестнадцатеричная_метка = tk.Label(self.input_frame, text="Шестнадцатеричное:")
        self.шестнадцатеричная_метка.pack(side=tk.LEFT)
        self.шестнадцатеричное_поле = tk.Entry(self.input_frame)
        self.шестнадцатеричное_поле.pack(side=tk.LEFT)

        # Создаем кнопку конверсии
        self.конверсия_кнопка = tk.Button(self.input_frame, text="Конвертировать", command=self.конвертировать)
        self.конверсия_кнопка.pack(side=tk.LEFT)

        # Создаем кнопку очистки
        self.очистка_кнопка = tk.Button(self.input_frame, text="Очистить", command=self.очистить)
        self.очистка_кнопка.pack(side=tk.LEFT)

        # Создаем метки вывода
        self.вывод_метка = tk.Label(self.output_frame, text="Результат:")
        self.вывод_метка.pack(side=tk.TOP)

        self.вывод_поле = tk.Text(self.output_frame, height=10, width=40)
        self.вывод_поле.pack(side=tk.TOP)

    def конвертировать(self):
        # Получаем значения ввода
        десятичное = self.десятичное_поле.get()
        двоичное = self.двоичное_поле.get()
        шестнадцатеричное = self.шестнадцатеричное_поле.get()

        # Выполняем конверсии
        if десятичное:
            двоичное = bin(int(десятичное)).replace("0b", "")
            шестнадцатеричное = hex(int(десятичное)).replace("0x", "")
        elif двоичное:
            десятичное = str(int(двоичное, 2))
            шестнадцатеричное = hex(int(двоичное, 2)).replace("0x", "")
        elif шестнадцатеричное:
            десятичное = str(int(шестнадцатеричное, 16))
            двоичное = bin(int(шестнадцатеричное, 16)).replace("0b", "")

        # Обновляем поле вывода
        self.вывод_поле.delete(1.0, tk.END)
        self.вывод_поле.insert(tk.END, "Десятичное: " + десятичное + "\n")
        self.вывод_поле.insert(tk.END, "Двоичное: " + двоичное + "\n")
        self.вывод_поле.insert(tk.END, "Шестнадцатеричное: " + шестнадцатеричное)

    def очистить(self):
        # Очищаем поля ввода и вывода
        self.десятичное_поле.delete(0, tk.END)
        self.двоичное_поле.delete(0, tk.END)
        self.шестнадцатеричное_поле.delete(0, tk.END)
        self.вывод_поле.delete(1.0, tk.END)

root = tk.Tk()
my_gui = КонвертерЧисел(root)
root.mainloop()