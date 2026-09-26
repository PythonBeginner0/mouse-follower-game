import math
import random
import pygame

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse Chaser - Road Adventure")
clock = pygame.time.Clock()

# ----------------------------
# Large map and camera
# ----------------------------
WORLD_WIDTH, WORLD_HEIGHT = 1600, 1500
PLAYER_START = (800.0, 1120.0)
CAMERA_SMOOTHING = 5.0

# Colors
BG = (16, 20, 28)
GRID = (38, 47, 60)
WHITE = (255, 255, 255)
TEXT = (235, 235, 235)
GOLD = (255, 210, 80)
ROAD = (78, 82, 94)
ROAD_EDGE = (150, 150, 160)
BLUE_LINE = (60, 140, 255)
GREEN = (70, 210, 105)
GREEN_DARK = (30, 125, 65)
SUPER_GREEN = (0, 245, 165)
SUPER_DARK = (0, 145, 95)
PINK = (245, 95, 155)
PINK_DARK = (155, 45, 95)
YELLOW = (255, 215, 0)
YELLOW_DARK = (170, 135, 0)
UPPER_AREA = (30, 38, 52)

# ----------------------------
# Map layout, arranged like the reference image
# ----------------------------
# The road begins in the lower area and goes upward to the blue finish line.
ROAD = pygame.Rect(700, 720, 200, 420)
FINISH_LINE = pygame.Rect(500, 720, 600, 12)
UPPER_AREA_RECT = pygame.Rect(500, 160, 600, 560)

# The three lower-area boxes sit beside the road.
UPGRADE_BOX = pygame.Rect(380, 940, 150, 115)       # Pink, left
TREADMILL = pygame.Rect(560, 900, 260, 180)         # Green, middle
MONEY_BOX = pygame.Rect(1000, 900, 300, 210)        # Yellow, right
MONEY_UNLOCKED = False

# ----------------------------
# Game variables
# ----------------------------
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

        # Buy the treadmill upgrade once when both player and pointer are in the pink box.
        if both_in_upgrade and not TREADMILL_UPGRADED and Money_collected >= UPGRADE_COST:
            Money_collected -= UPGRADE_COST
            TREADMILL_UPGRADED = True

        # Both player and mouse must be in the treadmill to increase Speed.
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

        # The yellow box only stops making money while the player is inside it.
        if MONEY_UNLOCKED and not player_in_money:
            Money_in_box += MONEY_GENERATION_RATE * dt

        if MONEY_UNLOCKED and player_in_money and Money_in_box > 0:
            collected = min(MONEY_COLLECTION_RATE * dt, Money_in_box)
            Money_in_box -= collected
            Money_collected += collected

        # Finish the road mission by touching the blue line.
        if FINISH_LINE.collidepoint(self.x, self.y):
            MONEY_UNLOCKED = True

        dx = mouse_world_x - self.x
        dy = mouse_world_y - self.y
        distance = math.hypot(dx, dy)

        # If the mouse pointer is in the treadmill, the player stops moving.
        if mouse_in_treadmill:
            self.vx *= 0.72
            self.vy *= 0.72
        elif distance > 1:
            desired_vx = dx / distance * Speed
            desired_vy = dy / distance * Speed
            response = min(1.0, 8.0 * dt)
            self.vx += (desired_vx - self.vx) * response
            self.vy += (desired_vy - self.vy) * response

        velocity = math.hypot(self.vx, self.vy)
        if velocity > MAX_SPEED:
            scale = MAX_SPEED / velocity
            self.vx *= scale
            self.vy *= scale

        self.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.x + self.vx * dt))
        self.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.y + self.vy * dt))

    def draw(self, surface, camera_x, camera_y):
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
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
            "x": x,
            "y": y,
            "vx": math.cos(angle) * velocity,
            "vy": math.sin(angle) * velocity,
            "life": random.uniform(0.3, 0.8),
            "color": color,
        })


def draw_world_rect(rect, camera_x, camera_y, fill, border, width=2, radius=10):
    visible = rect.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, fill, visible, border_radius=radius)
    pygame.draw.rect(screen, border, visible, width, border_radius=radius)


def world_point(point, camera_x, camera_y):
    return int(point[0] - camera_x), int(point[1] - camera_y)


