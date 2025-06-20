import tkinter as tk
import random
from PIL import Image, ImageTk

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
PLAYER_SPEED = 10
BULLET_SPEED = -15
ALIEN_SPEED = 2
ALIEN_SPAWN_RATE = 2000  # ms

class ShooterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Alien Shooter: Reloaded")

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        # Load player image
        img = Image.open("player.png").resize((40, 40))
        self.player_img = ImageTk.PhotoImage(img)
        self.player = self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT - 40, image=self.player_img)

        self.bullets = []
        self.aliens = []
        self.explosions = []

        # Bind controls
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<space>', self.shoot)

        # Schedule alien reinforcements
        self.root.after(ALIEN_SPAWN_RATE, self.spawn_alien)
        self.animate()

    def move_left(self, event):
        self.canvas.move(self.player, -PLAYER_SPEED, 0)

    def move_right(self, event):
        self.canvas.move(self.player, PLAYER_SPEED, 0)

    def shoot(self, event):
        x, y = self.canvas.coords(self.player)
        bullet = self.canvas.create_line(x, y - 20, x, y - 30, fill='cyan', width=3)
        self.bullets.append(bullet)

    def spawn_alien(self):
        x = random.randint(30, WINDOW_WIDTH - 30)
        alien = self.canvas.create_oval(x - 20, 0, x + 20, 40, fill='lime')
        self.aliens.append(alien)
        self.root.after(ALIEN_SPAWN_RATE, self.spawn_alien)

    def animate(self):
        # Move bullets
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, BULLET_SPEED)
            if self.canvas.coords(bullet)[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # Move aliens
        for alien in self.aliens[:]:
            self.canvas.move(alien, 0, ALIEN_SPEED)
            if self.canvas.coords(alien)[3] > WINDOW_HEIGHT:
                self.canvas.delete(alien)
                self.aliens.remove(alien)

        # Check for collisions
        for bullet in self.bullets[:]:
            for alien in self.aliens[:]:
                if self.intersects(bullet, alien):

                    bx1, by1, bx2, by2 = self.canvas.coords(alien)
                    x = (bx1 + bx2) / 2
                    y = (by1 + by2) / 2

                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.canvas.delete(bullet)
                    self.canvas.delete(alien)
                    self.show_explosion(x, y)

        # Remove explosion flashes
        for flash in self.explosions[:]:
            self.canvas.delete(flash)
        self.explosions.clear()

        self.root.after(50, self.animate)

    def intersects(self, a, b):
        a_coords = self.canvas.coords(a)
        b_coords = self.canvas.coords(b)

        if not a_coords or not b_coords:
            return False  # One of them has already been deleted

        ax, ay = a_coords[0], a_coords[1]
        bx1, by1, bx2, by2 = b_coords
        return bx1 < ax < bx2 and by1 < ay < by2

    def show_explosion(self, x, y):
        flash = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='orange', outline='')
        self.explosions.append(flash)

# --- Main Game ---
root = tk.Tk()
game = ShooterGame(root)
root.mainloop()