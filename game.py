import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from data import Data
from game_logic import GameLogic
import random
import os
import sys


class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Geografie Spel")
        self.root.geometry("1200x800")
        self.root.attributes("-fullscreen", True)

        countries_data = self.extract_data_by_type("landen")
        rivers_data = self.extract_data_by_type("rivieren")
        oceans_data = self.extract_data_by_type("oceanen")
        mountains_data = self.extract_data_by_type("bergen")
        continents_data = self.extract_data_by_type("continenten")
        world_blocks_data = self.extract_data_by_type("wereldblokken")

        self.game_logic = GameLogic(
            countries_data,
            rivers_data,
            oceans_data,
            mountains_data,
            continents_data,
            world_blocks_data,
        )

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.mode_frame = tk.Frame(self.control_frame)
        self.mode_frame.pack(pady=10)

        self.countries_button = tk.Button(
            self.mode_frame,
            text="Countries",
            command=lambda: self.set_game_mode("countries"),
        )
        self.countries_button.pack(side=tk.LEFT, padx=5)

        self.rivers_button = tk.Button(
            self.mode_frame, text="Rivers", command=lambda: self.set_game_mode("rivers")
        )
        self.rivers_button.pack(side=tk.LEFT, padx=5)

        self.oceans_button = tk.Button(
            self.mode_frame, text="Oceans", command=lambda: self.set_game_mode("oceans")
        )
        self.oceans_button.pack(side=tk.LEFT, padx=5)

        self.mountains_button = tk.Button(
            self.mode_frame,
            text="Mountains",
            command=lambda: self.set_game_mode("mountains"),
        )
        self.mountains_button.pack(side=tk.LEFT, padx=5)

        self.continents_button = tk.Button(
            self.mode_frame,
            text="Continents",
            command=lambda: self.set_game_mode("continents"),
        )
        self.continents_button.pack(side=tk.LEFT, padx=5)

        self.world_blocks_button = tk.Button(
            self.mode_frame,
            text="World Blocks",
            command=lambda: self.set_game_mode("world_blocks"),
        )
        self.world_blocks_button.pack(side=tk.LEFT, padx=5)

        self.score_label = tk.Label(
            self.control_frame, text="Score: 0", font=("Arial", 16)
        )
        self.score_label.pack(pady=10)

        self.question_label = tk.Label(
            self.control_frame, text="Select a game mode", font=("Arial", 14)
        )
        self.question_label.pack(pady=10)

        self.start_button = tk.Button(
            self.control_frame,
            text="Start Game",
            command=self.start_game,
            state=tk.DISABLED,
        )
        self.start_button.pack(pady=20)

        self.hint_button = tk.Button(
            self.control_frame, text="Hint", command=self.show_hint, state=tk.DISABLED
        )
        self.hard_mode_button = tk.Button(
            self.control_frame, text="Hard Mode", command=self.toggle_hard_mode
        )
        self.hard_mode_button.pack(pady=10)
        self.hint_button.pack(pady=10)

        self.next_button = tk.Button(
            self.control_frame, text="Next", command=self.next_round, state=tk.DISABLED
        )
        self.next_button.pack(pady=10)

        self.listbox = tk.Listbox(self.control_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.image_path = self.resource_path("./etopo.jpg")
        self.image_easy = plt.imread(self.image_path)

        self.figure = plt.figure(figsize=(20, 5))
        self.ax = self.figure.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        self.projections = [
            ccrs.Sinusoidal(),
            ccrs.InterruptedGoodeHomolosine(),
            ccrs.NearsidePerspective(),
            ccrs.LambertCylindrical(),
            ccrs.RotatedPole(),
        ]

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.map_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.init_map()

    def extract_data_by_type(self, data_type):
        for item in Data:
            if item["type"] == data_type:
                return item["data"]
        return {}

    def init_map(self):
        self.ax.clear()
        if not self.game_logic.hard_mode:
            self.ax.imshow(
                self.image_easy,
                origin="upper",
                extent=(-180, 180, -90, 90),
                transform=ccrs.PlateCarree(),
            )
        else:
            self.ax.add_feature(cfeature.LAND)
            self.ax.add_feature(cfeature.OCEAN)
        self.ax.add_feature(cfeature.COASTLINE)
        self.ax.add_feature(cfeature.BORDERS, linestyle=":")
        self.ax.add_feature(cfeature.LAKES, alpha=0.5)
        self.ax.add_feature(cfeature.RIVERS)
        self.ax.set_title("Geografie Spel")
        self.ax.set_global()

        if self.game_logic.rivers:
            for river, data in self.game_logic.rivers.items():
                lons, lats = zip(*data["coordinates"])
                self.ax.plot(
                    lons, lats, color="blue", linewidth=2, transform=ccrs.Geodetic()
                )

        self.figure.canvas.mpl_connect("button_press_event", self.on_map_click)
        self.canvas.draw()

    def resource_path(self, relative_path):
        try:
            return os.path.join(sys._MEIPASS, relative_path)
        except AttributeError:
            return relative_path

    def set_game_mode(self, mode):
        self.game_logic.set_game_mode(mode)
        self.start_button.config(state=tk.NORMAL)
        self.question_label.config(
            text=f"Game mode: {mode.capitalize()}\nClick 'Start Game' to begin"
        )
        self.populate_listbox()

    def start_game(self):
        self.game_logic.score = 0
        self.update_score_label()
        self.hint_button.config(state=tk.NORMAL)
        self.next_round()

    def next_round(self):
        self.init_map()
        self.next_button.config(state=tk.DISABLED)
        asked_item = self.game_logic.ask_random_item()
        if asked_item:
            if self.game_logic.hard_mode:
                self.toggle_new_map()
            self.question_label.config(text=f"Locate: {asked_item}")
        else:
            self.question_label.config(text="No more items in this category!")

    def on_map_click(self, event):
        if event.inaxes != self.ax or not self.game_logic.game_mode:
            return

        lon, lat = ccrs.PlateCarree().transform_point(
            event.xdata, event.ydata, self.ax.projection
        )
        clicked_item = self.game_logic.get_item_from_coordinates(lon, lat)

        if clicked_item:
            is_correct = self.game_logic.check_answer(clicked_item)
            self.update_score_label()
            self.show_feedback(lon, lat, clicked_item, is_correct)
            if is_correct:
                self.root.after(1000, self.next_round)

    def show_hint(self):
        if not self.game_logic.asked_item:
            return

        item_data = self.game_logic.get_item_data(self.game_logic.asked_item)
        if not item_data:
            return

        if self.game_logic.game_mode == "countries":
            if item_data and item_data.get("bbox"):
                for bbox in item_data["bbox"]:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    self.ax.add_patch(
                        plt.Rectangle(
                            (min_lon, min_lat),
                            max_lon - min_lon,
                            max_lat - min_lat,
                            fill=True,
                            edgecolor="yellow",
                            facecolor="yellow",
                            alpha=0.5,
                            transform=ccrs.PlateCarree(),
                        )
                    )
        elif self.game_logic.game_mode == "rivers":
            lons, lats = zip(*item_data["coordinates"])
            self.ax.plot(
                lons,
                lats,
                color="yellow",
                linewidth=10,
                alpha=0.5,
                transform=ccrs.Geodetic(),
            )
        elif self.game_logic.game_mode == "oceans":
            min_lon, min_lat, max_lon, max_lat = item_data["bbox"]
            self.ax.add_patch(
                plt.Rectangle(
                    (min_lon, min_lat),
                    max_lon - min_lon,
                    max_lat - min_lat,
                    fill=True,
                    edgecolor="yellow",
                    facecolor="yellow",
                    alpha=0.5,
                    transform=ccrs.PlateCarree(),
                )
            )
        elif self.game_logic.game_mode == "mountains":
            min_lon, min_lat, max_lon, max_lat = item_data["bbox"]
            self.ax.add_patch(
                plt.Rectangle(
                    (min_lon, min_lat),
                    max_lon - min_lon,
                    max_lat - min_lat,
                    fill=True,
                    edgecolor="yellow",
                    facecolor="yellow",
                    alpha=0.5,
                    transform=ccrs.PlateCarree(),
                )
            )
        elif self.game_logic.game_mode in ["continents", "world_blocks"]:
            for bbox in item_data["bbox"]:
                min_lon, min_lat, max_lon, max_lat = bbox
                self.ax.add_patch(
                    plt.Rectangle(
                        (min_lon, min_lat),
                        max_lon - min_lon,
                        max_lat - min_lat,
                        fill=True,
                        edgecolor="yellow",
                        facecolor="yellow",
                        alpha=0.5,
                        transform=ccrs.PlateCarree(),
                    )
                )

        self.canvas.draw()
        self.game_logic.score -= 1
        self.update_score_label()

    def toggle_hard_mode(self):
        self.game_logic.hard_mode = not self.game_logic.hard_mode
        mode_text = "ON" if self.game_logic.hard_mode else "OFF"
        self.hard_mode_button.config(text=f"Hard Mode: {mode_text}")

        self.figure.clear()

        if self.game_logic.hard_mode:
            self.ax = self.figure.add_subplot(
                1, 1, 1, projection=ccrs.AlbersEqualArea()
            )
        else:
            self.ax = self.figure.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        self.init_map()

    def toggle_new_map(self):
        random.choice(self.projections)
        self.figure.clear()
        self.ax = self.figure.add_subplot(
            1, 1, 1, projection=random.choice(self.projections)
        )
        self.init_map()

    def show_feedback(self, lon, lat, clicked_item, is_correct):
        self.init_map()

        color = "green" if is_correct else "red"
        self.ax.plot(
            lon,
            lat,
            marker="o",
            color=color,
            markersize=8,
            transform=ccrs.PlateCarree(),
        )

        if not is_correct:
            self.next_button.config(state=tk.NORMAL)
            item_data = self.game_logic.get_item_data(self.game_logic.asked_item)
            if self.game_logic.game_mode == "countries":
                if item_data and item_data.get("bbox"):
                    for bbox in item_data["bbox"]:
                        min_lon, min_lat, max_lon, max_lat = bbox
                        self.ax.add_patch(
                            plt.Rectangle(
                                (min_lon, min_lat),
                                max_lon - min_lon,
                                max_lat - min_lat,
                                fill=False,
                                edgecolor="green",
                                linewidth=2,
                                transform=ccrs.PlateCarree(),
                            )
                        )
            elif self.game_logic.game_mode == "rivers":
                lons, lats = zip(*item_data["coordinates"])
                self.ax.plot(
                    lons, lats, color="green", linewidth=2, transform=ccrs.Geodetic()
                )
            elif self.game_logic.game_mode == "oceans":
                min_lon, min_lat, max_lon, max_lat = item_data["bbox"]
                self.ax.add_patch(
                    plt.Rectangle(
                        (min_lon, min_lat),
                        max_lon - min_lon,
                        max_lat - min_lat,
                        fill=False,
                        edgecolor="green",
                        linewidth=2,
                        transform=ccrs.PlateCarree(),
                    )
                )
            elif self.game_logic.game_mode == "mountains":
                min_lon, min_lat, max_lon, max_lat = item_data["bbox"]
                self.ax.add_patch(
                    plt.Rectangle(
                        (min_lon, min_lat),
                        max_lon - min_lon,
                        max_lat - min_lat,
                        fill=False,
                        edgecolor="green",
                        linewidth=2,
                        transform=ccrs.PlateCarree(),
                    )
                )
            elif self.game_logic.game_mode in ["continents", "world_blocks"]:
                if item_data and item_data.get("bbox"):
                    for bbox in item_data["bbox"]:
                        min_lon, min_lat, max_lon, max_lat = bbox
                        self.ax.add_patch(
                            plt.Rectangle(
                                (min_lon, min_lat),
                                max_lon - min_lon,
                                max_lat - min_lat,
                                fill=False,
                                edgecolor="green",
                                linewidth=2,
                                transform=ccrs.PlateCarree(),
                            )
                        )

        title = f"{clicked_item} - {'Correct!' if is_correct else 'Wrong!'}"
        self.ax.set_title(title)

        if self.game_logic.game_mode == "rivers" and self.game_logic.rivers:
            for river, data in self.game_logic.rivers.items():
                lons, lats = zip(*data["coordinates"])
                self.ax.plot(
                    lons, lats, color="blue", linewidth=2, transform=ccrs.Geodetic()
                )

        self.canvas.draw()

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.game_logic.score}")

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)
        items = []
        if self.game_logic.game_mode == "countries":
            allowed_countries = [
                "China",
                "Russia",
                "US",
                "Brazil",
                "Egypt",
                "Turkey",
                "Iran",
                "Mexico",
                "Congo (Democratic Republic)",
            ]
            items = [
                country
                for country in self.game_logic.countries.keys()
                if country in allowed_countries
            ]
        elif self.game_logic.game_mode == "rivers":
            items = self.game_logic.rivers.keys()
        elif self.game_logic.game_mode == "oceans":
            items = self.game_logic.oceans.keys()
        elif self.game_logic.game_mode == "mountains":
            items = self.game_logic.mountains.keys()
        elif self.game_logic.game_mode == "continents":
            items = self.game_logic.continents.keys()
        elif self.game_logic.game_mode == "world_blocks":
            items = self.game_logic.world_blocks.keys()

        for item in items:
            self.listbox.insert(tk.END, item)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()
