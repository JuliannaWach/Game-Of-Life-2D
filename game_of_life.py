import numpy as np
from typing import Tuple, List
from PIL import Image

class GameOfLife:

    def __init__(self, width: int = 200, height: int = 200, boundary: str = 'periodic'):
        self.width = width
        self.height = height
        self.boundary = boundary  # Typ warunku brzegowego

        # Tworzymy plansze - tablica 2D z samymi zerami (martwe komorki)
        # 0 = martwa komorka, 1 = zywa komorka
        self.grid = np.zeros((height, width), dtype=int)

        # Licznik wykonanych krokow symulacji
        self.generation = 0

    def set_cell(self, x: int, y: int, state: int = 1):
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y, x] = state

    def set_pattern(self, pattern: List[Tuple[int, int]], offset_x: int = 0, offset_y: int = 0):
        for x, y in pattern:
            self.set_cell(x + offset_x, y + offset_y, 1)

    def count_neighbors_periodic(self, x: int, y: int) -> int:
        count = 0

        # Sprawdzamy wszystkie 8 sąsiednich komorek (sasiedztwo Moore'a)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                # Pomijamy sama komorke (dx=0 i dy=0)
                if dx == 0 and dy == 0:
                    continue

                # Obliczamy pozycje sasiada z zawijaniem (modulo)
                neighbor_x = (x + dx) % self.width
                neighbor_y = (y + dy) % self.height

                # Dodajemy do licznika jesli sasiad zyje
                count += self.grid[neighbor_y, neighbor_x]

        return count

    def count_neighbors_reflective(self, x: int, y: int) -> int:
        count = 0

        # Sprawdzamy wszystkie 8 sasiednich komórek
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                # Pomijamy sama komorke
                if dx == 0 and dy == 0:
                    continue

                neighbor_x = x + dx
                neighbor_y = y + dy

                # Sprawdzamy czy sasiad jest w granicach planszy
                if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                    count += self.grid[neighbor_y, neighbor_x]
                # Jesli sasiad jest poza planszą, traktujemy go jako martwego (nic nie dodajemy)

        return count

    def count_neighbors(self, x: int, y: int) -> int:
        if self.boundary == 'periodic':
            return self.count_neighbors_periodic(x, y)
        else:  # reflective
            return self.count_neighbors_reflective(x, y)

    def step(self, custom_rules: bool = False):
        # Tworzymy nowa plansze dla nastepnej generacji
        new_grid = np.zeros_like(self.grid)

        # Przechodzimy przez kazda komorke na planszy
        for y in range(self.height):
            for x in range(self.width):
                # Liczymy zywych sasiadow tej komorki
                neighbors = self.count_neighbors(x, y)

                if custom_rules:
                    # WLASNE REGULY - "HighLife" (dodaje regule narodzin przy 6 sąsiadach)
                    # Regula B36/S23 (Birth at 3,6 / Survival at 2,3)
                    if self.grid[y, x] == 1:  # Komorka zywa
                        # Zywa komorka przezywa przy 2 lub 3 sasiadach
                        if neighbors == 2 or neighbors == 3:
                            new_grid[y, x] = 1
                        # W przeciwnym razie umiera
                    else:  # Komorka martwa
                        # Martwa komorka ozywa przy 3 lub 6 sasiadach
                        if neighbors == 3 or neighbors == 6:
                            new_grid[y, x] = 1
                else:
                    # STANDARDOWE REGULY GRY W ZYCIE
                    if self.grid[y, x] == 1:  # Komorka jest zywa
                        # Regula 2: Komorka zywa z 2 lub 3 sasiadami pozostaje zywa
                        if neighbors == 2 or neighbors == 3:
                            new_grid[y, x] = 1
                        # Regula 3: Komorka zywa z wiecej niż 3 sasiadami umiera (przeludnienie)
                        # Regula 4: Komorka zywa z mniej niż 2 sasiadami umiera (samotnosc)
                        # Oba przypadki prowadzą do smierci, wiec zostawiamy 0
                    else:  # Komorka jest martwa
                        # Regula 1: Martwa komorka z dokladnie 3 sasiadami ozywa
                        if neighbors == 3:
                            new_grid[y, x] = 1

        # Zamieniamy stara plansze na nowa
        self.grid = new_grid
        self.generation += 1

    def reset(self):

        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.generation = 0

    def get_grid_copy(self) -> np.ndarray:

        return self.grid.copy()

def get_glider() -> List[Tuple[int, int]]:
    return [
        (1, 0),
        (2, 1),
        (0, 2), (1, 2), (2, 2)
    ]

def get_block() -> List[Tuple[int, int]]:
    return [
        (0, 0), (1, 0),
        (0, 1), (1, 1)
    ]

def get_pulsar() -> List[Tuple[int, int]]:
    pattern = []

    # Gorna czesc pulsara
    # Pierwszy wiersz z gory
    for x in [2, 3, 4, 8, 9, 10]:
        pattern.append((x, 0))

    # Drugi wiersz
    for x in [2, 3, 4, 8, 9, 10]:
        pattern.append((x, 5))

    # Boki - lewa i prawa strona
    for y in [2, 3, 4]:
        pattern.append((0, y))
        pattern.append((5, y))
        pattern.append((7, y))
        pattern.append((12, y))

    # Dolna czesc - lustrzane odbicie gornej
    for x in [2, 3, 4, 8, 9, 10]:
        pattern.append((x, 7))

    for x in [2, 3, 4, 8, 9, 10]:
        pattern.append((x, 12))

    for y in [8, 9, 10]:
        pattern.append((0, y))
        pattern.append((5, y))
        pattern.append((7, y))
        pattern.append((12, y))

    return pattern

def get_pentadecathlon() -> List[Tuple[int, int]]:
    return [
        (5, 4),
        (4, 5), (5, 5), (6, 5),
        (5, 6),
        (5, 7),
        (5, 8),
        (4, 9), (5, 9), (6, 9),
        (5, 10),
        (5, 11),
        (5, 12),
        (4, 13), (5, 13), (6, 13),
        (5, 14)
    ]

def get_acorn() -> List[Tuple[int, int]]:
    return [
        (1, 0),
        (3, 1),
        (0, 2), (1, 2), (4, 2), (5, 2), (6, 2)
    ]

def save_frames_as_gif(frames: List[np.ndarray], filename: str = "game_of_life.gif",
                       duration: int = 100, cell_size: int = 3):
    images = []

    for frame in frames:
        # Powiekszamy obraz (kazda komorka to cell_size x cell_size pikseli)
        img_array = np.repeat(np.repeat(frame, cell_size, axis=0), cell_size, axis=1)

        img_array = (img_array * 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode='L')
        images.append(img)

    # Zapisujemy jako GIF
    if images:
        images[0].save(
            filename,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0
        )
        print(f"GIF zapisany jako: {filename}")