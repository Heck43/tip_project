from turtle import *
import time
import random
import winsound
# Создаем экран черепашки
screen = Screen()
screen.title("Turtle with Transparent Background")

# Получаем холст и корневое окно
canvas = screen.getcanvas()
root = canvas.winfo_toplevel()
root.wm_attributes('-transparentcolor', 'black')  # Устанавливаем прозрачный цвет
root.overrideredirect(True)  # Убираем заголовок окна

# Переменные для перетаскивания окна
dragging = False
previous_x = 0
previous_y = 0

# Переменные для изменения размера окна
resizing = False
start_width = 0
start_height = 0
start_x = 0
start_y = 0

def on_mouse_press(event):
    global dragging, previous_x, previous_y, resizing, start_width, start_height, start_x, start_y
    # Проверяем, находится ли курсор в правом нижнем углу для изменения размера
    if event.x >= root.winfo_width() - 10 and event.y >= root.winfo_height() - 10:
        resizing = True
        start_width = root.winfo_width()
        start_height = root.winfo_height()
        start_x = event.x
        start_y = event.y
    else:
        dragging = True
        previous_x = event.x
        previous_y = event.y

def on_mouse_motion(event):
    global dragging, previous_x, previous_y, resizing, start_width, start_height

    if dragging:
        x = root.winfo_x() - previous_x + event.x
        y = root.winfo_y() - previous_y + event.y
        root.geometry(f"+{x}+{y}")

    if resizing:
        new_width = start_width + (event.x - start_x)
        new_height = start_height + (event.y - start_y)
        root.geometry(f"{new_width}x{new_height}")

def on_mouse_release(event):
    global dragging, resizing
    dragging = False
    resizing = False

    # Функция для закрытия программы
def close_program():
    screen.bye()  # Закрывает окно turtle

# Привязываем события мыши к функциям
canvas.bind("<Button-1>", on_mouse_press)
canvas.bind("<B1-Motion>", on_mouse_motion)
canvas.bind("<ButtonRelease-1>", on_mouse_release)

# Привязываем клавишу Esc к функции закрытия
screen.onkey(close_program, "Escape")
screen.listen()  # Начинаем слушать события клавиатуры

bgcolor('black')
pencolor('green')
tracer(0)
hideturtle()

pos = [0,0]
degree = 0
rotation_speed = 0.2
cube = [[[0,0],[0,0],[0,0],[0,0]],[[0,0],[0,0],[0,0],[0,0]]]
cube_length = 100
offset = [round(cube_length/2),10]
motion_vector = random.randint(0,3)
motion_speed = 1
pensize(cube_length/20)
colision_reset = 3
colision_time = 0

def Cube():
    global cube, degree, colision_time
    clear()
    up()
    goto(pos[0],pos[1])
    setheading(degree)
    fd(-cube_length/2)
    lt(90)
    fd(-cube_length/2)
    down()
    for i in range(4):
        cube[0][i][0] = xcor()
        cube[0][i][1] = ycor()
        fd(cube_length)
        rt(90)
    goto(xcor()+offset[0],ycor()+offset[1])
    for i in range(4):
        cube[1][i][0] = xcor()
        cube[1][i][1] = ycor()
        fd(cube_length)
        rt(90)
    for i in range(4):
        up()
        goto(cube[0][i][0],cube[0][i][1])
        down()
        goto(cube[1][i][0],cube[1][i][1])
    PrintStats()
    if colision_time > 0:
        colision_time -= 0.1
    if colision_time <= 0:
        pencolor('green')
    update()
    degree += rotation_speed

def Motion():
    global pos
    if motion_vector == 0: # Вверх - право
        pos[0] += motion_speed
        pos[1] += motion_speed
    if motion_vector == 1: # Вверх - лево
        pos[0] -= motion_speed
        pos[1] += motion_speed
    if motion_vector == 2: # Вниз - право
        pos[0] += motion_speed
        pos[1] -= motion_speed
    if motion_vector == 3: # Вниз - лево
        pos[0] -= motion_speed
        pos[1] -= motion_speed

def Borders():
    global motion_vector, rotation_speed, motion_speed, cube_length, offset, colision_time
    check = CheckBorders()
    check2 = False
    if check == 0: # Верх
        if motion_vector == 0:
            motion_vector = 2
            check2 = True
        elif motion_vector == 1:
            motion_vector = 3
            check2 = True
        else:
            pass
    elif check == 1: # Низ
        if motion_vector == 2:
            motion_vector = 0
            check2 = True
        elif motion_vector == 3:
            motion_vector = 1
            check2 = True
        else:
            pass
    elif check == 2: # Право
        if motion_vector == 0:
            motion_vector = 1
            check2 = True
        elif motion_vector == 2:
            motion_vector = 3
            check2 = True
        else:
            pass
    elif check == 3: # Лево
        if motion_vector == 1:
            motion_vector = 0
            check2 = True
        elif motion_vector == 3:
            motion_vector = 2
            check2 = True
        else:
            pass
    else:
        pass
    if check2 == True:
        rotation_speed = -rotation_speed*1.01
        motion_speed *=1.01
        cube_length *=1.01
        offset[0] = round(cube_length/2)
        pensize(cube_length/20)
        pencolor('white')
        colision_time = colision_reset
    else:
        pass
   
def CheckBorders():
    result = -1
    for s in range(2):
        for i in range(4):
            if cube[s][i][1] >= Screen().window_height()/2:
                result = 0
                return result # Верх
            else:
                pass
    for s in range(2):
        for i in range(4):
            if cube[s][i][1] <= -Screen().window_height()/2:
                result = 1
                return result # Низ
            else:
                pass
    for s in range(2):
        for i in range(4):
            if cube[s][i][0] >= Screen().window_width()/2:
                result = 2
                return result # Право
            else:
                pass
    for s in range(2):
        for i in range(4):
            if cube[s][i][0] <= -Screen().window_width()/2:
                result = 3
                return result # лево
            else:
                pass
    return result

def PrintStats():
    up()
    if motion_vector == 0:
        vector = "x+ y+"
    elif motion_vector == 1:
        vector = "x- y+"
    elif motion_vector == 2:
        vector = "x+ y-"
    elif motion_vector == 3:
        vector = "x- y-"
    else:
        vector = "None"
    goto(-Screen().window_width()/2+5,-Screen().window_height()/2+10)
    write(f"Main position: {int(pos[0]),int(pos[1])}\nDegrees: {int(degree)}\nRotation speed: {rotation_speed:.2f}\nOffset: {offset}\nPerimeter of edge: {int(cube_length)}\nVector of motion: {vector}\nSpeed: {motion_speed:.2f}\nScreen size: {Screen().window_width(),Screen().window_height()}",move=False,align="left",font=("Courier",15,"normal"))

while True:
    Cube()
    Motion()
    Borders()
    for i in pos:
        if i >= 10000 or i <= -10000:
            pos = None
            pos = [0,0]
            degree = 0
            rotation_speed = 0.2
            cube = None
            cube = [[[0,0],[0,0],[0,0],[0,0]],[[0,0],[0,0],[0,0],[0,0]]]
            cube_length = 100
            offset = None
            offset = [round(cube_length/2),0]
            motion_vector = random.randint(0,3)
            motion_speed = 1
            pensize(cube_length/20)