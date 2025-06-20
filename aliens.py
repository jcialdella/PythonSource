import tkinter as tk

# --- Constants ---
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
PLAYER_SPEED = 10
BULLET_SPEED = -10
ALIEN_SPEED = 2

class ShooterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Alien Shooter")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        # Player setup
        self.player = self.canvas.create_rectangle(280, 370, 320, 390, fill='cyan')

        # Bind controls
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<space>', self.shoot)

        self.bullets = []
        self.aliens = [self.canvas.create_oval(x, 50, x+30, 80, fill='green') for x in range(50, 550, 100)]

        self.animate()

    def move_left(self, event):
        self.canvas.move(self.player, -PLAYER_SPEED, 0)

    def move_right(self, event):
        self.canvas.move(self.player, PLAYER_SPEED, 0)

    def shoot(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.player)
        bullet = self.canvas.create_rectangle((x1+x2)//2 - 2, y1 - 10, (x1+x2)//2 + 2, y1, fill='yellow')
        self.bullets.append(bullet)

    def animate(self):
        # Move bullets
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, BULLET_SPEED)
            if self.canvas.coords(bullet)[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # Move aliens
        for alien in self.aliens:
            self.canvas.move(alien, 0, ALIEN_SPEED)

        self.root.after(50, self.animate)

# --- Main ---
root = tk.Tk()
game = ShooterGame(root)
root.mainloop()