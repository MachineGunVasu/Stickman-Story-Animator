import pygame
import pickle
pygame.init()
pygame.mixer.init()
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
        self.run_frames = [
            pygame.image.load(f"resources/stick_run/stick_run_{i:04d}.png").convert_alpha()
            for i in range(4)
        ]
        self.run_frames = [pygame.transform.scale(img, (60, 50)) for img in self.run_frames] #run animation frames
        self.idle_frame = pygame.image.load("resources/stick_run/stickman.png").convert_alpha() 
        self.idle_frame = pygame.transform.scale(self.idle_frame, (60, 50))

        # Running Animation Variables
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.idle_frame
        # Smaller hitbox
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x + 10, y + 5, 30, 45)
      # smaller than sprite
        self.hitbox.center = self.rect.center
        # Movement
        self.vel_y = 0
        self.on_ground = False
        self.menu = False

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
            self.image = self.idle_frame

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
        for rect in world.collision_tiles:
            if self.hitbox.colliderect(rect):
                if dx > 0:
                    self.hitbox.right = rect.left
                elif dx < 0:
                    self.hitbox.left = rect.right

        # --- Vertical Collision ---
        self.hitbox.y += dy
        self.on_ground = False
        for rect in world.collision_tiles:
            if self.hitbox.colliderect(rect):
                if dy > 0:  # falling
                    self.hitbox.bottom = rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0:  # jumping
                    self.hitbox.top = rect.bottom
                    self.vel_y = 0
        # --- Check for deadly tile collision (Game Over) ---
        for hitbox in world.deadly_tiles:
            if self.hitbox.colliderect(hitbox):
                self.menu=True  # Placeholder for game over logic


        # Update sprite position to hitbox
        self.rect.topleft = (self.hitbox.x - 10, self.hitbox.y - 5)

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
        self.deadly_tiles = []
        platform_img = pygame.image.load("resources/pebble_brown_1_old.png").convert_alpha()
        spike_img = pygame.image.load("resources/spike.png").convert_alpha()
        gate_animation = [
            pygame.image.load(f"resources/gate{i}.png").convert_alpha()
            for i in range(1)
        ] 
        gate_img = pygame.transform.scale(gate_animation[0], (50, 50))
        self.gate_open = False
        self.gate_rect = None
        # Store spawn position
        self.spawn_x = 60
        self.spawn_y = HEIGHT - 50 - 50
        
        for row_index, row in enumerate(data):
            for col_index, tile in enumerate(row):
                x, y = col_index * 50, row_index * 50
                if tile == 1: # platform
                    img = pygame.transform.scale(platform_img, (50, 50))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                    self.collision_tiles.append(rect)
                if tile == 2: # deadly spike
                    img = pygame.transform.scale(spike_img, (50, 50))
                    rect = img.get_rect(topleft=(x, y))
                    deadly_hitbox = pygame.Rect(rect.x, rect.y + 19, 50, 25)
                    self.tile_list.append((img, rect))
                    self.deadly_tiles.append(deadly_hitbox)
                if tile == 8: #gate
                    self.gate_rect = pygame.Rect(x, y, 50, 50)
                if tile == 9: #spawn point
                    self.spawn_x = x
                    self.spawn_y = y-50


    def draw(self,player):
        bg_img = pygame.image.load("resources/bg/bg-1.png").convert_alpha()
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        screen.blit(bg_img, (0,0))
        #draw tiles
        for img, rect in self.tile_list:
            screen.blit(img, rect) 
        # Draw gate
        if self.gate_rect is not None:
            if self.gate_open:
                gate_img = pygame.image.load("resources/gate1.png").convert_alpha()
            else:
                gate_img = pygame.image.load("resources/gate0.png").convert_alpha()
            gate_img = pygame.transform.scale(gate_img, (50, 50))
            screen.blit(gate_img, self.gate_rect.topleft)
            # Check if player reached the gate
            if player.hitbox.colliderect(self.gate_rect):
                self.gate_open = True

#--- Level Manager Class ---
class Levels():
    def __init__(self):
        self.levels = []
        self.curr = 0
        self.load_level()

    def load_level(self):
        levels=["levels/level1_data","levels/level2_data"]
        for level in levels:
            with open(level, "rb") as f:
                data = pickle.load(f)
                self.levels.append(data)
    
    def current_level(self):
        if len(self.levels) > self.curr:
            return self.levels[self.curr]   
    
    def next_level(self):
        self.curr += 1
        if len(self.levels) > self.curr:
            return self.levels[self.curr]
        else:
            return None
    
    def reset_levels(self):
        self.curr = 0

    def get_current_level_number(self):
        return self.curr + 1
    
#FUNCTIONS
def showHitboxes():  #show hitboxes and rect for debugging
    for hitbox in world.deadly_tiles:
            pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)
    for img,rect in world.tile_list:
            pygame.draw.rect(screen, (255, 0, 255), rect, 1)
    pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2)
    pygame.draw.rect(screen, (0, 255, 0), player.rect, 2)
