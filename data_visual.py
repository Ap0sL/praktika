from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import dataset


DEFAULT_CMAP = "viridis"
MARKER_STYLE = "<"
STUDENT_ID = "70221789"
SURNAME = "Анисимов"
OUTPUT_DIR = Path(__file__).resolve().parent / "graphs"

COLORMAPS = [
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "Greys",
    "Purples",
    "Blues",
    "Greens",
    "Oranges",
    "Reds",
    "YlOrBr",
    "YlOrRd",
    "OrRd",
    "PuRd",
    "RdPu",
    "BuPu",
    "GnBu",
    "PuBu",
    "YlGnBu",
    "PuBuGn",
    "BuGn",
    "YlGn",
    "binary",
    "gist_yarg",
    "spring",
    "summer",
    "autumn",
    "winter",
]


class VisualApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Improved data visualization")

        self.numeric_columns = dataset.get_numeric_columns()
        self.categorical_columns = dataset.get_categorical_columns()
        self.columns = self.numeric_columns + self.categorical_columns
        if len(self.columns) < 2:
            raise ValueError("The dataset must contain at least two columns.")

        self.x_column = tk.StringVar(value=self.columns[0])
        self.y_column = tk.StringVar(value=self.columns[1])
        self.cmap = tk.StringVar(value=DEFAULT_CMAP)
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
        center.rowconfigure(1, weight=1)

        top = ttk.Frame(center)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(top, text="Color map").pack(side="left")
        cmap_box = ttk.Combobox(top, textvariable=self.cmap, values=COLORMAPS, state="readonly")
        cmap_box.pack(side="left", padx=6)
        cmap_box.bind("<<ComboboxSelected>>", lambda _event: self.update_plot())

        self.canvas = tk.Canvas(center, width=840, height=520, bg="white", highlightthickness=1)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        bottom = ttk.Frame(center)
        bottom.grid(row=2, column=0, sticky="ew", pady=(8, 0))
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
        figure = Figure(figsize=(8.4, 5.2), dpi=100)
        axis = figure.add_subplot(111)
        x_name = self.x_column.get()
        y_name = self.y_column.get()
        x_is_numeric = x_name in self.numeric_columns
        y_is_numeric = y_name in self.numeric_columns

        if x_name == y_name and x_is_numeric:
            axis.hist(dataset.df[x_name].dropna(), bins=10, color=self._first_cmap_color())
            axis.set_ylabel("Count")
        elif x_name == y_name and not x_is_numeric:
            counts = dataset.df[x_name].fillna("NaN").value_counts()
            axis.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
        elif not x_is_numeric and y_is_numeric:
            counts = dataset.df[x_name].fillna("NaN").value_counts()
            axis.bar(counts.index.astype(str), counts.values, color=self._cmap_colors(len(counts)))
            axis.set_ylabel("Count")
            axis.tick_params(axis="x", labelrotation=30)
        elif x_is_numeric and not y_is_numeric:
            groups = [
                group[x_name].dropna().to_numpy()
                for _category, group in dataset.df.groupby(y_name, dropna=False)
            ]
            labels = [str(label) for label in dataset.df.groupby(y_name, dropna=False).groups]
            axis.boxplot(groups, tick_labels=labels)
            axis.set_ylabel(x_name)
            axis.tick_params(axis="x", labelrotation=30)
        else:
            axis.scatter(
                dataset.df[x_name],
                dataset.df[y_name],
                marker=MARKER_STYLE,
                color=self._first_cmap_color(),
                alpha=0.72,
            )

        axis.set_xlabel(x_name)
        if not (x_name == y_name and not x_is_numeric):
            axis.set_title(f"{x_name} / {y_name}")
        axis.grid(True, alpha=0.2)
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

    def _first_cmap_color(self) -> tuple[float, float, float, float]:
        return self._cmap_colors(1)[0]

    def _cmap_colors(self, count: int) -> list[tuple[float, float, float, float]]:
        from matplotlib import colormaps

        cmap = colormaps[self.cmap.get()]
        if count <= 1:
            return [cmap(0.6)]
        return [cmap(index / (count - 1)) for index in range(count)]

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
    VisualApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
