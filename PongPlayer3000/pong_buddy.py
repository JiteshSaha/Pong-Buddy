import pygame
import random
import torch
import joblib
import numpy as np
from safetensors.torch import load_file

# --- Load trained AI model ---
class PongAI(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(7, 64)
        self.fc2 = torch.nn.Linear(64, 32)
        self.fc3 = torch.nn.Linear(32, 3)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

model = PongAI()
state_dict = load_file("pong_ai_model.safetensors")
model.load_state_dict(state_dict)
model.eval()

scaler = joblib.load("scaler.pkl")

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
FPS = 60
FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = random.choice([-5, 5]), random.choice([-5, 5])
paddle1_y = paddle2_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle_speed = 10

score1, score2 = 0, 0

clock = pygame.time.Clock()
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # Handle quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Player Paddle (Left, Human) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1_y > 0:
        paddle1_y -= paddle_speed
    if keys[pygame.K_s] and paddle1_y < HEIGHT - PADDLE_HEIGHT:
        paddle1_y += paddle_speed

    # --- AI Paddle (Right) ---
    input_features = np.array([[ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y, 0]])
    input_scaled = scaler.transform(input_features)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor)
        action = torch.argmax(output).item()
        print(f"{action}")
    # Convert action (0=up, 1=stay, 2=down)
    if action == 0 and paddle2_y > 0:
        paddle2_y -= paddle_speed
    elif action == 2 and paddle2_y < HEIGHT - PADDLE_HEIGHT:
        paddle2_y += paddle_speed

    # --- Ball movement ---
    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y - BALL_RADIUS <= 0 or ball_y + BALL_RADIUS >= HEIGHT:
        ball_dy *= -1

    if (ball_x - BALL_RADIUS <= PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT) or \
       (ball_x + BALL_RADIUS >= WIDTH - PADDLE_WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT):
        ball_dx *= -1

    if ball_x < 0:
        score2 += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_dx *= -1
    elif ball_x > WIDTH:
        score1 += 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_dx *= -1

    # --- Draw ---
    pygame.draw.rect(screen, WHITE, (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_RADIUS)

    score_text = FONT.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - 30, 20))
    pygame.display.update()

pygame.quit()