player = Player(*PLAYER_START)
camera_x = player.x - WIDTH / 2
camera_y = player.y - HEIGHT / 2
running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Convert the screen cursor position into a position in the scrolling world.
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_world_x = mouse_x + camera_x
    mouse_world_y = mouse_y + camera_y
    player.update(dt, mouse_world_x, mouse_world_y)

    # Follow the player with the camera.
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

    # Large upper area from the drawing.
    draw_world_rect(UPPER_AREA_RECT, camera_x, camera_y, UPPER_AREA, ROAD_EDGE, 3, 4)
    upper_screen = UPPER_AREA_RECT.move(-int(camera_x), -int(camera_y))
    upper_text = font.render("UPPER AREA", True, ROAD_EDGE)
    screen.blit(upper_text, (upper_screen.centerx - upper_text.get_width() // 2, upper_screen.top + 25))

    # Vertical road and blue finish line.
    road_screen = ROAD.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, ROAD, road_screen)
    pygame.draw.rect(screen, ROAD_EDGE, road_screen, 3)
    for stripe_y in range(road_screen.top + 25, road_screen.bottom, 65):
        pygame.draw.line(screen, ROAD_EDGE, (road_screen.centerx, stripe_y), (road_screen.centerx, stripe_y + 30), 4)

    finish_screen = FINISH_LINE.move(-int(camera_x), -int(camera_y))
    pygame.draw.rect(screen, BLUE_LINE, finish_screen)
    pygame.draw.rect(screen, WHITE, finish_screen, 2)
    finish_label = small_font.render("FINISH TO UNLOCK", True, WHITE)
    screen.blit(finish_label, (finish_screen.centerx - finish_label.get_width() // 2, finish_screen.y - 25))

    # Pink upgrade box on the left.
    draw_world_rect(UPGRADE_BOX, camera_x, camera_y, PINK, PINK_DARK, 3)
    upgrade_screen = UPGRADE_BOX.move(-int(camera_x), -int(camera_y))
    upgrade_text = "BOUGHT!" if TREADMILL_UPGRADED else "UPGRADE"
    screen.blit(small_font.render(upgrade_text, True, WHITE), (upgrade_screen.x + 32, upgrade_screen.y + 24))
    if not TREADMILL_UPGRADED:
        screen.blit(small_font.render("Cost: $10", True, WHITE), (upgrade_screen.x + 32, upgrade_screen.y + 58))

    # Green treadmill in the middle; its appearance changes after upgrading.
    treadmill_fill = SUPER_GREEN if TREADMILL_UPGRADED else GREEN
    treadmill_border = SUPER_DARK if TREADMILL_UPGRADED else GREEN_DARK
    draw_world_rect(TREADMILL, camera_x, camera_y, treadmill_fill, treadmill_border, 4)
    treadmill_screen = TREADMILL.move(-int(camera_x), -int(camera_y))
    title = "SUPER TREADMILL" if TREADMILL_UPGRADED else "TREADMILL"
    rate = 5 if TREADMILL_UPGRADED else 1
    title_surface = font.render(title, True, WHITE)
    screen.blit(title_surface, (treadmill_screen.centerx - title_surface.get_width() // 2, treadmill_screen.y + 28))
    rate_surface = small_font.render(f"+{rate} Speed/s", True, WHITE)
    screen.blit(rate_surface, (treadmill_screen.centerx - rate_surface.get_width() // 2, treadmill_screen.y + 65))
    for stripe_x in range(treadmill_screen.x + 22, treadmill_screen.right - 20, 45):
        pygame.draw.line(screen, WHITE, (stripe_x, treadmill_screen.y + 140), (stripe_x + 20, treadmill_screen.y + 118), 3)

    # Yellow money box is hidden until the blue line is reached.
    if MONEY_UNLOCKED:
        draw_world_rect(MONEY_BOX, camera_x, camera_y, YELLOW, YELLOW_DARK, 4)
        money_screen = MONEY_BOX.move(-int(camera_x), -int(camera_y))
        money_title = font.render("MONEY BOX", True, (45, 45, 25))
        screen.blit(money_title, (money_screen.centerx - money_title.get_width() // 2, money_screen.y + 28))
        money_amount = small_font.render(f"Inside: ${Money_in_box:.0f}", True, (45, 45, 25))
        screen.blit(money_amount, (money_screen.centerx - money_amount.get_width() // 2, money_screen.y + 70))
        screen.blit(tiny_font.render("Player inside = collect", True, (45, 45, 25)), (money_screen.x + 78, money_screen.y + 105))
    else:
        instruction = font.render("Follow the road and touch the blue line to unlock the yellow Money Box!", True, TEXT)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 20))

    for particle in particles:
        px, py = world_point((particle["x"], particle["y"]), camera_x, camera_y)
        pygame.draw.circle(screen, particle["color"], (px, py), 4)

    player.draw(screen, camera_x, camera_y)

    # Fixed HUD and cursor.
    pygame.draw.line(screen, GOLD, (mouse_x - 8, mouse_y), (mouse_x + 8, mouse_y), 2)
    pygame.draw.line(screen, GOLD, (mouse_x, mouse_y - 8), (mouse_x, mouse_y + 8), 2)
    pygame.draw.circle(screen, GOLD, (mouse_x, mouse_y), 5, 1)
    screen.blit(font.render(f"Speed: {Speed:.0f}", True, GOLD), (20, 18))
    screen.blit(font.render(f"Collected: ${Money_collected:.1f}", True, YELLOW), (20, 48))
    screen.blit(small_font.render("Road mission: reach the blue line. Mouse in treadmill = stop; both inside = boost.", True, TEXT), (20, HEIGHT - 28))

    pygame.display.flip()

pygame.quit()
