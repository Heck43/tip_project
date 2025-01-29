def update_physics(cube, platforms):
    # Update physics logic here
    cube.y += cube.velocity
    cube.velocity += 0.2  # Применение гравитации к скорости куба
    cube.x += 5  # Движение куба по горизонтали
    cube.distance_traveled += 5  # Обновление расстояния, которое прошел куб

    # Ограничение скорости падения куба
    if cube.velocity > 10:
        cube.velocity = 10

    # Проверка на столкновение с платформами
    for platform in platforms:
        if (cube.x + 50 > platform.x and
            cube.x < platform.x + platform.width and
            cube.y + 50 > platform.y and
            cube.y < platform.y + platform.height):
            # Если куб столкнулся с платформой, то он должен остановиться на ней
            cube.y = platform.y - 50
            cube.velocity = 0
            cube.is_on_ground = True
            break

    # Проверка на столкновение с землей
    if cube.y + 50 > 480:
        cube.y = 480 - 50
        cube.velocity = 0
        cube.is_on_ground = True
