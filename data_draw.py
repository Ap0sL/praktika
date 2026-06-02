from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, ttk

from PIL import Image, ImageDraw, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg

from data_visual import DEFAULT_CMAP, VisualApp


DEFAULT_BRUSH_WIDTH = 9
DEFAULT_BRUSH_COLOR = "#161159"
STUDENT_ID = "70221789"
SURNAME = "Анисимов"
OUTPUT_DIR = Path(__file__).resolve().parent


class DrawApp(VisualApp):
    def __init__(self, root: tk.Tk) -> None:
        self.draw_enabled = False
        self.brush_color = tk.StringVar(value=DEFAULT_BRUSH_COLOR)
        self.brush_width = tk.IntVar(value=DEFAULT_BRUSH_WIDTH)
        self._base_image: Image.Image | None = None
        self._draw_image: Image.Image | None = None
        self._image_before_last_line: Image.Image | None = None
        self._active_line: list[tuple[int, int]] = []
        self._last_line: list[tuple[int, int]] = []
        super().__init__(root)
        self.root.title("Visualization drawing tools")

    def _build_layout(self) -> None:
        super()._build_layout()

        tools = ttk.Frame(self.root, padding=8)
        tools.grid(row=1, column=1, sticky="ew")

        self.draw_button = ttk.Button(tools, text="Draw", command=self.toggle_draw)
        self.draw_button.pack(side="left", padx=2)

        self.color_button = tk.Button(
            tools,
            width=3,
            bg=self.brush_color.get(),
            command=self.choose_color,
            relief=tk.RAISED,
        )
        self.color_button.pack(side="left", padx=6)

        ttk.Label(tools, text="Width").pack(side="left")
        width_spin = ttk.Spinbox(tools, from_=1, to=30, textvariable=self.brush_width, width=4)
        width_spin.pack(side="left", padx=4)

        self.canvas.bind("<ButtonPress-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.finish_line)
        self.canvas.bind("<ButtonPress-3>", lambda _event: self.disable_draw())
        self.root.bind("<Control-z>", self.undo_last_line)

    def set_x_column(self, column: str) -> None:
        self.disable_draw()
        super().set_x_column(column)

    def set_y_column(self, column: str) -> None:
        self.disable_draw()
        super().set_y_column(column)

    def toggle_draw(self) -> None:
        if self.draw_enabled:
            self.disable_draw()
            return
        self.draw_enabled = True
        self.draw_button.state(["pressed"])
        self.canvas.configure(cursor="pencil")

    def disable_draw(self) -> None:
        self.draw_enabled = False
        if hasattr(self, "draw_button"):
            self.draw_button.state(["!pressed"])
        if hasattr(self, "canvas"):
            self.canvas.configure(cursor="")
        self._active_line = []

    def choose_color(self) -> None:
        color = colorchooser.askcolor(color=self.brush_color.get())[1]
        if color:
            self.brush_color.set(color)
            self.color_button.configure(bg=color)

    def start_line(self, event: tk.Event) -> None:
        if not self.draw_enabled or self._draw_image is None:
            return
        self._image_before_last_line = self._draw_image.copy()
        self._active_line = [(int(event.x), int(event.y))]
        self._paint_square(int(event.x), int(event.y))
        self._refresh_canvas_image()

    def draw_line(self, event: tk.Event) -> None:
        if not self.draw_enabled or self._draw_image is None or not self._active_line:
            return
        point = (int(event.x), int(event.y))
        previous = self._active_line[-1]
        draw = ImageDraw.Draw(self._draw_image)
        draw.line([previous, point], fill=self.brush_color.get(), width=self.brush_width.get())
        self._active_line.append(point)
        self._refresh_canvas_image()

    def finish_line(self, _event: tk.Event) -> None:
        if not self._active_line:
            return
        self._last_line = self._active_line[:]
        self._active_line = []

    def undo_last_line(self, _event: tk.Event | None = None) -> None:
        if self._active_line or not self._last_line or self._image_before_last_line is None:
            return
        self._draw_image = self._image_before_last_line.copy()
        self._image_before_last_line = None
        self._last_line = []
        self._refresh_canvas_image()

    def update_plot(self) -> None:
        figure = self.create_figure()
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        width, height = canvas.get_width_height()
        self._base_image = Image.frombytes("RGBA", (width, height), canvas.buffer_rgba())
        self._draw_image = self._base_image.copy()
        self._image_before_last_line = None
        self._last_line = []
        self._refresh_canvas_image()

    def save_graph(self) -> Path:
        graphs_dir = OUTPUT_DIR / "graphs"
        graphs_dir.mkdir(exist_ok=True)
        filename = datetime.now().strftime("graph%H_%M_%S.png")
        path = graphs_dir / filename
        counter = 1
        while path.exists():
            path = graphs_dir / f"{path.stem}_{counter}.png"
            counter += 1
        if self._draw_image is not None:
            self._draw_image.save(path)
        else:
            self.create_figure().savefig(path, dpi=120)
        return path

    def _paint_square(self, x: int, y: int) -> None:
        if self._draw_image is None:
            return
        half = self.brush_width.get() // 2
        draw = ImageDraw.Draw(self._draw_image)
        draw.rectangle([x - half, y - half, x + half, y + half], fill=self.brush_color.get())

    def _refresh_canvas_image(self) -> None:
        if self._draw_image is None:
            return
        self._photo = ImageTk.PhotoImage(self._draw_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)


def main() -> None:
    root = tk.Tk()
    app = DrawApp(root)
    app.cmap.set(DEFAULT_CMAP)
    app.update_plot()
    root.mainloop()


if __name__ == "__main__":
    main()
