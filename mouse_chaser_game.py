import math
import random
import pygame

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse Chaser - Road Adventure")
clock = pygame.time.Clock()

# Screen and world settings
WORLD_WIDTH, WORLD_HEIGHT = 2600, 1400
PLAYER_START = (250.0, 700.0)
CAMERA_SMOOTHING = 5.0

# Colors
BG = (16, 20, 28)
GRID = (38, 47, 60)
WHITE = (255, 255, 255)
TEXT = (235, 235, 235)
GOLD = (255, 210, 80)
GREEN = (70, 210, 105)
GREEN_DARK = (30, 125, 65)
SUPER_GREEN = (0, 245, 165)
SUPER_DARK = (0, 145, 95)
PINK = (245, 95, 155)
PINK_DARK = (155, 45, 95)
YELLOW = (255, 215, 0)
YELLOW_DARK = (170, 135, 0)
ROAD = (78, 82, 94)
ROAD_EDGE = (130, 135, 145)
CHECKPOINT = (100, 180, 255)

# World objects
TREADMILL = pygame.Rect(520, 470, 300, 190)
UPGRADE_BOX = pygame.Rect(850, 500, 145, 130)
MONEY_BOX = pygame.Rect(1700, 470, 300, 210)

# Road mission: reach the blue checkpoint to unlock the money box.
ROAD_START = pygame.Rect(180, 650, 1250, 150)
ROAD_FINISH = pygame.Rect(1300, 650, 80, 150)
MONEY_UNLOCKED = False

# Game variables
Speed = 200.0
MAX_SPEED = 1200.0
BOOST_RATE = 1.0
UPGRADED_BOOST_RATE = 5.0
TREADMILL_UPGRADED = False

Money_in_box = 0.0
Money_collected = 0.0
MONEY_GENERATION_RATE = 2.0
MONEY_COLLECTION_RATE = 50.0
UPGRADE_COST = 10.0

font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 16)
tiny_font = pygame.font.SysFont("arial", 13)
pygame.mouse.set_visible(False)


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0.0, 0.0
        self.radius = 22
        self.color = (255, 105, 105)
        self.flash = 0.0

    def update(self, dt, mouse_world_x, mouse_world_y):
        global Speed, Money_in_box, Money_collected
        global TREADMILL_UPGRADED, MONEY_UNLOCKED

        mouse_in_treadmill = TREADMILL.collidepoint(mouse_world_x, mouse_world_y)
        player_in_treadmill = TREADMILL.collidepoint(self.x, self.y)
        both_in_treadmill = mouse_in_treadmill and player_in_treadmill

        mouse_in_upgrade = UPGRADE_BOX.collidepoint(mouse_world_x, mouse_world_y)
        player_in_upgrade = UPGRADE_BOX.collidepoint(self.x, self.y)
        both_in_upgrade = mouse_in_upgrade and player_in_upgrade

        player_in_money = MONEY_BOX.collidepoint(self.x, self.y)
        money_available = MONEY_UNLOCKED and player_in_money

        # Buy once when both player and pointer are in the pink upgrade box.
        if both_in_upgrade and not TREADMILL_UPGRADED and Money_collected >= UPGRADE_COST:
            Money_collected -= UPGRADE_COST
            TREADMILL_UPGRADED = True

        # The treadmill increases Speed only while both are inside it.
        if both_in_treadmill:
            rate = UPGRADED_BOOST_RATE if TREADMILL_UPGRADED else BOOST_RATE
            Speed = min(MAX_SPEED, Speed + rate * dt)
            self.color = (145, 255, 165) if not TREADMILL_UPGRADED else (120, 255, 220)
            self.flash = 0.2
        elif player_in_money:
            self.color = (255, 240, 100)
        elif both_in_upgrade:
            self.color = (255, 150, 200)
        else:
            self.color = (255, 105, 105)
            self.flash = max(0.0, self.flash - dt)

        # Money is generated everywhere except while the player is in the yellow box.
        if MONEY_UNLOCKED and not player_in_money:
            Money_in_box += MONEY_GENERATION_RATE * dt

        # The player collects money while inside the yellow box.
        if money_available and Money_in_box > 0:
            collected = min(MONEY_COLLECTION_RATE * dt, Money_in_box)
            Money_in_box -= collected
            Money_collected += collected

        # Reaching the blue road checkpoint unlocks the money box.
        if ROAD_FINISH.collidepoint(self.x, self.y):
            MONEY_UNLOCKED = True

        dx, dy = mouse_world_x - self.x, mouse_world_y - self.y
        distance = math.hypot(dx, dy)

        # When the mouse is in the treadmill, the player stops moving.
        # Speed still increases if the player is also inside it.
        if mouse_in_treadmill:
            self.vx *= 0.72
            self.vy *= 0.72
        elif distance > 1:
            desired_vx = dx / distance * Speed
            desired_vy = dy / distance * Speed
            self.vx += (desired_vx - self.vx) * min(1.0, 8.0 * dt)
            self.vy += (desired_vy - self.vy) * min(1.0, 8.0 * dt)

        current_velocity = math.hypot(self.vx, self.vy)
        if current_velocity > MAX_SPEED:
            scale = MAX_SPEED / current_velocity
            self.vx *= scale
            self.vy *= scale

        self.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.x + self.vx * dt))
        self.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.y + self.vy * dt))

    def draw(self, surface, camera_x, camera_y):
        x, y = int(self.x - camera_x), int(self.y - camera_y)
        pygame.draw.circle(surface, (0, 0, 0), (x + 5, y + 7), self.radius)
        pygame.draw.circle(surface, self.color, (x, y), self.radius)
        pygame.draw.circle(surface, (25, 25, 25), (x + 6, y - 5), 4)
        pygame.draw.arc(surface, (25, 25, 25), (x - 9, y - 5, 18, 18), 0.5, math.pi - 0.5, 2)
        if self.flash > 0:
            pygame.draw.circle(surface, (170, 255, 190), (x, y), self.radius + 12, 2)


