import pygame
import random
import sys

# Initialize
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Invasion: Refined")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Courier", 18)

# Load assets
PLAYER_IMG = pygame.transform.scale(pygame.image.load("player.png"), (50, 50))
ALIEN_IMG = pygame.transform.scale(pygame.image.load("alien.png"), (40, 40))
LASER_SOUND = pygame.mixer.Sound("laser.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")
POWERUP_SOUND = pygame.mixer.Sound("powerup.wav")

# Game State
score = 0
lives = 3
game_over = False

# Sprite Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.speed = 6
        self.power = None
        self.power_time = 0

    def update(self, keys):
        if not game_over:
            if keys[pygame.K_LEFT]: self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]: self.rect.x += self.speed
            self.rect.clamp_ip(screen.get_rect())
            if self.power and pygame.time.get_ticks() - self.power_time > 5000:
                self.power = None

    def shoot(self):
        if game_over: return
        offsets = [-10, 10] if self.power == "double" else [0]
        for dx in offsets:
            b = Bullet(self.rect.centerx + dx, self.rect.top)
            all_sprites.add(b)
            bullets.add(b)
        LASER_SOUND.play()

    def set_power(self, kind):
        self.power = kind
        self.power_time = pygame.time.get_ticks()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -7

    def update(self, *args):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ALIEN_IMG
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), -30))
        self.speedy = 0.6
        self.health = 2

    def update(self, *args):
        global lives, game_over
        if not game_over:
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT:
                self.kill()
                lives -= 1
                if lives <= 0:
                    end_game()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.effect = random.choice(["double", "shield"])
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 105, 180))
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), -20))
        self.speedy = 3

    def update(self, *args):
        if not game_over:
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT:
                self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=center)
        self.timer = 12

    def update(self, *args):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# Groups
all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Timers
ALIEN_EVENT = pygame.USEREVENT + 1
POWER_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ALIEN_EVENT, 1500)
pygame.time.set_timer(POWER_EVENT, 10000)

def end_game():
    global game_over
    game_over = True
    pygame.time.set_timer(ALIEN_EVENT, 0)
    pygame.time.set_timer(POWER_EVENT, 0)

# Main loop
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: player.shoot()
            if event.key == pygame.K_ESCAPE and game_over: running = False
        if event.type == ALIEN_EVENT:
            a = Alien()
            all_sprites.add(a)
            aliens.add(a)
        if event.type == POWER_EVENT:
            p = PowerUp()
            all_sprites.add(p)
            powerups.add(p)

    all_sprites.update(keys)

    # Bullet–alien collisions
    for bullet in bullets.copy():
        for alien in aliens.copy():
            if bullet.rect.colliderect(alien.rect):
                bullet.kill()
                alien.health -= 1
                if alien.health <= 0:
                    EXPLOSION_SOUND.play()
                    explosion = Explosion(alien.rect.center)
                    all_sprites.add(explosion)
                    explosions.add(explosion)
                    alien.kill()
                    score += 10

    # PowerUp collision
    for pu in powerups.copy():
        if player.rect.colliderect(pu.rect):
            POWERUP_SOUND.play()
            player.set_power(pu.effect)
            pu.kill()

    # Drawing
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    hud = FONT.render(f"Score: {score}  Lives: {lives}  Power: {player.power or 'None'}", True, WHITE)
    screen.blit(hud, (10, 10))
    if game_over:
        over = FONT.render("GAME OVER - Press Esc to Exit", True, (255, 50, 50))
        screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

pygame.quit()
sys.exit()