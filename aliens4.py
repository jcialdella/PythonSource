import pygame
import random
import sys
import math

# --- Initialization ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
FPS = 60
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Invasion")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Courier", 18)

# --- Assets ---
PLAYER_IMG = pygame.transform.scale(pygame.image.load("player.png"), (50, 50))
ALIEN_IMG = pygame.transform.scale(pygame.image.load("alien.png"), (40, 40))
LASER_SOUND = pygame.mixer.Sound("laser.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")
POWERUP_SOUND = pygame.mixer.Sound("powerup.wav")

# --- Starfield ---
class Star:
    def __init__(self, layer):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = layer
        self.speed = 0.2 * layer

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        shade = 180 + self.radius * 20
        pygame.draw.circle(surface, (shade, shade, shade), (int(self.x), int(self.y)), self.radius)

stars = [Star(random.choice([1, 2, 3])) for _ in range(100)]

# --- Game State ---
score = 0
lives = 3
game_over = False

# --- Sprites ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        self.speed = 6
        self.power = None
        self.power_time = 0

    def update(self, keys):
        if game_over: return
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

    def set_power(self, effect):
        self.power = effect
        self.power_time = pygame.time.get_ticks()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, offset=0):
        super().__init__()
        self.image = ALIEN_IMG
        self.orig_x = x
        self.rect = self.image.get_rect(center=(x, y))
        self.wave_offset = offset
        self.health = 2

    def update(self, *args):
        if game_over: return
        t = pygame.time.get_ticks() / 500 + self.wave_offset
        self.rect.x = self.orig_x + 20 * math.sin(t)
        self.rect.y += 0.3 + 0.2 * math.sin(t * 0.7)
        if self.rect.top > HEIGHT:
            self.kill()
            global lives
            lives -= 1
            if lives <= 0: end_game()

class BossAlien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((80, 60))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -60))
        self.health = 20
        self.speed = 1.5             # ⏩ faster horizontal movement
        self.fall_speed = 0.6        # ⏬ slightly faster vertical descent
        self.direction = 1
        self.spawn_time = pygame.time.get_ticks()  # 🕒 used for timeout

    def update(self, *args):
        if game_over:
            return

        self.rect.y += self.fall_speed
        self.rect.x += self.speed * self.direction

        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

        # 💣 Auto-despawn after 15 seconds if not destroyed
        if pygame.time.get_ticks() - self.spawn_time > 15000:
            print("👻 Boss auto-despawned")
            self.kill()

        # 🚨 Failsafe: if boss drifts off bottom
        if self.rect.top > HEIGHT:
            self.kill()
            global lives
            lives -= 3
            if lives <= 0:
                end_game()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=center)
        self.timer = 10

    def update(self, *args):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.effect = random.choice(["double", "shield"])
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 105, 180))
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), -20))
        self.speed = 3

    def update(self, *args):
        if game_over: return
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# --- WaveManager ---
class WaveManager:
    def __init__(self):
        self.next_wave_time = pygame.time.get_ticks() + 2000
        self.wave_count = 0
        self.formations = [
            [[1, 0, 1, 0, 1],
             [0, 1, 0, 1, 0]],
            [[1, 1, 1, 1, 1],
             [0, 1, 1, 1, 0]],
            [[0, 0, 1, 0, 0],
             [0, 1, 1, 1, 0],
             [1, 1, 1, 1, 1]]
        ]

    def update(self):
        if game_over:
            return
        now = pygame.time.get_ticks()
        if len(aliens) == 0 and now >= self.next_wave_time:
            if self.wave_count > 0 and self.wave_count % 4 == 0:
                boss = BossAlien()
                all_sprites.add(boss)
                aliens.add(boss)
                self.next_wave_time = now + 10000
            else:
                formation = random.choice(self.formations)
                self.spawn_wave(formation)
                self.next_wave_time = now + 8000
            self.wave_count += 1

    def spawn_wave(self, matrix):
        rows = len(matrix)
        cols = len(matrix[0])
        spacing_x = WIDTH // (cols + 1)
        start_y = 40
        for r in range(rows):
            for c in range(cols):
                if matrix[r][c]:
                    x = spacing_x * (c + 1)
                    y = start_y + r * 40
                    offset = c * 0.4
                    alien = Alien(x, y, offset)
                    all_sprites.add(alien)
                    aliens.add(alien)

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
wave_manager = WaveManager()

# --- Timers ---
POWER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(POWER_EVENT, 10000)

def end_game():
    global game_over
    game_over = True

# --- Main Game Loop ---
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_ESCAPE and game_over:
                running = False
        if event.type == POWER_EVENT:
            p = PowerUp()
            all_sprites.add(p)
            powerups.add(p)

    for star in stars:
        star.update()

    wave_manager.update()
    all_sprites.update(keys)

    # --- Collisions ---
    for bullet in bullets.copy():
        for alien in aliens.copy():
            if bullet.rect.colliderect(alien.rect):
                bullet.kill()
                alien.health -= 1
                if alien.health <= 0:
                    all_sprites.add(Explosion(alien.rect.center))
                    EXPLOSION_SOUND.play()
                    alien.kill()
                    score += 100 if isinstance(alien, BossAlien) else 10

    for powerup in powerups.copy():
        if player.rect.colliderect(powerup.rect):
            POWERUP_SOUND.play()
            player.set_power(powerup.effect)
            powerup.kill()

    # --- Draw Everything ---
    screen.fill((0, 0, 0))
    for star in stars:
        star.draw(screen)
    all_sprites.draw(screen)

    hud = FONT.render(f"Score: {score}  Lives: {lives}  Power: {player.power or 'None'}", True, WHITE)
    screen.blit(hud, (10, 10))

    if game_over:
        text = FONT.render("GAME OVER — Press Esc to Exit", True, (255, 50, 50))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()