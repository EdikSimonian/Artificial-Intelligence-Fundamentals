import time

import pygame
import random
import heapq
# Window dimensions
WIDTH, HEIGHT = 500, 500

# Cell size
CELL_SIZE = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Start
RED = (255, 0, 0)  # End
BLUE = (0, 0, 255)  # Path
GREY = (211, 211, 211)  # Backtrack

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.walls = {'north': True, 'south': True, 'east': True, 'west': True}

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def generate(self):
        stack = []
        current = self.cells[0][0]
        current.visited = True

        while True:
            neighbors = self.get_unvisited_neighbors(current)
            if neighbors:
                next_cell = random.choice(neighbors)
                self.remove_wall(current, next_cell)
                next_cell.visited = True
                stack.append(current)
                current = next_cell
            elif stack:
                current = stack.pop()
            else:
                break

    def get_unvisited_neighbors(self, cell):
        neighbors = []
        if cell.x > 0 and not self.cells[cell.x - 1][cell.y].visited:
            neighbors.append(self.cells[cell.x - 1][cell.y])
        if cell.x < self.width - 1 and not self.cells[cell.x + 1][cell.y].visited:
            neighbors.append(self.cells[cell.x + 1][cell.y])
        if cell.y > 0 and not self.cells[cell.x][cell.y - 1].visited:
            neighbors.append(self.cells[cell.x][cell.y - 1])
        if cell.y < self.height - 1 and not self.cells[cell.x][cell.y + 1].visited:
            neighbors.append(self.cells[cell.x][cell.y + 1])
        return neighbors

    def remove_wall(self, cell1, cell2):
        if cell1.x == cell2.x:  # vertical wall
            if cell1.y < cell2.y:
                cell1.walls['south'] = False
                cell2.walls['north'] = False
            else:
                cell1.walls['north'] = False
                cell2.walls['south'] = False
        else:  # horizontal wall
            if cell1.x < cell2.x:
                cell1.walls['east'] = False
                cell2.walls['west'] = False
            else:
                cell1.walls['west'] = False
                cell2.walls['east'] = False

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[x][y]
                if cell.walls['north']:
                    pygame.draw.line(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE), ((x + 1) * CELL_SIZE, y * CELL_SIZE), 2)
                if cell.walls['south']:
                    pygame.draw.line(screen, BLACK, (x * CELL_SIZE, (y + 1) * CELL_SIZE), ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 2)
                if cell.walls['east']:
                    pygame.draw.line(screen, BLACK, ((x + 1) * CELL_SIZE, y * CELL_SIZE), ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE), 2)
                if cell.walls['west']:
                    pygame.draw.line(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE), (x * CELL_SIZE, (y + 1) * CELL_SIZE), 2)
                if x == 0 and y == 0:  # Start
                    pygame.draw.rect(screen, GREEN, (x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                elif x == self.width - 1 and y == self.height - 1:  # End
                    pygame.draw.rect(screen, RED, (x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))


    def draw_arrow(self, screen, px, py, x, y, color):
        """Helper function to draw an arrow from (px, py) to (x, y)."""
        arrow_size = 5
        dx, dy = x - px, y - py

        if dx == 1:  # right arrow
            pygame.draw.polygon(screen, color,
                                [(px * CELL_SIZE + CELL_SIZE, py * CELL_SIZE + CELL_SIZE // 2),
                                 (
                                 px * CELL_SIZE + CELL_SIZE - arrow_size, py * CELL_SIZE + CELL_SIZE // 2 - arrow_size),
                                 (px * CELL_SIZE + CELL_SIZE - arrow_size,
                                  py * CELL_SIZE + CELL_SIZE // 2 + arrow_size)])
        elif dx == -1:  # left arrow
            pygame.draw.polygon(screen, color,
                                [(px * CELL_SIZE, py * CELL_SIZE + CELL_SIZE // 2),
                                 (px * CELL_SIZE + arrow_size, py * CELL_SIZE + CELL_SIZE // 2 - arrow_size),
                                 (px * CELL_SIZE + arrow_size, py * CELL_SIZE + CELL_SIZE // 2 + arrow_size)])
        elif dy == 1:  # down arrow
            pygame.draw.polygon(screen, color,
                                [(px * CELL_SIZE + CELL_SIZE // 2, py * CELL_SIZE + CELL_SIZE),
                                 (
                                 px * CELL_SIZE + CELL_SIZE // 2 - arrow_size, py * CELL_SIZE + CELL_SIZE - arrow_size),
                                 (px * CELL_SIZE + CELL_SIZE // 2 + arrow_size,
                                  py * CELL_SIZE + CELL_SIZE - arrow_size)])
        elif dy == -1:  # up arrow
            pygame.draw.polygon(screen, color,
                                [(px * CELL_SIZE + CELL_SIZE // 2, py * CELL_SIZE),
                                 (px * CELL_SIZE + CELL_SIZE // 2 - arrow_size, py * CELL_SIZE + arrow_size),
                                 (px * CELL_SIZE + CELL_SIZE // 2 + arrow_size, py * CELL_SIZE + arrow_size)])

    def solve(self, screen):
        start = (0, 0)
        end = (self.width - 1, self.height - 1)

        # Priority queue: (cost, x, y, previous_cell)
        pq = [(0, start[0], start[1], None)]

        # Distance dictionary
        distances = {start: 0}

        # Parent dictionary to reconstruct the path
        parent = {}

        visited = set()
        path = []
        arrow_size = 5

        while pq:
            cost, x, y, prev = heapq.heappop(pq)

            # If already visited, skip
            if (x, y) in visited:
                continue
            visited.add((x, y))

            # Store parent for path reconstruction
            if prev is not None:
                parent[(x, y)] = prev

            # Stop when reaching the goal
            if (x, y) == end:
                break

            # Explore neighbors
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy

                if (0 <= nx < self.width and 0 <= ny < self.height and
                        (nx, ny) not in visited and
                        not self.cells[x][y].walls[self.get_wall(dx, dy)]):

                    new_cost = cost + 1  # Each move has uniform cost

                    # If this path is shorter, update it
                    if (nx, ny) not in distances or new_cost < distances[(nx, ny)]:
                        distances[(nx, ny)] = new_cost
                        heapq.heappush(pq, (new_cost, nx, ny, (x, y)))

            # Draw the exploration process
            screen.fill(WHITE)
            self.draw(screen)

            # Draw visited cells
            for vx, vy in visited:
                pygame.draw.rect(screen, GREY, (vx * CELL_SIZE + 2, vy * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4))

            pygame.display.flip()

        # Backtrack to find the final path
        current = end
        while current in parent:
            path.append(current)
            current = parent[current]
        path.append(start)
        path.reverse()

        # Draw the final shortest path
        for i in range(1, len(path)):
            px, py = path[i - 1]
            x, y = path[i]
            self.draw_arrow(screen, px, py, x, y, BLUE)

        pygame.display.flip()

        # Pause to show final result
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    paused = False

    def get_wall(self, dx, dy):
        if dx == 0 and dy == -1:
            return 'north'
        elif dx == 0 and dy == 1:
            return 'south'
        elif dx == -1 and dy == 0:
            return 'west'
        elif dx == 1 and dy == 0:
            return 'east'


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    maze = Maze(WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)
    maze.generate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        maze.draw(screen)
        pygame.display.flip()
        clock.tick(5)

        # Wait for a key press to start solving
        pygame.time.delay(1000)
        maze.solve(screen)

    pygame.quit()


if __name__ == "__main__":
    main()