def drawGrid(): #show grid lines
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, GREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, GREY, (0, y), (WIDTH, y))

def start_menu():   #start menu before game begins
    menu_bg = pygame.image.load("resources/pixelated_start.png").convert_alpha()
    menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
    font = pygame.font.Font("resources/MagicSchoolOne.ttf", 50)
    menu_running = True
    while menu_running:
        screen.blit(menu_bg, (0, 0))
        title = font.render("Press any key to start...", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT - 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return True  # Start the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Start on any mouse click
                return True
        
        pygame.display.update()
        clock.tick(60)

def game_over_menu():    #game over menu when player hits deadly tile
    font_big = pygame.font.Font("resources/MagicSchoolOne.ttf", 60)
    font_small = pygame.font.Font("resources/MagicSchoolOne.ttf", 50)

    # Buttons (Rectangles)
    restart_btn = pygame.Rect(WIDTH // 2 - 100, (HEIGHT // 2)-30, 200, 60)
    exit_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 60)
    menu_bg = pygame.image.load("resources/menu1.png").convert_alpha()
    menu_bg = pygame.transform.scale(menu_bg, (500, 300))
    while True:
        # Background overlay
        screen.blit(menu_bg, (WIDTH // 2 - 250, HEIGHT // 2 - 150))
        
        # Title
        title = font_big.render("GAME OVER", True, ( 255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))

        # Mouse position
        mx, my = pygame.mouse.get_pos()

        # Button colors (hover effect)
        restart_color = (0, 200, 0) if restart_btn.collidepoint(mx, my) else (0, 120, 0)
        exit_color = (200, 0, 0) if exit_btn.collidepoint(mx, my) else (120, 0, 0)

        pygame.draw.rect(screen, restart_color, restart_btn, border_radius=8)
        pygame.draw.rect(screen, exit_color, exit_btn, border_radius=8)

        # Button text - PROPERLY CENTERED
        restart_text = font_small.render("RESTART", True, WHITE)
        exit_text = font_small.render("EXIT", True, WHITE)

        # Center text both horizontally and vertically
        screen.blit(restart_text, (
            restart_btn.centerx - restart_text.get_width() // 2,
            restart_btn.centery - restart_text.get_height() // 2
        ))
        screen.blit(exit_text, (
            exit_btn.centerx - exit_text.get_width() // 2,
            exit_btn.centery - exit_text.get_height() // 2
        ))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.collidepoint(mx, my):
                    return "restart"
                elif exit_btn.collidepoint(mx, my):
                    pygame.quit()
                    exit()

def win(total_levels):    #win menu when all levels are completed
    font_big = pygame.font.Font("resources/MagicSchoolOne.ttf", 80)
    font_small = pygame.font.Font("resources/MagicSchoolOne.ttf", 50)
    font_tiny = pygame.font.Font("resources/MagicSchoolOne.ttf", 30)
    menu_bg = pygame.image.load("resources/menu1.png").convert_alpha()
    menu_bg = pygame.transform.scale(menu_bg, (500, 300))

    while True:
        # Background overlay
        screen.blit(menu_bg, (WIDTH // 2 - 250, HEIGHT // 2 - 150))
        
        # Title and message
        title = font_big.render("YOU WIN!", True, (50, 255, 50))
        congrats = font_tiny.render(f"Completed all {total_levels} levels!", True, (255, 255, 255))
        prompt = font_small.render("Press ENTER", True, (255, 255, 255))

        # Draw text
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
        screen.blit(congrats, (WIDTH // 2 - congrats.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.quit()
                    exit()


# --- MAIN PROGRAM ---
pygame.mixer.music.load("resources/music/bg.mp3")
pygame.mixer.music.play(-1)  
start_menu()
level=Levels()   
level_data = level.current_level()  #load first level
world = World(level_data)  #--- Create world ---
player = Player(world.spawn_x, world.spawn_y)
player_group = pygame.sprite.Group(player)  #--- Create player---
# --- Game Loop ---
run = True
while run:
    clock.tick(60)
    screen.fill((0,0,0))
    for event in pygame.event.get():      #exit game
        if event.type == pygame.QUIT:
            run = False
    # Draw world & update player
    world.draw(player)
    player.update(world)
    player_group.draw(screen)
    #showHitboxes()  
    #drawGrid()
    # Check for game over
    if (player.menu):
        choice = game_over_menu()
        if choice == "restart":
            # Reset player and world here
            world = World(level.current_level())
            player = Player(world.spawn_x, world.spawn_y)
            player_group = pygame.sprite.Group(player)
            player.menu = False
            continue  # go back to loop
        else:
            run = False
    # Check for level completion    
    if abs(player.hitbox.centerx - world.gate_rect.centerx) < 10 and world.gate_open: 
        if level.next_level():
            current_level = level.current_level()   
            world = World(current_level)
            player = Player(world.spawn_x, world.spawn_y)
            player_group = pygame.sprite.Group(player)
        else:
            win(len(level.levels))
            run = False
    pygame.display.update()
print(world.gate_rect)

pygame.quit()
