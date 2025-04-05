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

# Paddle and Ball positions
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = random.choice([-5, 5]), random.choice([-5, 5])
paddle1_y, paddle2_y = HEIGHT // 2 - PADDLE_HEIGHT // 2, HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle_speed = 10
ai_speed = 7  # Speed of AI paddle movement

# Scores
score1, score2 = 0, 0

data_count = 0
max_data = 10000  # Stop after collecting 1000 data points

# Open CSV file for logging data
with open("pong_training_data.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["ball_x", "ball_y", "ball_dx", "ball_dy", "paddle1_y", "paddle2_y", "paddle1_action", "paddle2_action", "score1", "score2"])

    # Game loop
    running = True
    while running and data_count < max_data:
        pygame.time.delay(1000 // FPS)
        screen.fill(BLACK)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # AI Paddle Movement (Left Paddle with randomness)
        paddle1_action = 0  # Default no movement
        if ball_dx < 0:  # Only move when the ball is coming towards the AI
            if random.random() < 1:  # 90% chance to move towards the ball, 10% chance to fail
                if paddle1_y + PADDLE_HEIGHT // 2 < ball_y:
                    paddle1_y += ai_speed
                    paddle1_action = 1  # Move down
                elif paddle1_y + PADDLE_HEIGHT // 2 > ball_y:
                    paddle1_y -= ai_speed
                    paddle1_action = -1  # Move up
        
        # AI Paddle Movement (Right Paddle with randomness)
        paddle2_action = 0  # Default no movement
        if ball_dx > 0:  # Right paddle AI
            if random.random() < 1:
                if paddle2_y + PADDLE_HEIGHT // 2 < ball_y:
                    paddle2_y += ai_speed
                    paddle2_action = 1  # Move down
                elif paddle2_y + PADDLE_HEIGHT // 2 > ball_y:
                    paddle2_y -= ai_speed
                    paddle2_action = -1  # Move up
        
        # Move Ball
        ball_x += ball_dx
        ball_y += ball_dy
        
        # Ball Collision with top/bottom walls
        if ball_y - BALL_RADIUS <= 0 or ball_y + BALL_RADIUS >= HEIGHT:
            ball_dy *= -1
        
        # Ball Collision with paddles
        if (ball_x - BALL_RADIUS <= PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT) or \
           (ball_x + BALL_RADIUS >= WIDTH - PADDLE_WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT):
            ball_dx *= -1
        
        # Ball out of bounds (scoring)
        if ball_x < 0:
            score2 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Reset ball position
            ball_dx *= -1  # Reverse direction
        elif ball_x > WIDTH:
            score1 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2  # Reset ball position
            ball_dx *= -1  # Reverse direction
        
        # Log data
        writer.writerow([ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y, paddle1_action, paddle2_action, score1, score2])
        data_count += 1
        
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_RADIUS)
        
        # Draw scores
        score_text = FONT.render(f"{score1} - {score2}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - 30, 20))
        
        pygame.display.update()

pygame.quit()
