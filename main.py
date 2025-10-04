import pygame
import random
import sys
import math

# Constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
COLOR_BLACK = (6, 8, 12)
COLOR_WHITE = (245, 245, 245)
COLOR_GREY = (160, 160, 160)
COLOR_NEON_BLUE = (55, 200, 255)
COLOR_NEON_PINK = (255, 80, 190)
COLOR_NEON_GREEN = (80, 255, 160)

# Gameplay constants
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 120
PADDLE_MARGIN = 30
PADDLE_SPEED = 7

BALL_SIZE = 14
BALL_MIN_SPEED = 3
BALL_MAX_SPEED = 5
BALL_SPEED_INCREASE_ON_HIT = 0.3

FPS = 60


def reset_ball():
    accel_x = random.uniform(BALL_MIN_SPEED, BALL_MAX_SPEED)
    accel_y = random.uniform(BALL_MIN_SPEED, BALL_MAX_SPEED)
    if random.choice([True, False]):
        accel_x *= -1
    if random.choice([True, False]):
        accel_y *= -1
    return accel_x, accel_y


def draw_center_line(screen):
    dash_height = 20
    gap = 15
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(
            screen,
            COLOR_GREY,
            (SCREEN_WIDTH // 2 - 2, y, 4, dash_height),
        )
        y += dash_height + gap


def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))


def draw_neon_rect(screen, rect, base_color):
    glow_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    inner_rect = pygame.Rect(20, 20, rect.width, rect.height)
    for i in range(10, 0, -1):
        alpha = int(10 * i)
        color = (*base_color, alpha)
        expanded = inner_rect.inflate(i * 3, i * 3)
        pygame.draw.rect(glow_surface, color, expanded, border_radius=6)
    screen.blit(glow_surface, (rect.x - 20, rect.y - 20))
    pygame.draw.rect(screen, base_color, rect, border_radius=6)


def draw_neon_ellipse(screen, rect, base_color):
    glow_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    inner_rect = pygame.Rect(20, 20, rect.width, rect.height)
    for i in range(10, 0, -1):
        alpha = int(12 * i)
        color = (*base_color, alpha)
        expanded = inner_rect.inflate(i * 3, i * 3)
        pygame.draw.ellipse(glow_surface, color, expanded)
    screen.blit(glow_surface, (rect.x - 20, rect.y - 20))
    pygame.draw.ellipse(screen, base_color, rect)


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 3.1415 * 2)
        speed = random.uniform(2, 6)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.x = x
        self.y = y
        self.life = random.uniform(0.3, 0.9)
        self.color = color

    def update(self, dt):
        self.life -= dt
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # slight gravity

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * max(0, min(self.life, 1)))
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (4, 4), 4)
        screen.blit(surf, (self.x - 4, self.y - 4))


