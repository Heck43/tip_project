import pygame
import sys
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()  # Инициализация звукового модуля

# Устанавливаем размеры окна
screen_width = 1628
screen_height = 1017
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mysteries of the Pixel City")

# Загружаем изображения
background_image = pygame.image.load('image/location1.png').convert()
character_image = pygame.image.load('image/Sprite-detective.png').convert_alpha()
npc_image = pygame.image.load('image/Sprite-npc.png').convert_alpha()

# Загружаем фоны для диалогов NPC
dialogue_backgrounds = [pygame.image.load(f'image/dialogue_background{i}.png').convert() for i in range(1, 6)]

# Создаем объект для управления временем
clock = pygame.time.Clock()

# Устанавливаем шрифты
default_font = pygame.font.Font('font/better-vcr_0.ttf', 30)
loud_font = pygame.font.Font('font/GhastlyPanicCyr.otf', 60)
angry_font = pygame.font.Font('font/cyrillic_pixel-7.ttf', 40)
name_font = pygame.font.Font('font/better-vcr_0.ttf', 20)

# Имена персонажей
character_name = "Капитан детектив"
npc_name = "NPC Персонаж"
next_location_name = "Центральная площадь"  # Добавляем название следующей локации
prev_location_name = "Предыдущая локация"

# Параметры для отображения названия локации
location_display_x = screen_width - 150
right_location_display_x = screen_width - 150  # Для правой стороны
location_display_radius = 200

# Загружаем звук диалога
dialogue_sound = pygame.mixer.Sound('soung/dialogue_sound.wav')

