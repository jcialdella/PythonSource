import pygame
import random
import math
import sys
from pathlib import Path

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
    BOSS_TIMEOUT = 15000
    EXPLOSION_DURATION = 10
    POWERUP_SPEED = 3
    WAVE_INTERVAL = 8000
    BOSS_INTERVAL = 10000

# --- Game State ---
class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.game_over = False

    def add_score(self, points):
        self.score += points

    def deduct_life(self, amount=1):
        self.lives -= amount
        if self.lives <= 0:
            self.game_over = True

# --- Asset Loader ---
class Assets:
    def __init__(self):
        self.player_img = self.load_image("player.png", (50, 50))
        self.alien_img = self.load_image("alien.png", (40, 40))
        self.laser_sound = self.load_sound("laser.wav")
        self.explosion_sound = self.load_sound("explosion.wav")
        self.powerup_sound = self.load_sound("powerup.wav")

    def load_image(self, filename, scale):
        try:
            img = pygame.image.load(str(Path(filename)))
            return pygame.transform.scale(img, scale)
        except:
            surface = pygame.Surface(scale)
            surface.fill((128, 128, 128))
            return surface

    def load_sound(self, filename):
        try:
            return pygame.mixer.Sound(str(Path(filename)))
        except:
            return None

# --- Sprites ---
class Player(pygame.sprite.Sprite):
    def __init__(self, assets, game_state):
        super().__init__()
        self.image = assets.player_img
        self.rect = self.image.get_rect(midbottom=(Config.WIDTH // 2, Config.HEIGHT - 10))
        self.speed = Config.PLAYER_SPEED
        self.power = None
        self.power_time = 0
        self.game_state = game_state
        self.shield_active = False
        self.assets = assets

    def update(self, keys, dt):
        if self.game_state.game_over:
            return
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt * Config.FPS
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt * Config.FPS
        self.rect.clamp_ip(pygame.Rect(0, 0, Config.WIDTH, Config.HEIGHT))
        if self.power and pygame.time.get_ticks() - self.power_time > Config.POWERUP_DURATION:
            self.power = None
            self.shield_active = False

    def shoot(self):
        if self.game_state.game_over:
            return []
        offsets = [-10, 10] if self.power == "double" else [0]
        bullets = [Bullet(self.rect.centerx + dx, self.rect.top) for dx in offsets]
        if self.assets.laser_sound:
            self.assets.laser_sound.play()
        return bullets

    def set_power(self, effect):
        self.power = effect
        self.power_time = pygame.time.get_ticks()
        if effect == "shield":
            self.shield_active = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = Config.BULLET_SPEED

    def update(self, keys, dt):
        self.rect.y += self.speed * dt * Config.FPS
        if self.rect.bottom < 0:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, offset, img, game_state):
        super().__init__()
        self.image = img
        self.orig_x = x
        self.rect = self.image.get_rect(center=(x, y))
        self.offset = offset
        self.health = Config.ALIEN_HEALTH
        self.game_state = game_state

    def update(self, keys, dt):
        if self.game_state.game_over:
            return
        t = pygame.time.get_ticks() / 500 + self.offset
        self.rect.x = self.orig_x + 20 * math.sin(t)
        self.rect.y += (0.3 + 0.2 * math.sin(t * 0.7)) * dt * Config.FPS
        if self.rect.top > Config.HEIGHT:
            self.kill()
            self.game_state.deduct_life(1)

class BossAlien(pygame.sprite.Sprite):
    def __init__(self, img, game_state):
        super().__init__()
        self.image = pygame.Surface((80, 60))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midtop=(Config.WIDTH // 2, -60))
        self.health = Config.BOSS_HEALTH
        self.fall_speed = 0.6
        self.speed = 1.5
        self.direction = 1
        self.spawn_time = pygame.time.get_ticks()
        self.game_state = game_state

    def update(self, keys, dt):
        self.rect.y += self.fall_speed * dt * Config.FPS
        self.rect.x += self.speed * self.direction * dt * Config.FPS
        if self.rect.left < 0 or self.rect.right > Config.WIDTH:
            self.direction *= -1
        if pygame.time.get_ticks() - self.spawn_time > Config.BOSS_TIMEOUT:
            self.kill()
        if self.rect.top > Config.HEIGHT:
            self.kill()
            self.game_state.deduct_life(3)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect(center=center)
        self.timer = Config.EXPLOSION_DURATION

    def update(self, keys, dt):
        self.timer -= dt * Config.FPS
        if self.timer <= 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.effect = random.choice(["double", "shield"])
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 105, 180))
        self.rect = self.image.get_rect(center=(random.randint(30, Config.WIDTH - 30), -20))
        self.speed = Config.POWERUP_SPEED

    def update(self, keys, dt):
        self.rect.y += self.speed * dt * Config.FPS
        if self.rect.top > Config.HEIGHT:
            self.kill()

