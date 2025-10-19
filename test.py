import pygame, sys

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman: Echo of Time")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
BLUE = (100, 150, 255)

# --- Game Variables ---
gravity = 0.8
player_speed = 4
jump_force = 9
current_level = 1
font = pygame.font.Font(None, 36)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y): # x , y -> coordinates
        super().__init__()
        self.run_frames = [
            pygame.image.load(f"resources/stick_run/stick_run_{i:04d}.png").convert_alpha()
            #i:04d makes sure i is in the format 0000,0001 etc (format specifier)
            for i in range(3) #3 because no of images is 3
        ]
        #loads images frm stick_run and stores in list self.run_frames
        self.run_frames = [pygame.transform.scale(img, (60, 80)) for img in self.run_frames] #resizes image
        # Animation variables
        self.frame_index = 0
        self.animation_speed = 0.2
        # default char img
        self.image = self.run_frames[0] #sets the first image as default 
        self.rect = self.image.get_rect(topleft=(x, y)) #creates rectangle around char for collision check
         # Movement
        self.vel_y = 0
        self.on_ground = False

    #updates char movemont
    def update(self, platforms):
        keys = pygame.key.get_pressed() #keys store keyboard input (up,left,right etc)
        dx = 0 #dx contains horizontal movement

        # Move and animate right
        if keys[pygame.K_RIGHT]:
            dx = player_speed
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            self.image = self.run_frames[int(self.frame_index)]  

        # Move and animate left
        elif keys[pygame.K_LEFT]:
            dx = -player_speed
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            # Flip image horizontally
            self.image = pygame.transform.flip(self.run_frames[int(self.frame_index)], True, False)

        else:
            # Idle frame
            self.frame_index = 0
            self.image = self.run_frames[0]
        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -jump_force
            self.on_ground = False

        # Gravity
        self.vel_y += gravity
        dy = self.vel_y

         # --- Horizontal Movement ---
        self.rect.x += dx
        for platform in platforms:
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                if dx > 0:  # moving right
                    self.rect.right = platform.rect.left
                elif dx < 0:  # moving left
                    self.rect.left = platform.rect.right
                dx = 0

        # --- Vertical Movement ---
        self.rect.y += dy
        self.on_ground = False
        for platform in platforms:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y > 0:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True
                            
        # Move
        self.rect.x += dx
        self.rect.y += dy

        # Screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

# --- Platform Class ---
# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()  # ✅ Proper initialization
        self.image = pygame.Surface((w, h))
        self.image.fill(GREY)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- Gear Class ---
class Gear(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__() 
        self.image = pygame.image.load("resources/armor.png").convert_alpha()
        self.image=pygame.transform.scale(self.image, (40, 60)) # ✅ Proper initialization
        #self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        #pygame.draw.circle(self.image, (255, 223, 0), (15, 15), 15)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- Level Setup ---
def create_level(level_num):
    platforms = pygame.sprite.Group()
    gears = pygame.sprite.Group()
    dialogues = []
    player_start = (50, HEIGHT - 100)

    if level_num == 1:  # Empty Town
        platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
        platforms.add(Platform(300, 400, 150, 20))
        platforms.add(Platform(600, 350, 150, 20))
        gears.add(Gear(650, 310))
        dialogues = ["Welcome, Ryn...", "Find the first gear to begin your journey."]

    elif level_num == 2:  # Forest of Echoes
        platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
        platforms.add(Platform(200, 380, 100, 20))
        platforms.add(Platform(400, 320, 100, 20))
        platforms.add(Platform(600, 260, 100, 20))
        gears.add(Gear(650, 220))
        dialogues = ["Whispers echo through the trees...", "Find the second gear deep within."]

    elif level_num == 3:  # Underground Factory
        platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
        platforms.add(Platform(200, 380, 100, 20))
        platforms.add(Platform(450, 340, 150, 20))
        platforms.add(Platform(700, 300, 100, 20))
        gears.add(Gear(750, 260))
        dialogues = ["The machines still hum below.", "A broken arm guards your next gear."]

    elif level_num == 4:  # Frozen Mountains
        platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
        platforms.add(Platform(250, 400, 120, 20))
        platforms.add(Platform(500, 340, 120, 20))
        platforms.add(Platform(700, 280, 100, 20))
        gears.add(Gear(750, 240))
        dialogues = ["Cold winds whisper warnings...", "Eliora awaits atop the mountain."]

    elif level_num == 5:  # Clocktower Core
        platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
        platforms.add(Platform(250, 380, 100, 20))
        platforms.add(Platform(500, 300, 100, 20))
        platforms.add(Platform(700, 200, 100, 20))
        gears.add(Gear(750, 160))
        dialogues = ["The final climb...", "Your echo awaits."]

    return platforms, gears, dialogues, player_start

# --- Game Setup ---
platforms, gears, dialogues, player_start = create_level(current_level)
player = Player(*player_start)
player_group = pygame.sprite.Group(player)
dialogue_index = 0
show_dialogue = True
collected_gears = 0

# --- Main Loop ---
while True:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            show_dialogue = False

    # Update
    if not show_dialogue:
        player.update(platforms)

        # Check gear collection
        collected = pygame.sprite.spritecollide(player, gears, True)
        if collected:
            collected_gears += 1
            if collected_gears >= 1 and len(gears) == 0:
                current_level += 1
                if current_level > 5:
                    # --- Ending Selection ---
                    screen.fill(WHITE)
                    end_texts = [
                        "1. Rebirth – Restore Time",
                        "2. Stillness – Stay Frozen",
                        "3. Chaos – End the Cycle"
                    ]
                    for i, txt in enumerate(end_texts):
                        t = font.render(txt, True, BLACK)
                        screen.blit(t, (250, 200 + i * 50))
                    pygame.display.flip()

                    waiting = True
                    while waiting:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if e.type == pygame.KEYDOWN:
                                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                                    waiting = False
                    pygame.quit()
                    sys.exit()

                # Load next level
                platforms, gears, dialogues, player_start = create_level(current_level)
                player.rect.topleft = player_start
                dialogue_index = 0
                show_dialogue = True

    # Draw
    platforms.draw(screen)
    gears.draw(screen)
    player_group.draw(screen)

    # Dialogue box
    if show_dialogue and dialogue_index < len(dialogues):
        pygame.draw.rect(screen, GREY, (50, HEIGHT - 120, WIDTH - 100, 80), border_radius=10)
        text = font.render(dialogues[dialogue_index], True, WHITE)
        screen.blit(text, (70, HEIGHT - 95))
        dialogue_index += 1
        pygame.display.flip()
        pygame.time.delay(1500)
    elif show_dialogue:
        show_dialogue = False

    # HUD
    hud = font.render(f"Gears: {collected_gears} | Level: {current_level}", True, BLACK)
    screen.blit(hud, (20, 20))

    pygame.display.flip()
    clock.tick(60)