def main():

    pygame.init()
    pygame.display.set_caption("Pong")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Fonts
    try:
        font = pygame.font.SysFont("monospace", 56, bold=True)
        small_font = pygame.font.SysFont("monospace", 22)
    except Exception:
        font = pygame.font.Font(None, 56)
        small_font = pygame.font.Font(None, 22)

    # Paddles
    paddle_left = pygame.Rect(
        PADDLE_MARGIN,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )
    paddle_right = pygame.Rect(
        SCREEN_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )

    # Ball
    ball = pygame.Rect(
        SCREEN_WIDTH // 2 - BALL_SIZE // 2,
        SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
        BALL_SIZE,
        BALL_SIZE,
    )
    ball_vx, ball_vy = reset_ball()

    # Trail and particles
    ball_trail = []  # list of (x, y)
    particles = []

    # Scores
    score_left = 0
    score_right = 0

    # Game states: 'menu' | 'countdown' | 'playing'
    state = 'menu'
    countdown_started_at = 0
    countdown_value = 3

    # Screen effects
    shake_timer = 0
    shake_mag = 0
    flash_alpha = 0

    running = True
    while running:
        dt_ms = clock.get_time()
        dt = dt_ms / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == 'menu' and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                state = 'countdown'
                countdown_started_at = pygame.time.get_ticks()
                countdown_value = 3

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False

        # State: countdown
        if state == 'countdown':
            elapsed = (pygame.time.get_ticks() - countdown_started_at) / 1000.0
            countdown_value = max(0, 3 - int(elapsed))
            if elapsed >= 3:
                state = 'playing'

        # Gameplay only during playing
        if state == 'playing':
            # Paddle movement - Left (W/S)
            if keys[pygame.K_w]:
                paddle_left.y -= PADDLE_SPEED
            if keys[pygame.K_s]:
                paddle_left.y += PADDLE_SPEED

            # Paddle movement - Right (Up/Down)
            if keys[pygame.K_UP]:
                paddle_right.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN]:
                paddle_right.y += PADDLE_SPEED

            # Clamp paddles within screen
            paddle_left.y = clamp(paddle_left.y, 0, SCREEN_HEIGHT - PADDLE_HEIGHT)
            paddle_right.y = clamp(paddle_right.y, 0, SCREEN_HEIGHT - PADDLE_HEIGHT)

            # Move ball
            ball.x += int(ball_vx)
            ball.y += int(ball_vy)

            ball_trail.append((ball.centerx, ball.centery))
            if len(ball_trail) > 14:
                ball_trail.pop(0)

            # Wall collisions (top/bottom)
            if ball.top <= 0:
                ball.top = 0
                ball_vy *= -1
                flash_alpha = 140
                shake_timer = 150
                shake_mag = 6
                particles.extend(Particle(ball.centerx, ball.top, COLOR_NEON_BLUE) for _ in range(10))
            elif ball.bottom >= SCREEN_HEIGHT:
                ball.bottom = SCREEN_HEIGHT
                ball_vy *= -1
                flash_alpha = 140
                shake_timer = 150
                shake_mag = 6
                particles.extend(Particle(ball.centerx, ball.bottom, COLOR_NEON_BLUE) for _ in range(10))

            # Paddle collisions
            if ball.colliderect(paddle_left) and ball_vx < 0:
                ball.left = paddle_left.right
                ball_vx *= -1
                offset = (ball.centery - paddle_left.centery) / (PADDLE_HEIGHT / 2)
                ball_vy += offset
                ball_vx += BALL_SPEED_INCREASE_ON_HIT if ball_vx > 0 else -BALL_SPEED_INCREASE_ON_HIT
                flash_alpha = 160
                shake_timer = 180
                shake_mag = 8
                particles.extend(Particle(ball.left, ball.centery, COLOR_NEON_GREEN) for _ in range(14))

            if ball.colliderect(paddle_right) and ball_vx > 0:
                ball.right = paddle_right.left
                ball_vx *= -1
                offset = (ball.centery - paddle_right.centery) / (PADDLE_HEIGHT / 2)
                ball_vy += offset
                ball_vx += BALL_SPEED_INCREASE_ON_HIT if ball_vx > 0 else -BALL_SPEED_INCREASE_ON_HIT
                flash_alpha = 160
                shake_timer = 180
                shake_mag = 8
                particles.extend(Particle(ball.right, ball.centery, COLOR_NEON_PINK) for _ in range(14))

            # Scoring
            if ball.left <= 0:
                score_right += 1
                ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                ball_vx, ball_vy = reset_ball()
                state = 'countdown'
                countdown_started_at = pygame.time.get_ticks()
                countdown_value = 3
                flash_alpha = 180
                shake_timer = 220
                shake_mag = 10
            elif ball.right >= SCREEN_WIDTH:
                score_left += 1
                ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                ball_vx, ball_vy = reset_ball()
                state = 'countdown'
                countdown_started_at = pygame.time.get_ticks()
                countdown_value = 3
                flash_alpha = 180
                shake_timer = 220
                shake_mag = 10

        # Update particles
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.life > 0]

        # Effects decay
        flash_alpha = max(0, flash_alpha - 400 * dt)
        shake_timer = max(0, shake_timer - dt_ms)
        offset_x = random.randint(-shake_mag, shake_mag) if shake_timer > 0 else 0
        offset_y = random.randint(-shake_mag, shake_mag) if shake_timer > 0 else 0

        # Render
        screen.fill(COLOR_BLACK)

        # Apply shake by drawing to a temp surface
        scene = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        draw_center_line(scene)

        # Draw paddles and ball with neon glow
        draw_neon_rect(scene, paddle_left, COLOR_NEON_GREEN)
        draw_neon_rect(scene, paddle_right, COLOR_NEON_PINK)

        # Ball trail
        for i, (tx, ty) in enumerate(ball_trail):
            age = i / max(1, len(ball_trail))
            alpha = int(180 * age)
            size = max(4, int(BALL_SIZE * age))
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLOR_NEON_BLUE, alpha), (size // 2, size // 2), size // 2)
            scene.blit(surf, (tx - size // 2, ty - size // 2))

        draw_neon_ellipse(scene, ball, COLOR_NEON_BLUE)

        # Particles
        for p in particles:
            p.draw(scene)

        # Score
        score_text = font.render(f"{score_left}   {score_right}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        scene.blit(score_text, score_rect)

        # HUD / Info or states
        if state == 'menu':
            title = font.render("P O N G", True, COLOR_WHITE)
            trect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            scene.blit(title, trect)
            prompt = small_font.render("Press any key to start", True, COLOR_GREY)
            prect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            scene.blit(prompt, prect)
        elif state == 'countdown':
            cd_text = font.render(str(max(1, countdown_value)), True, COLOR_WHITE)
            cd_rect = cd_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            scene.blit(cd_text, cd_rect)
        else:
            info_text = small_font.render(
                "Left: W/S  |  Right: Up/Down  |  Esc: Quit",
                True,
                COLOR_GREY,
            )
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            scene.blit(info_text, info_rect)

        # Flash overlay
        if flash_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, int(flash_alpha)))
            scene.blit(overlay, (0, 0))

        # Blit scene with shake
        screen.blit(scene, (offset_x, offset_y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()