# --- Starfield ---
class Starfield:
    def __init__(self, count=100):
        self.stars = [(random.randint(0, Config.WIDTH), random.randint(0, Config.HEIGHT), random.choice([1, 2, 3]))
                      for _ in range(count)]

    def update(self, dt):
        new_stars = []
        for x, y, layer in self.stars:
            y += 0.2 * layer * dt * Config.FPS
            if y > Config.HEIGHT:
                y = 0
                x = random.randint(0, Config.WIDTH)
            new_stars.append((x, y, layer))
        self.stars = new_stars

    def draw(self, surface):
        for x, y, r in self.stars:
            shade = 180 + r * 20
            pygame.draw.circle(surface, (shade, shade, shade), (int(x), int(y)), r)

# --- Wave Manager ---
class WaveManager:
    def __init__(self, game_state, all_sprites, aliens, assets):
        self.game_state = game_state
        self.all_sprites = all_sprites
        self.aliens = aliens
        self.assets = assets
        self.wave_count = 0
        self.next_wave_time = pygame.time.get_ticks() + Config.WAVE_INTERVAL
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
        if len(self.aliens) == 0 and now >= self.next_wave_time:
            self.wave_count += 1
            if self.wave_count % 4 == 0:
                boss = BossAlien(None, self.game_state)
                self.all_sprites.add(boss)
                self.aliens.add(boss)
                self.next_wave_time = now + Config.BOSS_INTERVAL
            else:
                formation = random.choice(self.formations)
                self.spawn_wave(formation)
                self.next_wave_time = now + Config.WAVE_INTERVAL

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
                    alien = Alien(x, y, offset, self.assets.alien_img, self.game_state)
                    self.all_sprites.add(alien)
                    self.aliens.add(alien)

# --- Main Game Loop ---
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
    pygame.display.set_caption("Alien Invasion")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 18)

    game_state = GameState()
    assets = Assets()
    starfield = Starfield()

    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player(assets, game_state)
    all_sprites.add(player)
    wave_manager = WaveManager(game_state, all_sprites, aliens, assets)

    POWER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(POWER_EVENT, 10000)

    running = True
    while running:
        dt = clock.tick(Config.FPS) / 1000
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
        all_sprites.update(keys, dt)

        # --- Collisions ---
        hits = pygame.sprite.groupcollide(bullets, aliens, True, False)
        for bullet, victims in hits.items():
            for alien in victims:
                alien.health -= 1
                if alien.health <= 0:
                    all_sprites.add(Explosion(alien.rect.center))
                    if assets.explosion_sound:
                        assets.explosion_sound.play()
                    alien.kill()
                    game_state.add_score(100 if isinstance(alien, BossAlien) else 10)

        for p in pygame.sprite.spritecollide(player, powerups, True):
            if assets.powerup_sound:
                assets.powerup_sound.play()
            player.set_power(p.effect)

        if not player.shield_active:
            for alien in pygame.sprite.spritecollide(player, aliens, True):
                all_sprites.add(Explosion(alien.rect.center))
                if assets.explosion_sound:
                    assets.explosion_sound.play()
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
    sys.exit()

if __name__ == "__main__":
    main()