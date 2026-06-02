from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import dataset


MARKER_STYLE = "<"
STUDENT_ID = "70221789"
SURNAME = "Анисимов"
OUTPUT_DIR = Path(__file__).resolve().parent / "graphs"


class ScatterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Primary data visualization")

        self.columns = dataset.get_numeric_columns()
        if len(self.columns) < 2:
            raise ValueError("The dataset must contain at least two numeric columns.")

        self.x_column = tk.StringVar(value=self.columns[0])
        self.y_column = tk.StringVar(value=self.columns[1])
        self._photo: ImageTk.PhotoImage | None = None

        self._build_layout()
        self.update_plot()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=8)
        left.grid(row=0, column=0, sticky="ns")
        ttk.Label(left, text="Y axis").pack(anchor="w")
        for column in self.columns:
            ttk.Button(left, text=column, command=lambda c=column: self.set_y_column(c)).pack(
                fill="x", pady=2
            )

        center = ttk.Frame(self.root, padding=8)
        center.grid(row=0, column=1, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(center, width=820, height=520, bg="white", highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        bottom = ttk.Frame(center)
        bottom.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(bottom, text="X axis").pack(side="left")
        for column in self.columns:
            ttk.Button(bottom, text=column, command=lambda c=column: self.set_x_column(c)).pack(
                side="left", padx=2
            )
        ttk.Button(bottom, text="Save", command=self.save_graph).pack(side="right", padx=2)

    def set_x_column(self, column: str) -> None:
        self.x_column.set(column)
        self.update_plot()

    def set_y_column(self, column: str) -> None:
        self.y_column.set(column)
        self.update_plot()

    def create_figure(self) -> Figure:
        figure = Figure(figsize=(8.2, 5.2), dpi=100)
        axis = figure.add_subplot(111)
        axis.scatter(
            dataset.df[self.x_column.get()],
            dataset.df[self.y_column.get()],
            marker=MARKER_STYLE,
            color="#2454a6",
            alpha=0.72,
        )
        axis.set_xlabel(self.x_column.get())
        axis.set_ylabel(self.y_column.get())
        axis.grid(True, alpha=0.25)
        figure.tight_layout()
        return figure

    def update_plot(self) -> None:
        figure = self.create_figure()
        self._draw_figure_on_canvas(figure)

    def save_graph(self) -> Path:
        OUTPUT_DIR.mkdir(exist_ok=True)
        filename = datetime.now().strftime("graph%H_%M_%S.png")
        path = OUTPUT_DIR / filename
        counter = 1
        while path.exists():
            path = OUTPUT_DIR / f"{path.stem}_{counter}.png"
            counter += 1
        self.create_figure().savefig(path, dpi=120)
        return path

    def _draw_figure_on_canvas(self, figure: Figure) -> None:
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        width, height = canvas.get_width_height()
        image = Image.frombytes("RGBA", (width, height), canvas.buffer_rgba())
        self._photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)


def main() -> None:
    root = tk.Tk()
    ScatterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