class DialogueSystem:
    def __init__(self):
        self.dialogues = []
        self.current_index = 0
        self.current_char_index = 0
        self.time_since_last_update = 0
        self.active = False
        self.speed = 50
        self.font = default_font
        self.choices = []
        self.selected_choice = 0
        self.choice_mode = False
        self.current_response = None
        self.talking_to_npc = False
        self.showing_response = False
        self.full_text_shown = False
        self.current_dialogue_background_index = 0
        self.current_dialogue_background = dialogue_backgrounds[self.current_dialogue_background_index]
        self.dialogue_surface = pygame.Surface((screen_width, 200))
        self.dialogue_surface.set_alpha(180)
        self.sound_delay = 0
        self.max_text_width = screen_width - 100  # Maximum width for text before wrapping

    def start_dialogue(self, dialogue_list, is_npc=False):
        self.dialogues = dialogue_list
        self.current_index = 0
        self.current_char_index = 0
        self.active = True
        self.choices = []
        self.selected_choice = 0
        self.choice_mode = False
        self.current_response = None
        self.talking_to_npc = is_npc
        self.showing_response = False
        self.full_text_shown = False
        if is_npc:
            self.change_dialogue_background()

    def update(self, delta_time):
        if self.active and not self.choice_mode:
            self.time_since_last_update += delta_time
            if self.time_since_last_update >= self.speed / 1000 and self.current_char_index < len(self.dialogues[self.current_index][0]):
                self.current_char_index += 1
                self.time_since_last_update = 0
                
                # Воспроизводим звук с задержкой
                self.sound_delay += 1
                if self.sound_delay >= 3:  # Воспроизводим звук каждые 3 символа
                    dialogue_sound.play()
                    self.sound_delay = 0
                
            elif self.current_char_index >= len(self.dialogues[self.current_index][0]):
                self.full_text_shown = True

    def draw(self, surface, name):
        if self.active or self.choice_mode:
            if self.talking_to_npc:
                surface.blit(self.current_dialogue_background, (0, 0))
            else:
                self.dialogue_surface.fill((0, 0, 0))
                surface.blit(self.dialogue_surface, (0, screen_height - 400))  

            name_surface = default_font.render(name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(topleft=(10, screen_height - 380))  
            surface.blit(name_surface, name_rect)

            if self.active and not self.choice_mode:
                current_dialogue_text, _, current_font, _ = self.dialogues[self.current_index]
                visible_text = current_dialogue_text[:self.current_char_index]
                wrapped_lines = self.wrap_text(visible_text, current_font, self.max_text_width)
                
                for i, line in enumerate(wrapped_lines):
                    rendered_text = current_font.render(line, True, (255, 255, 255))
                    surface.blit(rendered_text, (50, screen_height - 330 + i * 35))  # 35 pixels between lines
            
            if self.choice_mode and not self.showing_response:
                for i, choice in enumerate(self.choices):
                    choice_text = default_font.render(choice, True, (255, 255, 255))
                    choice_rect = choice_text.get_rect(center=(screen_width // 2, screen_height - 300 + i * 40))  
                    surface.blit(choice_text, choice_rect)

                    if i == self.selected_choice:
                        pygame.draw.rect(surface, (255, 255, 0), choice_rect.inflate(10, 10), 2)

    def next(self):
        if self.active and not self.choice_mode:
            if not self.full_text_shown:
                self.current_char_index = len(self.dialogues[self.current_index][0])
                self.full_text_shown = True
            else:
                self.current_index += 1
                self.current_char_index = 0
                self.full_text_shown = False
                if self.talking_to_npc:
                    self.change_dialogue_background()
                if self.current_index >= len(self.dialogues):
                    self.active = False
                    if self.talking_to_npc:
                        self.finish_response()
                    elif self.showing_response:
                        self.finish_response()

    def add_choices(self, choices):
        self.choices = choices
        self.selected_choice = 0
        self.choice_mode = True

    def select_choice(self):
        if self.choices:
            selected = self.choices[self.selected_choice]
            self.current_response = self.get_response(selected)
            self.dialogues = [(self.current_response, 50, default_font, False)]
            self.current_index = 0
            self.current_char_index = 0
            self.choice_mode = False
            self.active = True
            self.showing_response = True
            self.full_text_shown = False
            self.change_dialogue_background()
            return selected
        return None

    def finish_response(self):
        self.current_response = None
        self.choice_mode = True
        self.active = False
        self.showing_response = False
        self.choices = ["Спросить о тайнах города", "Спросить о безопасности", "Пока, мне нужно идти"]

    def get_response(self, choice):
        responses = {
            "Спросить о тайнах города": "В городе много тайн. Некоторые говорят о древних артефактах, спрятанных под улицами.",
            "Спросить о безопасности": "Будьте осторожны, особенно в темных переулках. Держите глаза открытыми.",
            "Пока, мне нужно идти": "Удачи вам в ваших приключениях, капитан!"
        }
        return responses.get(choice, "Извините, я не могу ответить на это.")

    def change_dialogue_background(self):
        self.current_dialogue_background_index = (self.current_dialogue_background_index + 1) % len(dialogue_backgrounds)
        self.current_dialogue_background = dialogue_backgrounds[self.current_dialogue_background_index]

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, (255, 255, 255))
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))
        return lines

class Character(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)

    def update(self, dx=0, dy=0):
        self.rect.x += dx
        self.rect.y += dy

def fade_screen(surface, start_dialogue=False, end_dialogue=False, fade_time=0.001):
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill((0, 0, 0))
    
    for alpha in range(0, 256, 8):
        fade_surface.set_alpha(alpha)
        surface.blit(background_image, (0, 0))
        all_sprites.draw(surface)
        surface.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(int(fade_time * 700 / 1000))
    
    if start_dialogue:
        dialogue_system.start_dialogue(npc_dialogue_list, is_npc=True)
    elif end_dialogue:
        dialogue_system.active = False
        dialogue_system.talking_to_npc = False
        dialogue_system.choice_mode = False
    
    for alpha in range(255, -1, -8):
        fade_surface.set_alpha(alpha)
        surface.blit(background_image, (0, 0))
        all_sprites.draw(surface)
        if dialogue_system.active or dialogue_system.choice_mode:
            dialogue_system.draw(surface, npc_name if dialogue_system.talking_to_npc else character_name)
        surface.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(int(fade_time * 700 / 256))

def fade_from_black(surface):
    # Создаем черную поверхность
    black_surface = pygame.Surface((screen_width, screen_height))
    black_surface.fill((0, 0, 0))
    
    # Плавное появление из черного
    for alpha in range(255, 0, -5):
        # Отрисовываем текущее состояние игры
        surface.blit(background_image, (0, 0))
        all_sprites.draw(surface)
        
        # Накладываем черную поверхность с уменьшающейся прозрачностью
        black_surface.set_alpha(alpha)
        surface.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)

