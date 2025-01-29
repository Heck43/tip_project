import pygame
import sys
from cube import Cube
from level import generate_level
from graphics import draw_cube, draw_platform, draw_spike
from physics import update_physics
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import os

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Windowed mode
    fullscreen = False

    # Load the main menu image
    current_dir = os.path.dirname(__file__)
    menu_image_path = os.path.join(current_dir, 'menu_image.png')  # Replace with the actual file name and path
    menu_image = load_image(menu_image_path)
    
    if menu_image is None:
        print("Error loading menu image. Using default background.")
        menu_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu_image.fill((0, 0, 0))  # Default black background
    else:
        menu_image = pygame.transform.scale(menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Button properties
    button_width = 200
    button_height = 50
    button_x = SCREEN_WIDTH - 600
    button_y = SCREEN_HEIGHT - 200
    button_color = (255, 255, 255)
    button_hover_color = (255, 255, 255)
    button_text_color = (255, 255, 255)
    button_font = pygame.font.Font(None, 32)
    
    new_button_pressed = False
    new_section_active = False

    # Main menu 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_x < event.pos[0] < button_x + button_width and button_y < event.pos[1] < button_y + button_height:
                    start_game(screen, fullscreen)
                    return
                elif button_x + 300 < event.pos[0] < button_x + 500 and button_y < event.pos[1] < button_y + button_height:
                    new_button_pressed = True
                    new_section_active = True
                elif new_section_active and event.pos[0] > SCREEN_WIDTH // 2 - 100 and event.pos[0] < SCREEN_WIDTH // 2 + 100 and event.pos[1] > SCREEN_HEIGHT // 2 - 50 and event.pos[1] < SCREEN_HEIGHT // 2 + 50:
                    new_section_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    fullscreen = not fullscreen
        # Draw main menu
        screen.blit(menu_image, (0, 0))  # Draw the menu image
        if not new_section_active:
            screen.blit(menu_image, (0, 0))  # Draw the menu image

        ## Draw button
        mouse_pos = pygame.mouse.get_pos()
        if button_x < mouse_pos[0] < button_x + button_width and button_y < mouse_pos[1] < button_y + button_height:
            pygame.draw.rect(screen, button_hover_color, (button_x, button_y, button_width, button_height), 2)
        else:
            pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height), 2)
        button_text = button_font.render("Играть", True, button_text_color)
        screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, button_y + button_height // 2 - button_text.get_height() // 2))

    # Draw new button
        if button_x + 300 < mouse_pos[0] < button_x + 500 and button_y < mouse_pos[1] < button_y + button_height:
                pygame.draw.rect(screen, button_hover_color, (button_x + 300, button_y, button_width, button_height), 2)
        else:
                pygame.draw.rect(screen, button_color, (button_x + 300, button_y, button_width, button_height), 2)
        new_button_text = button_font.render("Настройки", True, button_text_color)
        screen.blit(new_button_text, (button_x + 300 + button_width // 2 - new_button_text.get_width() // 2, button_y + button_height // 2 - new_button_text.get_height() // 2))

        # Draw "Кто сделал" и "Версия кода"
        author = "by Heck1337"  # Замените на ваше имя
        version = "Alpha 0.1"      # Замените на вашу версию
        font_small = pygame.font.Font(None, 24)
        text_author = font_small.render(author, True, (255, 255, 255))
        text_version = font_small.render(version, True, (255, 255, 255))
        screen.blit(text_author, (SCREEN_WIDTH - 1015, SCREEN_HEIGHT - 50))
        screen.blit(text_version, (SCREEN_WIDTH - 1015, SCREEN_HEIGHT - 20))

        if new_section_active:
    # Draw background
            screen.blit(menu_image, (0, 0))  # Draw the menu image

            # Draw new section of the main screen
            new_section_text = button_font.render("Настройки", True, (0, 0, 0))
            screen.blit(new_section_text, (SCREEN_WIDTH - 750,  SCREEN_HEIGHT - 720))
            exit_button = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100, 200, 100)
            pygame.draw.rect(screen, (255, 0, 0), exit_button)
            exit_text = button_font.render("Выйти", True, (255, 255, 255))
            screen.blit(exit_text, (exit_button.centerx - exit_text.get_width() // 2, exit_button.centery - exit_text.get_height() // 2))

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.collidepoint(event.pos):
                        new_section_active = False
        pygame.display.flip()
        pygame.time.Clock().tick(90)

def load_image(path):
    try:
        return pygame.image.load(path)
    except pygame.error as e:
        print(f"Error loading image: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None

def start_game(screen, fullscreen):
    # Initialize game objects
    cube = Cube(50, SCREEN_HEIGHT - 50)  # Start on the ground (SCREEN_HEIGHT - 50)
    level = generate_level()

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    if fullscreen:
                        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    else:
                        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    fullscreen = not fullscreen
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and cube.is_on_ground:
            cube.velocity = -6
            cube.is_on_ground = False
            cube.target_rotation_angle = (cube.target_rotation_angle - 90) % 360
        if not keys[pygame.K_SPACE] and cube.velocity < 0:
            cube.velocity += 0.5
            if cube.velocity >= 0:
                cube.velocity = 0

        # Update game logic
        cube.update_rotation()
        update_physics(cube, level.platforms)

        # Check for collisions with spikes
        for spike in level.spikes:
            if check_collisions(cube, spike):
                game_over(screen)
                pygame.time.wait(0)  # Wait for 2 seconds
                play_again = True
                while play_again:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                play_again = False
                                cube = Cube(50, SCREEN_HEIGHT - 50)  # Reset cube position
                                level = generate_level()  # Reset level
                            elif event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()

        # Draw graphics
        screen.fill((0, 0, 0))  # Черный фон
        camera_x = cube.x - SCREEN_WIDTH // 7
        camera_y = -1  # You can adjust this value to change the camera's y-position
        draw_cube(cube, screen, camera_x, camera_y)
        for platform in level.platforms:
            draw_platform(platform, screen, camera_x, camera_y)
        for spike in level.spikes:
            draw_spike(spike, screen, camera_x, camera_y)

        # Update screen
        pygame.display.flip()
        pygame.time.Clock().tick(120)

def check_collisions(cube, spike):
    if (cube.x + 25 > spike.x and
        cube.x - 25 < spike.x + 30 and
        cube.y + 25 > spike.y and
        cube.y - 25 < spike.y + 30):
        return True
    return False

def game_over(screen):
    font = pygame.font.Font(None, 64)
    text = font.render("Game Over!", True, (255, 255, 255))
    font2 = pygame.font.Font(None, 32)
    text2 = font2.render("Press SPACE to play again, or ESC to return to main menu", True, (255, 255, 255))

    # Create a transparent background
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.set_alpha(128)  # Transparency 128 out of 255
    background.fill((0, 0, 0))  # Black background

    # First, draw the background
    screen.blit(background, (0, 0))

    # Then, draw the text
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 32))
    screen.blit(text2, (SCREEN_WIDTH - 690, SCREEN_HEIGHT // 2 + 32))

    pygame.display.flip()

    play_again = True
    while play_again:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play_again = False
                    cube = Cube(50, SCREEN_HEIGHT - 50)  # Reset cube position
                    level = generate_level()  # Reset level
                elif event.key == pygame.K_ESCAPE:
                    main()  # Return to main menu

if __name__ == "__main__":
    main()