particles = []

def add_particles(x, y, color, count=3):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        velocity = random.uniform(20, 130)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * velocity,
            "vy": math.sin(angle) * velocity,
            "life": random.uniform(0.3, 0.8),
            "color": color,
        })


def draw_world_rect(rect, camera_x, camera_y, fill, border, width=2, radius=10):
    visible = rect.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, fill, visible, border_radius=radius)
    pygame.draw.rect(screen, border, visible, width, border_radius=radius)


player = Player(*PLAYER_START)
camera_x = player.x - WIDTH / 2
camera_y = player.y - HEIGHT / 2
running = True

while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # The cursor points into the scrolling world, not directly at the screen origin.
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_world_x = mouse_x + camera_x
    mouse_world_y = mouse_y + camera_y
    player.update(dt, mouse_world_x, mouse_world_y)

    # Camera follows the player, making the map scroll.
    target_camera_x = player.x - WIDTH / 2
    target_camera_y = player.y - HEIGHT / 2
    camera_x += (target_camera_x - camera_x) * min(1.0, CAMERA_SMOOTHING * dt)
    camera_y += (target_camera_y - camera_y) * min(1.0, CAMERA_SMOOTHING * dt)
    camera_x = max(0, min(WORLD_WIDTH - WIDTH, camera_x))
    camera_y = max(0, min(WORLD_HEIGHT - HEIGHT, camera_y))

    if TREADMILL.collidepoint(player.x, player.y) and TREADMILL.collidepoint(mouse_world_x, mouse_world_y):
        add_particles(player.x, player.y, SUPER_GREEN if TREADMILL_UPGRADED else (120, 255, 140))
    if MONEY_UNLOCKED and MONEY_BOX.collidepoint(player.x, player.y):
        add_particles(player.x, player.y, YELLOW)

    for particle in particles[:]:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["life"] -= dt
        if particle["life"] <= 0:
            particles.remove(particle)

    screen.fill(BG)

    # Scrolling grid
    grid_start_x = -int(camera_x) % 60
    grid_start_y = -int(camera_y) % 60
    for x in range(grid_start_x, WIDTH, 60):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(grid_start_y, HEIGHT, 60):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

    # Road and its finish checkpoint
    road = ROAD_START.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, ROAD, road)
    for stripe_x in range(road.left + 20, road.right, 70):
        pygame.draw.line(screen, ROAD_EDGE, (stripe_x, road.centery), (stripe_x + 35, road.centery), 4)
    finish = ROAD_FINISH.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, CHECKPOINT, finish)
    pygame.draw.rect(screen, WHITE, finish, 3)
    screen.blit(small_font.render("FINISH ROAD", True, WHITE), (finish.x - 5, finish.y - 28))

    # Treadmill appearance changes after buying upgrade.
    treadmill_fill = SUPER_GREEN if TREADMILL_UPGRADED else GREEN
    treadmill_border = SUPER_DARK if TREADMILL_UPGRADED else GREEN_DARK
    draw_world_rect(TREADMILL, camera_x, camera_y, treadmill_fill, treadmill_border, 4)
    treadmill_screen = TREADMILL.move(-int(camera_x), -int(camera_y))
    title = "SUPER TREADMILL" if TREADMILL_UPGRADED else "TREADMILL"
    rate = 5 if TREADMILL_UPGRADED else 1
    screen.blit(font.render(title, True, WHITE), (treadmill_screen.x + 30, treadmill_screen.y + 30))
    screen.blit(small_font.render(f"+{rate} Speed/s", True, WHITE), (treadmill_screen.x + 78, treadmill_screen.y + 65))
    for stripe_x in range(treadmill_screen.x + 20, treadmill_screen.right - 20, 45):
        pygame.draw.line(screen, WHITE, (stripe_x, treadmill_screen.y + 125), (stripe_x + 20, treadmill_screen.y + 105), 3)

    # Upgrade box
    draw_world_rect(UPGRADE_BOX, camera_x, camera_y, PINK, PINK_DARK, 3)
    upgrade_screen = UPGRADE_BOX.move(-int(camera_x), -int(camera_y))
    upgrade_text = "BOUGHT!" if TREADMILL_UPGRADED else "UPGRADE"
    screen.blit(small_font.render(upgrade_text, True, WHITE), (upgrade_screen.x + 25, upgrade_screen.y + 25))
    if not TREADMILL_UPGRADED:
        screen.blit(small_font.render("Cost: $10", True, WHITE), (upgrade_screen.x + 25, upgrade_screen.y + 58))

    # Money box is hidden until the road mission is complete.
    if MONEY_UNLOCKED:
        draw_world_rect(MONEY_BOX, camera_x, camera_y, YELLOW, YELLOW_DARK, 4)
        money_screen = MONEY_BOX.move(-int(camera_x), -int(camera_y))
        screen.blit(font.render("MONEY BOX", True, (45, 45, 25)), (money_screen.x + 55, money_screen.y + 25))
        screen.blit(small_font.render(f"Inside: ${Money_in_box:.0f}", True, (45, 45, 25)), (money_screen.x + 75, money_screen.y + 65))
        screen.blit(tiny_font.render("Player inside = collect", True, (45, 45, 25)), (money_screen.x + 65, money_screen.y + 98))
    else:
        instruction = font.render("Follow the road to the blue FINISH to unlock the Money Box!", True, TEXT)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 22))

    for particle in particles:
        pygame.draw.circle(screen, particle["color"], (int(particle["x"] - camera_x), int(particle["y"] - camera_y)), 4)

    player.draw(screen, camera_x, camera_y)

    # Fixed HUD and mouse cursor
    pygame.draw.line(screen, GOLD, (mouse_x - 8, mouse_y), (mouse_x + 8, mouse_y), 2)
    pygame.draw.line(screen, GOLD, (mouse_x, mouse_y - 8), (mouse_x, mouse_y + 8), 2)
    pygame.draw.circle(screen, GOLD, (mouse_x, mouse_y), 5, 1)
    screen.blit(font.render(f"Speed: {Speed:.0f}", True, GOLD), (20, 18))
    screen.blit(font.render(f"Collected: ${Money_collected:.1f}", True, YELLOW), (20, 48))
    screen.blit(small_font.render("Reach the blue checkpoint. Mouse in treadmill = stop; both inside = boost.", True, TEXT), (20, HEIGHT - 28))

    pygame.display.flip()

pygame.quit()
