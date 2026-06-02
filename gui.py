import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from game_of_life import (
    GameOfLife,
    get_glider,
    get_block,
    get_pulsar,
    get_pentadecathlon,
    get_acorn,
    save_frames_as_gif
)

class GameOfLifeGUI:

    def __init__(self, root, grid_size: int = 100, cell_size: int = 6):
        self.root = root
        self.root.title("Gra w Zycie - Automat Komorkowy")

        self.grid_size = grid_size
        self.cell_size = cell_size
        self.simulation_speed = 100  # Predkosc w milisekundach

        # Tworzymy obiekt gry (logika)
        self.game = GameOfLife(width=grid_size, height=grid_size, boundary='periodic')

        # Flagi sterujace
        self.is_running = False  # Czy symulacja jest uruchomiona
        self.custom_rules = False  # Czy uzywamy wlasnych regul
        self.frames = []  # Lista klatek do zapisu GIF
        self.recording = False  # Czy nagrywamy do GIF
        self.drawing = False  # Czy rysujemy myszka
        self.erasing = False  # Czy wymazujemy myszka

        # Tworzymy elementy interfejsu
        self.create_widgets()

        # Rysujemy plansze
        self.draw_grid()

        # Bindujemy zdarzenia myszy
        self.canvas.bind("<Button-1>", self.mouse_down)  # Lewy przycisk - rysowanie
        self.canvas.bind("<Button-3>", self.mouse_down_erase)  # Prawy przycisk - wymazywanie
        self.canvas.bind("<B1-Motion>", self.mouse_drag)  # Przeciaganie z lewym
        self.canvas.bind("<B3-Motion>", self.mouse_drag_erase)  # Przeciaganie z prawym
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind("<ButtonRelease-3>", self.mouse_up)

    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Przycisk Start/Stop
        self.start_button = tk.Button(
            control_frame,
            text="Start",
            command=self.toggle_simulation,
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.start_button.pack(side=tk.LEFT, padx=2)

        # Przycisk pojedynczego kroku
        self.step_button = tk.Button(
            control_frame,
            text="Krok",
            command=self.single_step,
            width=10,
            font=("Arial", 10)
        )
        self.step_button.pack(side=tk.LEFT, padx=2)

        # Przycisk reset
        reset_button = tk.Button(
            control_frame,
            text="Reset",
            command=self.reset_simulation,
            width=10,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold")
        )
        reset_button.pack(side=tk.LEFT, padx=2)

        # Przycisk czyszczenia planszy
        clear_button = tk.Button(
            control_frame,
            text="Wyczysc",
            command=self.clear_board,
            width=10,
            font=("Arial", 10)
        )
        clear_button.pack(side=tk.LEFT, padx=2)

        pattern_frame = tk.LabelFrame(control_frame, text="Wzorzec startowy", padx=5, pady=5)
        pattern_frame.pack(side=tk.LEFT, padx=10)

        # Lista rozwijana z wzorcami
        self.pattern_var = tk.StringVar(value="Glider")
        pattern_menu = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_var,
            values=["Glider", "Block", "Pulsar", "Pentadecathlon", "Acorn"],
            state="readonly",
            width=15
        )
        pattern_menu.pack(side=tk.LEFT, padx=2)

        # Przycisk wczytania wzorca
        load_button = tk.Button(
            pattern_frame,
            text="Wczytaj",
            command=self.load_pattern,
            width=8
        )
        load_button.pack(side=tk.LEFT, padx=2)

        boundary_frame = tk.LabelFrame(control_frame, text="Warunek brzegowy", padx=5, pady=5)
        boundary_frame.pack(side=tk.LEFT, padx=10)

        # Lista rozwijana z warunkami brzegowymi
        self.boundary_var = tk.StringVar(value="Periodyczny")
        boundary_menu = ttk.Combobox(
            boundary_frame,
            textvariable=self.boundary_var,
            values=["Periodyczny", "Odbijajacy"],
            state="readonly",
            width=12
        )
        boundary_menu.pack(side=tk.LEFT, padx=2)
        boundary_menu.bind("<<ComboboxSelected>>", self.change_boundary)

        rules_frame = tk.LabelFrame(control_frame, text="Reguly", padx=5, pady=5)
        rules_frame.pack(side=tk.LEFT, padx=10)

        # Checkbox dla wlasnych reguł
        self.custom_rules_var = tk.BooleanVar(value=False)
        custom_check = tk.Checkbutton(
            rules_frame,
            text="Wlasne reguły (HighLife)",
            variable=self.custom_rules_var,
            command=self.toggle_custom_rules
        )
        custom_check.pack(side=tk.LEFT)

        control_frame2 = tk.Frame(self.root)
        control_frame2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        size_frame = tk.LabelFrame(control_frame2, text="Rozmiar siatki", padx=5, pady=5)
        size_frame.pack(side=tk.LEFT, padx=10)

        self.size_label = tk.Label(size_frame, text=f"{self.grid_size}x{self.grid_size}")
        self.size_label.pack(side=tk.LEFT, padx=5)

        self.size_scale = tk.Scale(
            size_frame,
            from_=50,
            to=200,
            orient=tk.HORIZONTAL,
            command=self.change_grid_size,
            showvalue=0,
            length=150
        )
        self.size_scale.set(self.grid_size)
        self.size_scale.pack(side=tk.LEFT, padx=2)

        # === PANEL PREDKOSCI ===
        speed_frame = tk.LabelFrame(control_frame2, text="Predkosc symulacji", padx=5, pady=5)
        speed_frame.pack(side=tk.LEFT, padx=10)

        self.speed_label = tk.Label(speed_frame, text="Normalna")
        self.speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_scale = tk.Scale(
            speed_frame,
            from_=10,
            to=500,
            orient=tk.HORIZONTAL,
            command=self.change_speed,
            showvalue=0,
            length=150
        )
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.LEFT, padx=2)

        gif_frame = tk.LabelFrame(control_frame2, text="Zapis GIF", padx=5, pady=5)
        gif_frame.pack(side=tk.LEFT, padx=10)

        # Przycisk nagrywania
        self.record_button = tk.Button(
            gif_frame,
            text="Nagraj GIF",
            command=self.toggle_recording,
            width=10
        )
        self.record_button.pack(side=tk.LEFT, padx=2)

        # Przycisk zapisu
        save_gif_button = tk.Button(
            gif_frame,
            text="Zapisz GIF",
            command=self.save_gif,
            width=10
        )
        save_gif_button.pack(side=tk.LEFT, padx=2)

        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # Etykieta z numerem generacji
        self.generation_label = tk.Label(
            info_frame,
            text="Generacja: 0",
            font=("Arial", 10, "bold")
        )
        self.generation_label.pack(side=tk.LEFT, padx=10)

        # Etykieta z liczba zywych komorek
        self.alive_label = tk.Label(
            info_frame,
            text="Zywych komorek: 0",
            font=("Arial", 10, "bold")
        )
        self.alive_label.pack(side=tk.LEFT, padx=10)

        # Etykieta statusu nagrywania
        self.record_label = tk.Label(
            info_frame,
            text="",
            font=("Arial", 10, "bold"),
            fg="red"
        )
        self.record_label.pack(side=tk.LEFT, padx=10)

        # Instrukcja
        help_label = tk.Label(
            info_frame,
            text="💡 LPM - rysuj | PPM - wymaz",
            font=("Arial", 9),
            fg="blue"
        )
        help_label.pack(side=tk.RIGHT, padx=10)

        canvas_frame = tk.Frame(self.root, bg="gray")
        canvas_frame.pack(padx=10, pady=10)

        canvas_size = self.grid_size * self.cell_size
        self.canvas = tk.Canvas(
            canvas_frame,
            width=canvas_size,
            height=canvas_size,
            bg="white",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.pack()

    def draw_grid(self):

        self.canvas.delete("all")  # Czyścimy canvas

        grid = self.game.get_grid_copy()

        # Rysujemy siatke
        for i in range(self.grid_size + 1):
            # Linie pionowe
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_size * self.cell_size, fill="#e0e0e0", width=1)
            # Linie poziome
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_size * self.cell_size, y, fill="#e0e0e0", width=1)

        # Przechodzimy przez wszystkie komorki
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if grid[y, x] == 1:  # Komorka zywa
                    # Rysujemy zielony kwadrat
                    x1 = x * self.cell_size + 1
                    y1 = y * self.cell_size + 1
                    x2 = x1 + self.cell_size - 1
                    y2 = y1 + self.cell_size - 1

                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#4CAF50",
                        outline=""
                    )

        # Aktualizujemy informacje
        self.update_info()

    def update_info(self):
        self.generation_label.config(text=f"Generacja: {self.game.generation}")
        alive_count = np.sum(self.game.grid)
        self.alive_label.config(text=f"Zywych komorek: {alive_count}")

    def toggle_simulation(self):
        self.is_running = not self.is_running

        if self.is_running:
            self.start_button.config(text="Stop", bg="#f44336")
            self.run_simulation()
        else:
            self.start_button.config(text="Start", bg="#4CAF50")

    def run_simulation(self):
        if self.is_running:
            self.game.step(custom_rules=self.custom_rules)

            # Jesli nagrywamy, zapisujemy klatke
            if self.recording:
                self.frames.append(self.game.get_grid_copy())

            self.draw_grid()

            # Wywolaj ponownie po okreslonym czasie
            self.root.after(self.simulation_speed, self.run_simulation)

    def single_step(self):
        self.game.step(custom_rules=self.custom_rules)

        if self.recording:
            self.frames.append(self.game.get_grid_copy())

        self.draw_grid()

    def reset_simulation(self):
        self.is_running = False
        self.start_button.config(text="Start", bg="#4CAF50")
        self.game.generation = 0
        self.draw_grid()

    def clear_board(self):
        self.is_running = False
        self.start_button.config(text="Start", bg="#4CAF50")
        self.game.reset()
        self.draw_grid()

    def load_pattern(self):
        # Zatrzymujemy symulacje i resetujemy plansze
        self.is_running = False
        self.start_button.config(text="Start", bg="#4CAF50")
        self.game.reset()

        # Pobieramy wybrany wzorzec
        pattern_name = self.pattern_var.get()

        # Srodek planszy
        center_x = self.grid_size // 2
        center_y = self.grid_size // 2

        # Wybieramy odpowiedni wzorzec
        if pattern_name == "Glider":
            pattern = get_glider()
        elif pattern_name == "Block":
            pattern = get_block()
        elif pattern_name == "Pulsar":
            pattern = get_pulsar()
        elif pattern_name == "Pentadecathlon":
            pattern = get_pentadecathlon()
        elif pattern_name == "Acorn":
            pattern = get_acorn()
        else:
            pattern = []

        # Ustawiamy wzorzec na srodku planszy
        self.game.set_pattern(pattern, center_x - 10, center_y - 10)
        self.draw_grid()

    def change_boundary(self, event=None):
        boundary_name = self.boundary_var.get()

        if boundary_name == "Periodyczny":
            self.game.boundary = 'periodic'
        else:  # Odbijajacy
            self.game.boundary = 'reflective'

    def toggle_custom_rules(self):
        self.custom_rules = self.custom_rules_var.get()

        if self.custom_rules:
            messagebox.showinfo(
                "Wlasne reguly",
                "Wlaczono reguly HighLife (B36/S23):\n\n"
                "- Komorka martwa ozywa przy 3 lub 6 sasiadach\n"
                "- Komorka zywa przezywa przy 2 lub 3 sasiadach\n\n"
                "Ta regula tworzy replikatory!"
            )

    def change_grid_size(self, value):
        new_size = int(float(value))
        self.size_label.config(text=f"{new_size}x{new_size}")

        if new_size != self.grid_size:
            # Zapisujemy aktualny stan
            old_grid = self.game.get_grid_copy()
            old_generation = self.game.generation

            # Tworzymy nową gre z nowym rozmiarem
            self.grid_size = new_size
            self.game = GameOfLife(width=new_size, height=new_size, boundary=self.game.boundary)

            # Probujemy przeniesc komorki (kopiujemy obszar, ktory sie miesci)
            min_height = min(old_grid.shape[0], new_size)
            min_width = min(old_grid.shape[1], new_size)
            self.game.grid[:min_height, :min_width] = old_grid[:min_height, :min_width]
            self.game.generation = old_generation

            # Aktualizujemy canvas
            canvas_size = self.grid_size * self.cell_size
            self.canvas.config(width=canvas_size, height=canvas_size)
            self.draw_grid()

    def change_speed(self, value):
        speed = int(float(value))
        self.simulation_speed = speed

        # Aktualizujemy etykiete
        if speed <= 50:
            label = "Bardzo szybka"
        elif speed <= 100:
            label = "Szybka"
        elif speed <= 200:
            label = "Normalna"
        elif speed <= 350:
            label = "Wolna"
        else:
            label = "Bardzo wolna"

        self.speed_label.config(text=label)

    def toggle_recording(self):
        self.recording = not self.recording

        if self.recording:
            self.frames = []  # Czyscimy listę klatek
            self.frames.append(self.game.get_grid_copy())  # Dodajemy pierwsza klatke
            self.record_button.config(text="Stop nagrywania", bg="#f44336")
            self.record_label.config(text="⏺ NAGRYWANIE")
        else:
            self.record_button.config(text="Nagraj GIF", bg="SystemButtonFace")
            self.record_label.config(text="")
            messagebox.showinfo(
                "Nagrywanie zakonczone",
                f"Nagrano {len(self.frames)} klatek.\n"
                "Uzyj przycisku 'Zapisz GIF' aby zapisac animacje."
            )

    def save_gif(self):
        if not self.frames:
            messagebox.showwarning(
                "Brak klatek",
                "Najpierw nagraj symulacje uzywajac przycisku 'Nagraj GIF'!"
            )
            return

        # Generujemy nazwe pliku
        pattern_name = self.pattern_var.get().lower()
        boundary_name = "periodic" if self.game.boundary == 'periodic' else "reflective"
        rules_name = "highlife" if self.custom_rules else "conway"
        filename = f"game_of_life_{pattern_name}_{boundary_name}_{rules_name}.gif"

        try:
            save_frames_as_gif(self.frames, filename, duration=100, cell_size=self.cell_size)
            messagebox.showinfo(
                "Sukces!",
                f"GIF zapisany jako:\n{filename}\n\n"
                f"Liczba klatek: {len(self.frames)}"
            )
        except Exception as e:
            messagebox.showerror(
                "Blad",
                f"Nie udalo sie zapisac GIF:\n{str(e)}"
            )

    def mouse_down(self, event):
        self.drawing = True
        self.toggle_cell(event)

    def mouse_down_erase(self, event):
        self.erasing = True
        self.toggle_cell(event, erase=True)

    def mouse_drag(self, event):
        if self.drawing:
            self.toggle_cell(event)

    def mouse_drag_erase(self, event):
        if self.erasing:
            self.toggle_cell(event, erase=True)

    def mouse_up(self, event):
        self.drawing = False
        self.erasing = False

    def toggle_cell(self, event, erase=False):
        # Obliczamy pozycje komorki na podstawie pozycji myszy
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        # Sprawdzamy czy pozycja jest w granicach planszy
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if erase:
                self.game.set_cell(x, y, 0)  # Ustawiamy jako martwa
            else:
                self.game.set_cell(x, y, 1)  # Ustawiamy jako zywa

            self.draw_grid()


def main():
    root = tk.Tk()

    # Ustawiamy rozmiar okna
    root.geometry("900x900")
    root.resizable(False, False)

    # Tworzymy GUI
    app = GameOfLifeGUI(root, grid_size=100, cell_size=6)

    root.mainloop()

# Uruchomienie programu
if __name__ == "__main__":
    main()