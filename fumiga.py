import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

# =======================
# PARÂMETROS
# =======================
NUM_NODES = 30
CONNECTIVITY = 0.25

NUM_ANTS = 100
NUM_ITERATIONS = 200

PHEROMONE_INIT = 0.1
PHEROMONE_DEPOSIT = 1.0
PHEROMONE_EVAPORATION = 0.02

ALPHA = 1.5
BETA = 1.0

EDGE_TRAVEL_TIME = 0.1

ANT_SPEED_MULTIPLIER = 5.0   # <<< CONTROLE DE VELOCIDADE

ANT_RADIUS = 5
NODE_RADIUS = 8

EDGE_WIDTH_MIN = 2.0
EDGE_WIDTH_MAX = 15.0

ANTHILL = 0
FOOD = 1


# =======================
# DESENHO
# =======================
def draw_circle(x, y, r, color):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(0, 361, 10):
        a = math.radians(i)
        glVertex2f(x + math.cos(a) * r, y + math.sin(a) * r)
    glEnd()


def draw_line(p1, p2, color):
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex2f(*p1)
    glVertex2f(*p2)
    glEnd()


def draw_grid(w, h, step=50):
    glColor3f(0.6, 0.6, 0.6)
    glBegin(GL_LINES)
    for x in range(0, w, step):
        glVertex2f(x, 0)
        glVertex2f(x, h)
    for y in range(0, h, step):
        glVertex2f(0, y)
        glVertex2f(w, y)
    glEnd()


# =======================
# GRAFO
# =======================
def generate_graph(n, conn, w, h):
    nodes = [(random.randint(50, w-50), random.randint(50, h-50)) for _ in range(n)]
    edges = {}
    dist = {}

    for i in range(1, n):
        j = random.randint(0, i-1)
        edges[(i, j)] = edges[(j, i)] = PHEROMONE_INIT

    for i in range(n):
        for j in range(i+1, n):
            if random.random() < conn:
                edges[(i, j)] = edges[(j, i)] = PHEROMONE_INIT

    for (i, j) in edges:
        dx = nodes[i][0] - nodes[j][0]
        dy = nodes[i][1] - nodes[j][1]
        dist[(i, j)] = math.hypot(dx, dy)

    return nodes, edges, dist


# =======================
# ACO
# =======================
def choose_next(cur, visited, edges, dist):
    options = []
    total = 0
    for (i, j), pher in edges.items():
        if i == cur and j not in visited:
            w = (pher ** ALPHA) * ((1 / dist[(i, j)]) ** BETA)
            options.append((j, w))
            total += w

    if not options:
        return None

    r = random.uniform(0, total)
    acc = 0
    for node, w in options:
        acc += w
        if acc >= r:
            return node


def build_path(edges, dist):
    path = [ANTHILL]
    visited = {ANTHILL}
    while path[-1] != FOOD:
        nxt = choose_next(path[-1], visited, edges, dist)
        if nxt is None:
            return None
        path.append(nxt)
        visited.add(nxt)

    return path + list(reversed(path[:-1]))


# =======================
# FORMIGA
# =======================
class Ant:
    def __init__(self, path, nodes):
        self.path = path
        self.nodes = nodes
        self.edge = 0
        self.t = 0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        # >>> IMPLEMENTAÇÃO DA VELOCIDADE GLOBAL <<<
        self.t += dt * ANT_SPEED_MULTIPLIER / EDGE_TRAVEL_TIME

        if self.t >= 1:
            self.t = 0
            self.edge += 1
            if self.edge >= len(self.path) - 1:
                self.finished = True

    def position(self):
        a = self.nodes[self.path[self.edge]]
        b = self.nodes[self.path[self.edge + 1]]
        return (
            a[0] * (1 - self.t) + b[0] * self.t,
            a[1] * (1 - self.t) + b[1] * self.t
        )


# =======================
# MAIN
# =======================
def main():
    pygame.init()
    info = pygame.display.Info()
    w, h = info.current_w, info.current_h

    pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL | FULLSCREEN)

    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)

    nodes, edges, dist = generate_graph(NUM_NODES, CONNECTIVITY, w, h)

    clock = pygame.time.Clock()
    iteration = 0
    ants = []

    running = True
    while running and iteration < NUM_ITERATIONS:
        dt = clock.tick(60) / 1000

        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                running = False

        if not ants:
            for k in edges:
                edges[k] *= (1 - PHEROMONE_EVAPORATION)

            ants = []
            paths = []

            for _ in range(NUM_ANTS):
                p = build_path(edges, dist)
                if p:
                    ants.append(Ant(p, nodes))
                    paths.append(p)

            for p in paths:
                for i in range(len(p)-1):
                    edges[(p[i], p[i+1])] += PHEROMONE_DEPOSIT

            iteration += 1

        for ant in ants:
            ant.update(dt)

        ants = [a for a in ants if not a.finished]

        glClearColor(0.8, 0.8, 0.8, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        draw_grid(w, h)

        max_pher = max(edges.values())
        for (i, j), p in edges.items():
            t = min(p / max_pher, 1)
            width = EDGE_WIDTH_MIN + t * (EDGE_WIDTH_MAX - EDGE_WIDTH_MIN)
            glLineWidth(width)
            draw_line(nodes[i], nodes[j], (t, 0, 1 - t))

        for i, (x, y) in enumerate(nodes):
            if i == ANTHILL:
                draw_circle(x, y, NODE_RADIUS + 3, (1, 0, 0))
            elif i == FOOD:
                draw_circle(x, y, NODE_RADIUS + 3, (0, 0, 1))
            else:
                draw_circle(x, y, NODE_RADIUS, (0, 0, 0))

        for ant in ants:
            x, y = ant.position()
            draw_circle(x, y, ANT_RADIUS, (1, 1, 0))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
