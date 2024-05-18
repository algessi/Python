import pygame
import os
import random
pygame.font.init()

# Screen setup
WIDTH, HEIGHT = 1000, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Call Of Space")

# Load assets
ASSET_DIR = os.path.join(os.path.dirname(__file__), "Assets")

EXPLOSION_IMAGE = pygame.image.load(os.path.join(ASSET_DIR, "Explosion.png"))

SHIP_COLORS = {
    "red": "pixel_ship_red_small.png",
    "green": "pixel_ship_green_small.png",
    "blue": "pixel_ship_blue_small.png",
}
LASER_COLORS = {
    "red": "pixel_laser_red.png",
    "green": "pixel_laser_green.png",
    "blue": "pixel_laser_blue.png",
    "yellow": "pixel_laser_yellow.png",
}

BG_IMAGE = "MultiGalaxy.jpg"
BG = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, BG_IMAGE)), (WIDTH, HEIGHT))
    
# Fonts
MAIN_FONT = pygame.font.SysFont("Arial", 50)
LOST_FONT = pygame.font.SysFont("comicsans", 60)

# Constants
FPS = 60
PLAYER_HEALTH = 100
ENEMY_HEALTH = 100
COOLDOWN = 30
PLAYER_VELOCITY = 5
LASER_VELOCITY = 5
ENEMY_VELOCITY = 1
WAVE_LENGTH = 5
MAX_LIVES = 5

# Laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (0 <= self.y <= height)

    def collision(self, obj):
        return collide(self, obj)


# Ship class
class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


# Player class
class Player(Ship):
    def __init__(self, x, y, health=PLAYER_HEALTH):
        super().__init__(x, y, health)
        self.ship_img = pygame.image.load(os.path.join(ASSET_DIR, "SpaceShip.png"))
        self.laser_img = pygame.image.load(os.path.join(ASSET_DIR, "pixel_laser_yellow.png"))
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 5, self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 5,
                                               self.ship_img.get_width() * (self.health / self.max_health), 5))


# Enemy class
class Enemy(Ship):
    def __init__(self, x, y, color, health=ENEMY_HEALTH):
        super().__init__(x, y, health)
        self.ship_img = pygame.image.load(os.path.join(ASSET_DIR, SHIP_COLORS[color]))
        self.laser_img = pygame.image.load(os.path.join(ASSET_DIR, LASER_COLORS[color]))
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#Explosion Class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.Explosion_img = pygame.transform.scale(EXPLOSION_IMAGE, (70, 50)) 
        self.timer = 0 

    def draw(self, window):
        window.blit(self.Explosion_img, (self.x, self.y))

# Collision detection function
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


# Main game loop
def main():
    player = Player(450, 700)
    enemies = []
    lives = MAX_LIVES
    level = 0
    lost = False
    lost_count = 0

    explosions = []

    clock = pygame.time.Clock()

    bg_y = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        for explosion in explosions:
            explosion.draw(WIN)
        WIN.blit(BG, (0, bg_y))
        WIN.blit(BG, (0, bg_y - HEIGHT))
        lives_label = MAIN_FONT.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = MAIN_FONT.render(f"Level: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
   
    for enemy in enemies:
        enemy.draw(WIN)

    player.draw(WIN)

    if lost:
        lost_label = LOST_FONT.render("You Lost!!", 1, (255, 255, 255))
        WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

    pygame.display.update()


    # Game initialization
    run = True
    while run:
        clock.tick(FPS)
        redraw_window()

        bg_y += 0.5  # Adjust this value to control scrolling speed
        if bg_y >= HEIGHT:
            bg_y = 0



        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            for _ in range(WAVE_LENGTH):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - PLAYER_VELOCITY > 0:  # left
            player.x -= PLAYER_VELOCITY
        if keys[pygame.K_d] and player.x + PLAYER_VELOCITY + player.get_width() < WIDTH:  # right
            player.x += PLAYER_VELOCITY
        if keys[pygame.K_w] and player.y - PLAYER_VELOCITY > 0:  # up
            player.y -= PLAYER_VELOCITY
        if keys[pygame.K_s] and player.y + PLAYER_VELOCITY + player.get_height() + 15 < HEIGHT:  # down
            player.y += PLAYER_VELOCITY
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(ENEMY_VELOCITY)
            enemy.move_lasers(LASER_VELOCITY, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                explosions.append(Explosion(enemy.x, enemy.y))
                
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-LASER_VELOCITY, enemies)

        # Update and remove explosions
        for explosion in explosions[:]:
            explosion.timer += 1
            if explosion.timer >= FPS:  # Adjust the duration of the explosion
                explosions.remove(explosion)

# Main menu function
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


# Entry point
if __name__ == "__main__":
    main_menu()