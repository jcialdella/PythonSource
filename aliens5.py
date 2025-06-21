import pygame
import random
import math
import logging
from pathlib import Path

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
class Config:
    WIDTH, HEIGHT = 600, 400
    FPS = 60
    WHITE = (255, 255, 255)
    PLAYER_SPEED = 6
    BULLET_SPEED = -7
    ALIEN_HEALTH = 2
    BOSS_HEALTH = 20
    POWERUP_DURATION = 5000
    WAVE_INTERVAL = 8000
    BOSS_INTERVAL = 10000
    BOSS_TIMEOUT = 15000
    POWERUP_SPEED = 3
    EXPLOSION_DURATION = 10

# --- Game State ---
class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.game_over = False

    def deduct_life(self, amount=1):
        self.lives -= amount
        if self.lives <= 0:
            self.game_over = True

    def add_score(self, points):
        self.score += points

# --- Asset Manager ---
class Assets:
    @staticmethod
    def load_image(file_name, scale=None):
        try:
            path = Path(file_name)
            if not path.exists():
                raise FileNotFoundError(f"Image {file_name} not found")
            img = pygame.image.load(str(path)).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except Exception as e:
            logger.error(f"Failed to load image {file_name}: {e}")
            surf = pygame.Surface((50, 50) if scale is None else scale)
            surf.fill((128, 128, 128))  # Gray fallback
            return surf

    @staticmethod
    def load_sound(file_name):
        try:
            path = Path(file_name)
            if not path.exists():
                raise FileNotFoundError(f"Sound {file_name} not found")
            return pygame.mixer.Sound(str(path))
        except Exception as e:
            logger.error(f"Failed to load sound {file_name}: {e}")
            return None

# --- Initialization ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Alien Invasion")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsansms", 18)

# --- Load Assets ---
assets = Assets()
PLAYER_IMG = assets.load_image("player.png", (50, 50))
ALIEN_IMG = assets.load_image("alien.png", (40, 40))
LASER_SOUND = assets.load_sound("laser.wav")
EXPLOSION_SOUND = assets.load_sound("explosion.wav")
POWERUP_SOUND = assets.load_sound("powerup.wav")

# --- Starfield ---
class Starfield:
    def __init__(self, num_stars=100):
        self.surface = pygame.Surface((Config.WIDTH, Config.HEIGHT)).convert()
        self.surface.set_colorkey((0, 0, 0))
        self.stars = [(random.randint(0, Config.WIDTH), random.randint(0, Config.HEIGHT), random.choice([1, 2, 3]))
                      for _ in range(num_stars)]
        self.draw_stars()

    def draw_stars(self):
        self.surface.fill((0, 0, 0))
        for x, y, layer in self.stars:
            shade = 180 + layer * 20
            pygame.draw.circle(self.surface, (shade, shade, shade), (int(x), int(y)), layer)

    def update(self, dt):
        for i, (x, y, layer) in enumerate(self.stars):
            y += 0.2 * layer * dt * Config.FPS
            if y > Config.HEIGHT:
                y = 0
                x = random.randint(0, Config.WIDTH)
            self.stars[i] = (x, y, layer)
        self.draw_stars()

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))

# --- Sprites ---
class Player(pygame.sprite.Sprite):
    def __init__(self, game_state):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(Config.WIDTH // 2, Config.HEIGHT - 10))
        self.speed = Config.PLAYER_SPEED
        self.power = None
        self.power_time = 0
        self.game_state = game_state
        self.shield_active = False

    def update(self, keys, dt):
        if self.game_state.game_over:
            return
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt * Config.FPS
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt * Config.FPS
        self.rect.clamp_ip(screen.get_rect())
        if self.power and pygame.time.get_ticks() - self.power_time > Config.POWERUP_DURATION:
            self.power = None
            self.shield_active = False

    def shoot(self):
        if self.game_state.game_over:
            return []
        offsets = [-10, 10] if self.power == "double" else [0]
        bullets = [Bullet(self.rect.centerx + dx, self.rect.top) for dx in offsets]
        if LASER_SOUND:
            LASER_SOUND.play()
        return bullets

    def set_power(self, effect):
        self.power = effect
        self.power_time = pygame.time.get_ticks()
        if effect == "shield":
            self.shield_active = True

class Bullet(pygame.sprite.Sprite):
    IMAGE = pygame.Surface((4, 10))
    IMAGE.fill((0, 255, 255))

    def __init__(self, x, y):
        super().__init__()
        self.image = self.IMAGE
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = Config.BULLET_SPEED

    def update(self, keys, dt):  # Accept keys to match signature, but ignore it
        self.rect.y += self.speed * dt * Config.FPS
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, offset, game_state):
        super().__init__()
        self.image = ALIEN_IMG
        self.orig_x = x
        self.rect = self.image.get_rect(center=(x, y))
        self.wave_offset = offset
        self.health = Config.ALIEN_HEALTH
        self.game_state = game_state

    def update(self, keys, dt):  # Accept keys to match signature, but ignore it
        if self.game_state.game_over:
            return
        t = pygame.time.get_ticks() / 500 + self.wave_offset
        self.rect.x = self.orig_x + 20 * math.sin(t)
        self.rect.y += (0.3 + 0.2 * math.sin(t * 0.7)) * dt * Config.FPS
        if self.rect.top > Config.HEIGHT:
            self.kill()
            if not self.game_state.game_over:
                self.game_state.deduct_life(1)

