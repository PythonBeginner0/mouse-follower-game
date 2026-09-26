import math
import random
import pygame

# ----------------------------
# Setup
# ----------------------------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse Chaser")
clock = pygame.time.Clock()

# Colors
BG = (16, 20, 28)
PLAYER_COLORS = [(255, 100, 100), (255, 200, 100), (120, 220, 255)]
BOOST_COLOR = (78, 220, 120)
BOOST_SHADOW = (30, 130, 70)
STOP_COLOR = (255, 90, 90)
STOP_SHADOW = (160, 40, 40)
WHITE = (255, 255, 255)
TEXT = (240, 240, 240)
DARK = (25, 25, 25)
GOLD = (255, 210, 80)

# Zones
BOOST_ZONE = pygame.Rect(120, 120, 220, 180)
STOP_ZONE = pygame.Rect(560, 310, 220, 170)

# ----------------------------
# Player class
# ----------------------------
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20
        self.speed = 260
        self.boost_speed = 520
        self.max_speed = 780
        self.drag = 0.84
        self.color = PLAYER_COLORS[0]
        self.flash_timer = 0.0

    def update(self, dt, mouse_x, mouse_y):
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = math.hypot(dx, dy)

        boost_active = BOOST_ZONE.collidepoint(mouse_x, mouse_y)
        stop_active = STOP_ZONE.collidepoint(mouse_x, mouse_y)

        target_speed = self.speed
        if boost_active:
            target_speed = self.boost_speed
            self.flash_timer = 0.25
            self.color = (135, 255, 150)
        elif stop_active:
            self.color = (255, 120, 120)
        else:
            self.color = PLAYER_COLORS[0]
            self.flash_timer = max(0, self.flash_timer - dt)

        if not stop_active and not boost_active:
            if dist > 1:
                # Movement toward mouse
                desired_vx = (dx / dist) * target_speed
                desired_vy = (dy / dist) * target_speed
                self.vx += (desired_vx - self.vx) * 0.12
                self.vy += (desired_vy - self.vy) * 0.12
        else:
            # Stop moving when mouse is inside boost or stop zone
            self.vx *= 0.72
            self.vy *= 0.72

        # Keep it under max speed
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce on screen edges
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -0.5
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx *= -0.5
        if self.y < self.radius:
            self.y = self.radius
            self.vy *= -0.5
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.vy *= -0.5

    def draw(self, surface):
        # Shadow
        pygame.draw.circle(surface, (0, 0, 0, 80), (int(self.x) + 5, int(self.y) + 8), self.radius)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

        # Eye
        eye_offset = 7
        eye_x = self.x + 5
        eye_y = self.y - 4
        pygame.draw.circle(surface, (20, 20, 20), (int(eye_x), int(eye_y)), 4)

        # Smile
        pygame.draw.arc(surface, (20, 20, 20), (self.x - 9, self.y - 4, 18, 18), 0.5, math.pi - 0.5, 2)

        # Flash effect when boosting
        if self.flash_timer > 0:
            glow_radius = self.radius + 10 + (self.flash_timer * 25)
            pygame.draw.circle(surface, (140, 255, 170, 80), (int(self.x), int(self.y)), int(glow_radius), 2)

# ----------------------------
# Particles
# ----------------------------
particles = []

def add_particles(x, y, color, count=8):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(20, 150)
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(0.3, 0.9),
            "color": color,
            "size": random.randint(2, 5),
        })

# ----------------------------
# Main
# ----------------------------
player = Player(WIDTH // 2, HEIGHT // 2)
running = True
font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 16)

# Hide system cursor
pygame.mouse.set_visible(False)

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Update player
    player.update(dt, mouse_x, mouse_y)

    # Particles for boost area
    if BOOST_ZONE.collidepoint(player.x, player.y):
        add_particles(player.x, player.y, (120, 255, 140), 2)
    if STOP_ZONE.collidepoint(player.x, player.y):
        add_particles(player.x, player.y, (255, 100, 100), 2)

    # Update particles
    for p in particles[:]:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["life"] -= dt
        p["color"] = (
            max(0, min(255, p["color"][0])),
            max(0, min(255, p["color"][1])),
            max(0, min(255, p["color"][2])),
        )
        if p["life"] <= 0:
            particles.remove(p)

    # Draw background
    screen.fill(BG)

    # Add a subtle moving grid or glow
    for x in range(0, WIDTH, 60):
        pygame.draw.line(screen, (40, 48, 60), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (40, 48, 60), (0, y), (WIDTH, y), 1)

    # Draw boost rectangle
    pygame.draw.rect(screen, BOOST_SHADOW, BOOST_ZONE.inflate(10, 10), border_radius=10)
    pygame.draw.rect(screen, BOOST_COLOR, BOOST_ZONE, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255, 120), BOOST_ZONE, 2, border_radius=10)
    boost_label = font.render("BOOST", True, WHITE)
    screen.blit(boost_label, (BOOST_ZONE.x + 18, BOOST_ZONE.y + 12))

    # Draw stop rectangle
    pygame.draw.rect(screen, STOP_SHADOW, STOP_ZONE.inflate(10, 10), border_radius=10)
    pygame.draw.rect(screen, STOP_COLOR, STOP_ZONE, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255, 120), STOP_ZONE, 2, border_radius=10)
    stop_label = font.render("STOP", True, WHITE)
    screen.blit(stop_label, (STOP_ZONE.x + 18, STOP_ZONE.y + 12))

    # Draw particle effects
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

    # Draw player
    player.draw(screen)

    # Draw custom cursor
    pygame.draw.line(screen, GOLD, (mouse_x - 8, mouse_y), (mouse_x + 8, mouse_y), 2)
    pygame.draw.line(screen, GOLD, (mouse_x, mouse_y - 8), (mouse_x, mouse_y + 8), 2)
    pygame.draw.circle(screen, GOLD, (mouse_x, mouse_y), 5, 1)

    # Text instructions
    hint = small_font.render("Move your mouse • Green zone = player speeds up • Red zone = player stops moving", True, TEXT)
    screen.blit(hint, (18, HEIGHT - 28))

    pygame.display.flip()

pygame.quit()
