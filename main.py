import pygame
import random
import math
import os

# ---------------- INITIAL SETUP ----------------
pygame.init()

WIDTH, HEIGHT = 1400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swarm PDU Communication Dashboard - Node Failure System")

clock = pygame.time.Clock()

# ---------------- FONTS ----------------
font_main = pygame.font.SysFont("Consolas", 11, bold=True)
font_small = pygame.font.SysFont("Consolas", 10, bold=True)
font_title = pygame.font.SysFont("Consolas", 18, bold=True)

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
GREEN = (57, 255, 20)
RED = (255, 60, 60)
GRAY = (180, 180, 180)

# ---------------- IMAGE LOADER ----------------
def get_robot_asset(name):

    filename = f"{name.lower()}.png"

    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()

            # Resize image
            return pygame.transform.scale(img, (55, 55))

        except:
            return None

    return None

# ---------------- PDU CLASS ----------------
class PDU:

    def __init__(self, source, destination, payload):

        self.header = {
            "source": source,
            "destination": destination,
            "packet_id": random.randint(1000, 9999)
        }

        self.payload = payload

    def get_packet_info(self):

        return f"PDU | {self.header['source']} -> {self.header['destination']} | {self.payload}"

# ---------------- ROBOT CLASS ----------------
class Robot:

    def __init__(self, name, x, y, color):

        self.name = name
        self.pos = [float(x), float(y)]

        self.color = color

        # Load Robot Image
        self.image = get_robot_asset(name)

        self.battery = random.randint(60, 100)
        self.failed = False

        self.target = [random.randint(50, 820), random.randint(50, 650)]

    # ---------------- NODE STATUS ----------------
    def check_status(self):

        if self.battery <= 15:
            self.failed = True

    # ---------------- MOVE ----------------
    def move(self):

        self.check_status()

        if self.failed:
            return

        self.battery -= 0.02

        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]

        dist = math.hypot(dx, dy)

        if dist > 3:

            self.pos[0] += (dx / dist) * 1.5
            self.pos[1] += (dy / dist) * 1.5

        else:

            self.target = [random.randint(50, 820), random.randint(50, 650)]

    # ---------------- DRAW ----------------
    def draw(self):

        x = int(self.pos[0])
        y = int(self.pos[1])

        # FAILED NODE
        if self.failed:

            pygame.draw.circle(screen, RED, (x, y), 30, 3)

        # SHOW ROBOT IMAGE
        elif self.image:

            img_rect = self.image.get_rect(center=(x, y))
            screen.blit(self.image, img_rect)

        # FALLBACK IF IMAGE NOT FOUND
        else:

            pygame.draw.circle(screen, self.color, (x, y), 20)

        # ROBOT NAME
        txt = font_main.render(self.name.upper(), True, (20, 20, 20))

        screen.blit(txt, (x - txt.get_width() // 2, y + 40))

# ---------------- ROBOTS ----------------
robots_data = [

    ("Nova", 200, 200, (100, 149, 237)),
    ("Lyra", 150, 500, (255, 105, 180)),
    ("Vortex", 420, 320, (0, 255, 150)),
    ("Orion", 760, 170, (255, 165, 0)),
    ("Aura", 650, 540, (147, 112, 219)),
    ("Glitch", 350, 580, (255, 60, 60))

]

robots = [Robot(n, x, y, c) for n, x, y, c in robots_data]

# ---------------- LOGS ----------------
message_log = [

    "SYSTEM READY",
    "PDU COMMUNICATION ACTIVE",
    "SWARM NODES ONLINE : 06"

]

# ---------------- PAYLOADS ----------------
payloads = [

    "CCN visualization: Status 100% stable.",
    "AI paper methodology is finalized.",
    "Exchanging positional state via S-RCP.",
    "Distance sensor: Nodes are in range.",
    "Battery level 85% for all swarm units.",
    "Wait, Glitch detected a packet delay!",
    "Visualizing swarm coordination logic."

]

# ---------------- MAIN LOOP ----------------
running = True

while running:

    screen.fill((245, 245, 250))

    # ---------------- SIDEBAR ----------------
    pygame.draw.rect(screen, (12, 14, 20), (900, 0, 500, HEIGHT))
    pygame.draw.line(screen, CYAN, (900, 0), (900, HEIGHT), 3)

    title = font_title.render("PDU NETWORK LOGS", True, CYAN)
    screen.blit(title, (1030, 20))

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ---------------- ROBOT LOGIC ----------------
    for r in robots:

        r.move()

        # NODE FAILURE LOG
        if r.failed:

            fail_msg = f"❌ NODE FAILED : {r.name}"

            if fail_msg not in message_log:
                message_log.append(fail_msg)

        for other in robots:

            if r != other and (not r.failed and not other.failed):

                d = math.hypot(
                    r.pos[0] - other.pos[0],
                    r.pos[1] - other.pos[1]
                )

                # CONNECTION RANGE
                if d < 220:

                    pygame.draw.line(screen, GRAY, r.pos, other.pos, 1)

                    # DISTANCE TEXT
                    dist_txt = font_small.render(
                        f"{int(d)}px",
                        True,
                        (90, 90, 110)
                    )

                    mid_x = (r.pos[0] + other.pos[0]) / 2
                    mid_y = (r.pos[1] + other.pos[1]) / 2

                    screen.blit(dist_txt, (mid_x, mid_y))

                    # RANDOM PDU MESSAGE
                    if random.random() < 0.002:

                        payload = random.choice(payloads)

                        packet = PDU(
                            r.name,
                            other.name,
                            payload
                        )

                        message_log.append(packet.get_packet_info())

                        if len(message_log) > 22:
                            message_log.pop(0)

        r.draw()

    # ---------------- LOG DISPLAY ----------------
    for i, log in enumerate(reversed(message_log)):

        if "FAILED" in log:
            color = RED

        elif "stable" in log.lower():
            color = GREEN

        elif "delay" in log.lower():
            color = RED

        else:
            color = WHITE

        txt = font_main.render(log, True, color)

        screen.blit(txt, (920, 70 + i * 26))

    # ---------------- INFO ----------------
    info1 = font_main.render(
        "HEADER: Source | Destination | Packet ID",
        True,
        WHITE
    )

    info2 = font_main.render(
        "SYSTEM: Swarm + Node Failure Active",
        True,
        WHITE
    )

    screen.blit(info1, (920, 620))
    screen.blit(info2, (920, 645))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()