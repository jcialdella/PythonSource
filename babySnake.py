import tkinter as tk
import random

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
SIZE = 20
GOAL_COLOR = "#fb607f"
PLAYER_COLOR = "#0096FF"
DELAY = 200  # milliseconds

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Game")

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack()

        self.directions = {
            'Left':  (-SIZE, 0),
            'Right': (SIZE, 0),
            'Up':    (0, -SIZE),
            'Down':  (0, SIZE)
        }

        # Initialize player & goal
        self.player_x, self.player_y = 0, 0
        self.player = self.create_rectangle(self.player_x, self.player_y, PLAYER_COLOR)

        self.goal_x, self.goal_y = self.random_position()
        self.goal = self.create_rectangle(self.goal_x, self.goal_y, GOAL_COLOR)

        self.direction_x, self.direction_y = SIZE, 0

        # Bind key events
        self.root.bind("<KeyPress>", self.handle_keypress)

        self.update_game()

    def create_rectangle(self, x, y, color):
        return self.canvas.create_rectangle(x, y, x + SIZE, y + SIZE, fill=color, outline="black")

    def detect_collision(self):
        return self.player_x < self.goal_x + SIZE and self.player_x + SIZE > self.goal_x and \
               self.player_y < self.goal_y + SIZE and self.player_y + SIZE > self.goal_y

    def random_position(self):
        return random.randint(0, CANVAS_WIDTH - SIZE), random.randint(0, CANVAS_HEIGHT - SIZE)

    def handle_keypress(self, event):
        if event.keysym in self.directions:
            self.direction_x, self.direction_y = self.directions[event.keysym]
        elif event.keysym == "Return":
            self.root.quit()

    def update_game(self):
        self.player_x += self.direction_x
        self.player_y += self.direction_y

        # Out-of-bounds check
        if not (0 <= self.player_x < CANVAS_WIDTH and 0 <= self.player_y < CANVAS_HEIGHT):
            print("Game over!")
            self.root.quit()

        # Collision detection
        if self.detect_collision():
            self.canvas.delete(self.goal)
            self.goal_x, self.goal_y = self.random_position()
            self.goal = self.create_rectangle(self.goal_x, self.goal_y, GOAL_COLOR)

        # Move player
        self.canvas.delete(self.player)
        self.player = self.create_rectangle(self.player_x, self.player_y, PLAYER_COLOR)

        self.root.after(DELAY, self.update_game)

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()