def location_transition_animation(surface, location_name):
    # Сохраняем текущее состояние экрана
    current_screen = surface.copy()
    
    # Создаем черную поверхность
    black_surface = pygame.Surface((screen_width, screen_height))
    black_surface.fill((0, 0, 0))
    
    # Создаем поверхность для текста
    location_name_surface = loud_font.render(location_name, True, (255, 255, 255))
    location_name_rect = location_name_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Затемнение текущего экрана
    for alpha in range(0, 255, 5):
        surface.blit(current_screen, (0, 0))
        black_surface.set_alpha(alpha)
        surface.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Показываем название локации
    for alpha in range(0, 255, 5):
        surface.fill((0, 0, 0))
        location_name_surface.set_alpha(alpha)
        surface.blit(location_name_surface, location_name_rect)
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Задержка, чтобы текст был виден
    pygame.time.delay(500)
    
    # Затемняем название локации
    for alpha in range(255, 0, -5):
        surface.fill((0, 0, 0))
        location_name_surface.set_alpha(alpha)
        surface.blit(location_name_surface, location_name_rect)
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Черный экран перед переходом
    surface.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.delay(100)
    
    return True

def transition_to_location(direction):
    if direction == "prev":
        location_transition_animation(screen, prev_location_name)
        # Импортируем следующую локацию только после завершения анимации
        import location2
        location2.fade_from_black(screen)  # Добавляем эффект появления
        location2.main()
    elif direction == "next":
        location_transition_animation(screen, next_location_name)
        import location2  # Исправлено с location3 на location2
        location2.fade_from_black(screen)  # Добавляем эффект появления
        location2.main()

def initialize_sprites():
    global all_sprites, character, npc
    all_sprites = pygame.sprite.Group()
    character = Character(character_image, (600, 600))
    npc = Character(npc_image, (1100, 600))
    all_sprites.add(character, npc)