class BossAlien(pygame.sprite.Sprite):
    IMAGE = pygame.Surface((80, 60))
    IMAGE.fill((255, 0, 0))

    def __init__(self, game_state):
        super().__init__()
        self.image = self.IMAGE
        self.rect = self.image.get_rect(midtop=(Config.WIDTH // 2, -60))
        self.health = Config.BOSS_HEALTH
        self.speed = 1.5
        self.fall_speed = 0.6
        self.direction = 1
        self.spawn_time = pygame.time.get_ticks()
        self.game_state = game_state

    def update(self, keys, dt):  # Accept keys to match signature, but ignore it
        if self.game_state.game_over:
            return
        self.rect.y += self.fall_speed * dt * Config.FPS
        self.rect.x += self.speed * self.direction * dt * Config.FPS
        if self.rect.left < 0 or self.rect.right > Config.WIDTH:
            self.direction *= -1
        if pygame.time.get_ticks() - self.spawn_time > Config.BOSS_TIMEOUT:
            logger.info("Boss auto-despawned")
            self.kill()
        if self.rect.top > Config.HEIGHT:
            self.kill()
            if not self.game_state.game_over:
                self.game_state.deduct_life(3)

class Explosion(pygame.sprite.Sprite):
    IMAGE = pygame.Surface((30, 30))
    IMAGE.fill((255, 165, 0))

    def __init__(self, center):
        super().__init__()
        self.image = self.IMAGE
        self.rect = self.image.get_rect(center=center)
        self.timer = Config.EXPLOSION_DURATION

    def update(self, keys, dt):  # Accept keys to match signature, but ignore it
        self.timer -= dt * Config.FPS
        if self.timer <= 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    IMAGE = pygame.Surface((20, 20))
    IMAGE.fill((255, 105, 180))

    def __init__(self):
        super().__init__()
        self.effect = random.choice(["double", "shield"])
        self.image = self.IMAGE
        self.rect = self.image.get_rect(center=(random.randint(30, Config.WIDTH - 30), -20))
        self.speed = Config.POWERUP_SPEED

    def update(self, keys, dt):  # Accept keys to match signature, but ignore it
        self.rect.y += self.speed * dt * Config.FPS
        if self.rect.top > Config.HEIGHT:
            self.kill()

class WaveManager:
    def __init__(self, game_state, all_sprites, aliens):
        self.game_state = game_state
        self.all_sprites = all_sprites
        self.aliens = aliens
        self.next_wave_time = pygame.time.get_ticks() + Config.WAVE_INTERVAL
        self.wave_count = 0
        self.wave_active = False
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
        if self.game_state.game_over:
            return
        now = pygame.time.get_ticks()
        if not self.wave_active and len(self.aliens) == 0 and now >= self.next_wave_time:
            self.wave_active = True
            if self.wave_count > 0 and self.wave_count % 4 == 0:
                boss = BossAlien(self.game_state)
                self.all_sprites.add(boss)
                self.aliens.add(boss)
                self.next_wave_time = now + Config.BOSS_INTERVAL
            else:
                formation = random.choice(self.formations)
                self.spawn_wave(formation)
                self.next_wave_time = now + Config.WAVE_INTERVAL
            self.wave_count += 1
            self.wave_active = False

    def spawn_wave(self, matrix):
        rows = len(matrix)
        cols = len(matrix[0])
        spacing_x = Config.WIDTH // (cols + 1)
        start_y = 40
        for r in range(rows):
            for c in range(cols):
                if matrix[r][c]:
                    x = spacing_x * (c + 1)
                    y = start_y + r * 40
                    offset = c * 0.4
                    alien = Alien(x, y, offset, self.game_state)
                    self.all_sprites.add(alien)
                    self.aliens.add(alien)

# --- Main Game Loop ---
def main():
    game_state = GameState()
    starfield = Starfield()
    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player(game_state)
    all_sprites.add(player)
    wave_manager = WaveManager(game_state, all_sprites, aliens)

    POWER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(POWER_EVENT, 10000)

    running = True
    while running:
        dt = clock.tick(Config.FPS) / 1000.0  # Delta time in seconds
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bullet in player.shoot():
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                if event.key == pygame.K_ESCAPE and game_state.game_over:
                    running = False
            if event.type == POWER_EVENT:
                p = PowerUp()
                all_sprites.add(p)
                powerups.add(p)

        starfield.update(dt)
        wave_manager.update()
        all_sprites.update(keys, dt)  # Pass both keys and dt

        # --- Collisions ---
        hits = pygame.sprite.groupcollide(bullets, aliens, True, False)
        for bullet, hit_aliens in hits.items():
            for alien in hit_aliens:
                alien.health -= 1
                if alien.health <= 0:
                    all_sprites.add(Explosion(alien.rect.center))
                    if EXPLOSION_SOUND:
                        EXPLOSION_SOUND.play()
                    alien.kill()
                    game_state.add_score(100 if isinstance(alien, BossAlien) else 10)

        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            if POWERUP_SOUND:
                POWERUP_SOUND.play()
            player.set_power(powerup.effect)

        # Player-alien collision (with shield check)
        if not player.shield_active:
            alien_hits = pygame.sprite.spritecollide(player, aliens, True)
            for alien in alien_hits:
                all_sprites.add(Explosion(alien.rect.center))
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                game_state.deduct_life(1)

        # --- Draw ---
        screen.fill((0, 0, 0))
        starfield.draw(screen)
        all_sprites.draw(screen)

        hud = font.render(f"Score: {game_state.score}  Lives: {game_state.lives}  Power: {player.power or 'None'}", True, Config.WHITE)
        screen.blit(hud, (10, 10))

        if game_state.game_over:
            text = font.render("GAME OVER — Press Esc to Exit", True, (255, 50, 50))
            screen.blit(text, (Config.WIDTH // 2 - text.get_width() // 2, Config.HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()