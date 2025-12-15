import pygame
import random
import math

# =====================
# CONFIGURATION
# =====================
WIDTH, HEIGHT = 900, 600
NUM_ANTS = 80
PHEROMONE_DECAY = 0.008
PHEROMONE_STRENGTH = 1.0
ANT_SPEED = 4

NEST_POS = (150, 300)
FOOD_POS = (750, 300)
FOOD_RADIUS = 20
NEST_RADIUS = 20

GRID_SIZE = 5
GRID_W = WIDTH // GRID_SIZE
GRID_H = HEIGHT // GRID_SIZE

# =====================
# INITIALIZATION
# =====================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony Optimization Simulation")
clock = pygame.time.Clock()

pheromones = [[0.0 for _ in range(GRID_H)] for _ in range(GRID_W)]


# =====================
# ANT CLASS
# =====================
class Ant:
    def __init__(self):
        self.x, self.y = NEST_POS
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False

    def move(self):
        # Sense pheromones
        self.angle += random.uniform(-0.3, 0.3)

        dx = math.cos(self.angle)
        dy = math.sin(self.angle)

        self.x += dx * ANT_SPEED
        self.y += dy * ANT_SPEED

        # Keep inside window
        self.x = max(0, min(WIDTH - 1, self.x))
        self.y = max(0, min(HEIGHT - 1, self.y))

    def deposit_pheromone(self):
        gx = int(self.x // GRID_SIZE)
        gy = int(self.y // GRID_SIZE)
        pheromones[gx][gy] += PHEROMONE_STRENGTH

    def check_food(self):
        if not self.has_food:
            if distance(self.x, self.y, *FOOD_POS) < FOOD_RADIUS:
                self.has_food = True
                self.angle += math.pi

    def check_nest(self):
        if self.has_food:
            if distance(self.x, self.y, *NEST_POS) < NEST_RADIUS:
                self.has_food = False
                self.angle += math.pi

    def update(self):
        self.move()
        self.deposit_pheromone()
        self.check_food()
        self.check_nest()

    def draw(self):
        color = (255, 0, 0) if self.has_food else (0, 0, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)


# =====================
# UTILITY FUNCTIONS
# =====================
def distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


def evaporate_pheromones():
    for x in range(GRID_W):
        for y in range(GRID_H):
            pheromones[x][y] *= (1 - PHEROMONE_DECAY)


def draw_pheromones():
    for x in range(GRID_W):
        for y in range(GRID_H):
            value = pheromones[x][y]
            if value > 0.1:
                intensity = min(255, int(value * 5))
                color = (0, intensity, 255)
                rect = pygame.Rect(
                    x * GRID_SIZE,
                    y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )
                pygame.draw.rect(screen, color, rect)


# =====================
# MAIN LOOP
# =====================
ants = [Ant() for _ in range(NUM_ANTS)]
running = True

while running:
    clock.tick(60)
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    evaporate_pheromones()
    draw_pheromones()

    for ant in ants:
        ant.update()
        ant.draw()

    # Draw nest and food
    pygame.draw.circle(screen, (0, 200, 0), FOOD_POS, FOOD_RADIUS)
    pygame.draw.circle(screen, (150, 75, 0), NEST_POS, NEST_RADIUS)

    pygame.display.flip()

pygame.quit()