def main():
    global running, screen, all_sprites, character, dialogue_system
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    
    # Инициализация спрайтов и диалоговой системы
    initialize_sprites()
    dialogue_system = DialogueSystem()
    
    # Эффект появления из черного экрана при запуске локации
    fade_from_black(screen)
    
    running = True
    initial_dialogue_active = True
    
    # Список начальных диалогов персонажа
    initial_dialogue_list = [
        ("Привет, как дела ?", 50, default_font, False),
        ("Я чувствую, что что-то назревает.", 45, loud_font, True),
        ("Это место полное тайн.", 50, default_font, False),
        ("Я не могу оставить это без внимания.", 45, loud_font, True)
    ]

    # Список диалогов NPC
    npc_dialogue_list = [
        ("Привет, капитан!", 50, default_font, False),
        ("Что ты здесь делаешь?", 50, default_font, False),
        ("Будь осторожен, здесь много опасностей.", 50, default_font, False)
    ]

    dialogue_system.start_dialogue(initial_dialogue_list, is_npc=False)

    # Радиус взаимодействия с NPC
    interaction_radius = 200

    # Определяем границы области, в которой может перемещаться персонаж
    boundary_rect = pygame.Rect(-100, 50, screen_width - -120, screen_height - 130)

    while running:
        delta_time = clock.tick(60)  # Ограничиваем FPS до 60

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if dialogue_system.active and not dialogue_system.choice_mode:
                        if dialogue_system.full_text_shown:
                            dialogue_system.next()
                            if not dialogue_system.active:
                                if initial_dialogue_active:
                                    initial_dialogue_active = False
                        else:
                            dialogue_system.current_char_index = len(dialogue_system.dialogues[dialogue_system.current_index][0])
                            dialogue_system.full_text_shown = True
                    elif dialogue_system.choice_mode and not dialogue_system.showing_response:
                        selected_choice = dialogue_system.select_choice()
                        print(f"Вы выбрали: {selected_choice}")
                        if selected_choice == "Пока, мне нужно идти":
                            fade_screen(screen, end_dialogue=True)
                elif event.key == pygame.K_e:  # Взаимодействие с NPC или переход локации
                    # Проверяем расстояние до NPC
                    distance_to_npc = math.hypot(character.rect.centerx - npc.rect.centerx, character.rect.centery - npc.rect.centery)
                    if distance_to_npc <= interaction_radius:
                        fade_screen(screen, start_dialogue=True)
                    # Проверяем, находится ли игрок в зоне перехода
                    elif abs(character.rect.centerx - location_display_x) <= location_display_radius:
                        transition_to_location("next")
                elif event.key == pygame.K_UP and dialogue_system.choice_mode:
                    dialogue_system.selected_choice = (dialogue_system.selected_choice - 1) % len(dialogue_system.choices)
                elif event.key == pygame.K_DOWN and dialogue_system.choice_mode:
                    dialogue_system.selected_choice = (dialogue_system.selected_choice + 1) % len(dialogue_system.choices)

            # Обработка выбора с помощью мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левый клик мыши
                if dialogue_system.choice_mode and not dialogue_system.showing_response:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i, choice in enumerate(dialogue_system.choices):
                        choice_rect = default_font.render(choice, True, (255, 255, 255)).get_rect(center=(screen_width // 2, screen_height - 300 + i * 40))
                        if choice_rect.collidepoint(mouse_x, mouse_y):
                            selected_choice = dialogue_system.select_choice()
                            print(f"Вы выбрали: {selected_choice}")
                            if selected_choice == "Пока, мне нужно идти":
                                fade_screen(screen, end_dialogue=True)

        # Управление движением персонажа только если диалог не активен
        if not dialogue_system.active and not dialogue_system.choice_mode and not initial_dialogue_active:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx -= 10
            if keys[pygame.K_RIGHT]:
                dx += 10
            if keys[pygame.K_UP]:
                dy -= 10
            if keys[pygame.K_DOWN]:
                dy += 10

            character.update(dx, dy)

            # Ограничение перемещения персонажа в пределах границ
            character.rect.clamp_ip(boundary_rect)

        # Заполнение фона
        screen.blit(background_image, (0, 0))

        # Отрисовка спрайтов
        all_sprites.draw(screen)

        # Рисуем рамку границ
        pygame.draw.rect(screen, (255, 0, 0), boundary_rect, 2)  # Рамка красного цвета

        # Проверяем расстояние между персонажем и NPC
        distance_to_npc = math.hypot(character.rect.centerx - npc.rect.centerx, character.rect.centery - npc.rect.centery)
        
        # Если персонаж находится в пределах радиуса взаимодействия, отображаем имя NPC
        if distance_to_npc <= interaction_radius:
            name_surface = name_font.render(npc_name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(center=(npc.rect.centerx, npc.rect.top - 20))
            
            # Создаем фон для имени
            background_rect = name_rect.copy()
            background_rect.inflate_ip(10, 10)
            pygame.draw.rect(screen, (0, 0, 0, 128), background_rect)
            
            screen.blit(name_surface, name_rect)

        # Проверяем расстояние между персонажем и правым краем для отображения названия локации
        distance_to_right = abs(character.rect.centerx - location_display_x)
        
        # Если персонаж находится в пределах радиуса от правого края, отображаем название локации
        if distance_to_right <= location_display_radius:
            # Создаем поверхность с названием локации
            location_name_surface = loud_font.render(next_location_name, True, (255, 255, 255))
            location_name_rect = location_name_surface.get_rect(center=(location_display_x, screen_height // 2))  # Changed to screen_height // 2 for vertical center
            
            # Создаем фон для названия
            background_rect = location_name_rect.copy()
            background_rect.inflate_ip(20, 20)
            background_surface = pygame.Surface((background_rect.width, background_rect.height))
            background_surface.fill((0, 0, 0))
            background_surface.set_alpha(128)
            
            # Отображаем фон и текст
            screen.blit(background_surface, background_rect)
            screen.blit(location_name_surface, location_name_rect)

        # Обновляем и отрисовываем систему диалогов
        dialogue_system.update(delta_time)
        if dialogue_system.active or dialogue_system.choice_mode:
            dialogue_system.draw(screen, npc_name if dialogue_system.talking_to_npc else character_name)

        # Обновляем экран
        pygame.display.flip()

    # Завершение игры
    pygame.quit()
    sys.exit()

main()