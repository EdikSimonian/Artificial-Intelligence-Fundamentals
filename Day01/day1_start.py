import pygame
import random
import time
import os

# Constants
WIDTH, HEIGHT = 500, 500
CELL_SIZE = 50
WHITE, BLACK, GREEN, RED, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_NAMES = ['up', 'right', 'down', 'left']
FONT_SIZE = 18

# Debug variables
SEED = None
ANIMATION_DELAY = 0.1
DEMO = False
SCREENSHOT = False

class Cell:
    def __init__(self, x, y):
        self.x, self.y, self.visited = x, y, False
        self.walls = {d: True for d in ('north', 'south', 'east', 'west')}
        self.step_number = None
        self.is_solution = False

class Maze:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def get_wall(self, dx, dy):
        return {(0, -1): 'north', (0, 1): 'south', (-1, 0): 'west', (1, 0): 'east'}[(dx, dy)]

    def generate(self):
        stack, current = [], self.cells[0][0]
        current.visited = True
        while True:
            neighbors = [(dx, dy, self.cells[current.x + dx][current.y + dy])
                         for dx, dy in DIRECTIONS
                         if 0 <= current.x + dx < self.width and 0 <= current.y + dy < self.height
                         and not self.cells[current.x + dx][current.y + dy].visited]
            if neighbors:
                dx, dy, next_cell = random.choice(neighbors)
                current.walls[self.get_wall(dx, dy)] = next_cell.walls[self.get_wall(-dx, -dy)] = False
                next_cell.visited = True
                stack.append(current)
                current = next_cell
            elif stack:
                current = stack.pop()
            else:
                break

    def draw(self, screen, font):
        screen.fill(WHITE)
        for row in self.cells:
            for cell in row:
                x, y = cell.x * CELL_SIZE, cell.y * CELL_SIZE
                for direction in ('north', 'south', 'east', 'west'):
                    if cell.walls[direction]:
                        if direction == 'north': pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
                        if direction == 'south': pygame.draw.line(screen, BLACK, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
                        if direction == 'east': pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
                        if direction == 'west': pygame.draw.line(screen, BLACK, (x, y), (x, y + CELL_SIZE), 2)
                pygame.draw.rect(screen, GREEN if (cell.x, cell.y) == (0, 0) else YELLOW if (cell.x, cell.y) == (self.width-1, self.height-1) else WHITE, (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))
                if cell.step_number is not None:
                    text_color = RED if cell.is_solution else BLUE
                    text_surface = font.render(str(cell.step_number), True, text_color)
                    text_rect = text_surface.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def get_neighbor_states(self, cell):
        states = {}
        for i, (dx, dy) in enumerate(DIRECTIONS):
            nx, ny = cell.x + dx, cell.y + dy
            direction_name = DIR_NAMES[i]
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbor = self.cells[nx][ny]
                wall_between = cell.walls[self.get_wall(dx, dy)]
                if neighbor == self.cells[self.width - 1][self.height - 1] and not wall_between:
                    states[direction_name] = "goal"
                elif neighbor.step_number is not None:
                    states[direction_name] = "visited"
                elif not wall_between:
                    states[direction_name] = "open"
                else:
                    states[direction_name] = "wall"
            else:
                states[direction_name] = "invalid"
        return states

    def move(self, neighbors, current):
        # Use following variables
        #   DIR_NAMES
        #   DIRECTIONS
        #   self.cells

        # Code here
            
        return None

    def solve(self, screen, font):
        current = self.cells[0][0]
        end = self.cells[self.width - 1][self.height - 1]
        stack, step = [current], 1
        current.step_number = step

        while current != end:
            pygame.event.pump()
            self.draw(screen, font)

            neighbors = self.get_neighbor_states(current)
            next_cell = self.move(neighbors, current)
            moved = next_cell is not None
            if moved:
                step += 1
                next_cell.step_number = step
                stack.append(next_cell)
                current = next_cell
            else:
                stack.pop()
                current = stack[-1]

            if moved and ANIMATION_DELAY > 0:
                pygame.display.flip()
                time.sleep(ANIMATION_DELAY)

        # Backtrack to find the shortest path
        current = end
        path = [current]
        while current.step_number != 1:
            neighbors = []
            for dx, dy in DIRECTIONS:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.cells[nx][ny]
                    if neighbor.step_number is not None and neighbor.step_number < current.step_number and not current.walls[self.get_wall(dx, dy)]:
                        neighbors.append(neighbor)

            if not neighbors:
                raise Exception(f"No valid neighbor found from cell ({current.x}, {current.y}) during backtracking!")

            current = min(neighbors, key=lambda cell: cell.step_number)
            path.append(current)

        # Mark the shortest path
        for cell in path:
            cell.is_solution = True

        self.draw(screen, font)

def main():
    pygame.init()
    pygame.display.set_caption("Maze Solver")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None, FONT_SIZE)

    running = True
    while running:
        # Seed random number generator for reproducibility
        seed = SEED if SEED is not None else random.randint(0, 1000000)
        random.seed(seed)

        # Generate maze
        maze = Maze(WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)
        maze.generate()

        # Draw maze
        maze.draw(screen, font)
        
        # Solve maze
        maze.solve(screen, font)

        # Screenshot 
        if SCREENSHOT:
            visited_cells = sum(1 for row in maze.cells for cell in row if cell.step_number is not None)
            total_cells = maze.width * maze.height
            visited_percentage = visited_cells / total_cells

            dimension_folder = f"{maze.width}x{maze.height}"
            if visited_percentage <= 0.25:
                folder_name = f"Day01/screenshots/{dimension_folder}/0-25_percent"
            elif visited_percentage <= 0.50:
                folder_name = f"Day01/screenshots/{dimension_folder}/25-50_percent"
            elif visited_percentage <= 0.75:
                folder_name = f"Day01/screenshots/{dimension_folder}/50-75_percent"
            else:
                folder_name = f"Day01/screenshots/{dimension_folder}/75-100_percent"

            os.makedirs(folder_name, exist_ok=True)
            
            pygame.image.save(screen, f"{folder_name}/{seed}_solved.jpg")
            os.rename("temp.jpg", f"{folder_name}/{seed}_unsolved.jpg")

        if DEMO:
            pygame.time.delay(3000)
        else:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_q, pygame.K_ESCAPE):
                            running = False
                        waiting = False

    pygame.quit()

if __name__ == "__main__":
    main()