import pygame
import pickle
pygame.init()

# --- Window ---
WIDTH, HEIGHT = 900, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman: Echo of Time")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
GREY = (100, 100, 100)

# --- Game Variables ---
gravity = 0.8
player_speed = 3
jump_force = 10

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load running frames
        self.run_frames = [
            pygame.image.load(f"resources/stick_run/stick_run_{i:04d}.png").convert_alpha()
            for i in range(3)
        ]
        self.run_frames = [pygame.transform.scale(img, (50, 50)) for img in self.run_frames]

        # Animation
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.run_frames[0]

        # Smaller hitbox
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x + 10, y + 5, 30, 45)  # smaller than sprite
        # Movement
        self.vel_y = 0
        self.on_ground = False

    def update(self, world):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Horizontal movement
        if keys[pygame.K_RIGHT]:
            dx = player_speed
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            self.image = self.run_frames[int(self.frame_index)]
        elif keys[pygame.K_LEFT]:
            dx = -player_speed
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            self.image = pygame.transform.flip(self.run_frames[int(self.frame_index)], True, False)
        else:
            self.frame_index = 0
            self.image = self.run_frames[0]

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -jump_force
            self.on_ground = False

        # Gravity
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10
        dy = self.vel_y

        # --- Horizontal Collision ---
        self.hitbox.x += dx
        for img,rect in world.tile_list:
            if self.hitbox.colliderect(rect):
                if dx > 0:
                    self.hitbox.right = rect.left
                elif dx < 0:
                    self.hitbox.left = rect.right

        # --- Vertical Collision ---
        self.hitbox.y += dy
        self.on_ground = False
        for img,rect in world.tile_list:
            if self.hitbox.colliderect(rect):
                if dy > 0:  # falling
                    self.hitbox.bottom = rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0:  # jumping
                    self.hitbox.top = rect.bottom
                    self.vel_y = 0

        # Update sprite position to hitbox
        self.rect.topleft = (self.hitbox.x - 10, self.hitbox.y - 5)
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)  # Draw hitbox for debugging
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)  # Draw sprite rect for debugging
        # Screen boundaries
        if self.hitbox.left < 0:
            self.hitbox.left = 0
        if self.hitbox.right > WIDTH:
            self.hitbox.right = WIDTH

# --- World Class ---
class World():
    def __init__(self, data):
        self.tile_list = []
        self.collision_tiles = []

        platform_img = pygame.image.load("resources/pebble_brown_1_old.png").convert_alpha()

        for row_index, row in enumerate(data):
            for col_index, tile in enumerate(row):
                x, y = col_index * 50, row_index * 50
                if tile == 1:
                    img = pygame.transform.scale(platform_img, (50, 50))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))

    def draw(self):
        bg_img = pygame.image.load("resources/bg/bg-1.png").convert_alpha()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        screen.blit(bg_img, (0,0))
        for img, rect in self.tile_list:
            screen.blit(img, rect)
            pygame.draw.rect(screen, (255, 0, 255), rect, 1)  # Draw tile rect for debugging

# --- Grid Helper (Optional) ---
def drawGrid():
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, GREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, GREY, (0, y), (WIDTH, y))

# --- Load Level ---
with open("level1_data", "rb") as f:
    world_data = pickle.load(f)

world = World(world_data)
spawn_x = 60
spawn_y = HEIGHT - 50 - 50  # 50 px above bottom minus sprite height
player = Player(spawn_x, spawn_y)
player_group = pygame.sprite.Group(player)

# --- Game Loop ---
run = True
while run:
    clock.tick(60)
    screen.fill((0,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Draw world & update player
    world.draw()
    player.update(world)
    player_group.draw(screen)

    pygame.display.update()

pygame.quit()
