import pygame
import random
import csv

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
FONT = pygame.font.Font(None, 36)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Initial Positions
def reset_game_state():
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y
    global paddle_speed, ai_speed, bounce_count, rounds_played
    global score1, score2, game_paused

    score1, score2 = 0, 0
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx, ball_dy = random.choice([-5, 5]), random.choice([-5, 5])
    paddle1_y = paddle2_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    paddle_speed = initial_paddle_speed
    ai_speed = 7
    bounce_count = 0
    rounds_played = 0
    game_paused = False

# Paddle and Ball positions
initial_paddle_speed = 10
reset_game_state()

show_speeds = True
data_count = 0
max_data = 1000
max_score = 100
game_paused = False

with open("pong_training_data.csv", mode="a+", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["ball_x", "ball_y", "ball_dx", "ball_dy", "paddle1_y", "paddle2_y", "paddle1_action", "paddle2_action", "score1", "score2"])

    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Handle events (even when paused)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if game_paused:
            freeze_text = FONT.render("Game Over! Max Score Reached - Press R to Restart", True, WHITE)
            screen.blit(freeze_text, (WIDTH // 2 - 250, HEIGHT // 2))
            pygame.display.update()

            if keys[pygame.K_r]:
                reset_game_state()
            continue  # Skip gameplay logic

        # Increase speed every 50 bounces
        if bounce_count // 50 > rounds_played:
            rounds_played += 1
            ball_dx *= 1.2
            ball_dy *= 1.2
            paddle_speed = int(initial_paddle_speed * 1.2)
            ai_speed = int(ai_speed * 1.2)

        # Player-controlled Paddle
        paddle1_action = 0
        if keys[pygame.K_UP] and paddle1_y > 0:
            paddle1_y -= paddle_speed
            paddle1_action = -1
        elif keys[pygame.K_DOWN] and paddle1_y + PADDLE_HEIGHT < HEIGHT:
            paddle1_y += paddle_speed
            paddle1_action = 1

        # AI Paddle Movement
        paddle2_action = 0
        if ball_dx > 0:
            if random.random() < 0.9:
                if paddle2_y + PADDLE_HEIGHT // 2 < ball_y:
                    paddle2_y += ai_speed
                    paddle2_action = 1
                elif paddle2_y + PADDLE_HEIGHT // 2 > ball_y:
                    paddle2_y -= ai_speed
                    paddle2_action = -1

        # Move Ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Collisions
        if ball_y - BALL_RADIUS <= 0 or ball_y + BALL_RADIUS >= HEIGHT:
            ball_dy *= -1

        if (ball_x - BALL_RADIUS <= PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT) or \
           (ball_x + BALL_RADIUS >= WIDTH - PADDLE_WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT):
            ball_dx *= -1
            bounce_count += 1

        # Scoring
        if ball_x < 0:
            score2 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx *= -1
        elif ball_x > WIDTH:
            score1 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx *= -1

        # Check for pause condition
        if max(score1, score2) >= max_score:
            game_paused = True
            continue  # Skip drawing frame this round

        # Log data
        writer.writerow([ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y,
                         paddle1_action, paddle2_action, score1, score2])
        data_count += 1

        # Drawing
        pygame.draw.rect(screen, WHITE, (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_RADIUS)

        score_text = FONT.render(f"{score1} - {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - 30, 20))

        if show_speeds:
            custom_font = pygame.font.Font(None, 28)  # Smaller font size

            speed_text = custom_font.render(
                f"Ball Speed: {abs(ball_dx):.1f}, Paddle Speed: {paddle_speed}", True, WHITE
            )
            screen.blit(speed_text, (20, HEIGHT - 60))  # x, y position (e.g., left side above bottom)


        pygame.display.update()

pygame.quit()
