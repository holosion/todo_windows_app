"""Confetti animation - a small celebration overlay when all tasks are done."""
from __future__ import annotations

import random
import tkinter as tk
from typing import List, Tuple


_COLORS = [
    "#22C55E", "#0EA5E9", "#F59E0B", "#EF4444", "#A855F7",
    "#EC4899", "#14B8A6", "#FACC15",
]


class ConfettiOverlay:
    """Drop colorful confetti pieces for ~2.5 seconds, then close."""

    DURATION_MS = 2500
    PIECE_COUNT = 80

    def __init__(self, parent: tk.Misc) -> None:
        self.parent = parent
        self._pieces: List[Tuple[int, dict]] = []
        self._canvas = tk.Canvas(
            parent, highlightthickness=0, bd=0, bg="", width=parent.winfo_width(),
            height=parent.winfo_height(),
        )
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._canvas.bind("<Configure>", self._on_resize)
        self._start_time = parent.after(0, self._tick)
        self._after_close = parent.after(self.DURATION_MS, self.close)

    def _on_resize(self, _event) -> None:
        self._canvas.configure(
            width=self.parent.winfo_width(),
            height=self.parent.winfo_height(),
        )

    def _seed(self) -> None:
        w = max(self._canvas.winfo_width(), 800)
        h = max(self._canvas.winfo_height(), 600)
        for _ in range(self.PIECE_COUNT):
            x = random.randint(0, w)
            y = random.randint(-h, 0)
            color = random.choice(_COLORS)
            piece = self._canvas.create_rectangle(
                x, y, x + 8, y + 14, fill=color, outline=color
            )
            dx = random.uniform(-2, 2)
            dy = random.uniform(2, 6)
            self._pieces.append((piece, {"dx": dx, "dy": dy, "color": color}))

    def _tick(self) -> None:
        if not self._pieces:
            self._seed()
        for piece, props in self._pieces:
            self._canvas.move(piece, props["dx"], props["dy"])
            props["dy"] += 0.15
            if self._canvas.coords(piece)[1] > self._canvas.winfo_height() + 30:
                self._canvas.move(piece, 0, -self._canvas.winfo_height() - 60)
        self._start_time = self.parent.after(20, self._tick)

    def close(self) -> None:
        for ref in (self._start_time, self._after_close):
            try:
                self.parent.after_cancel(ref)
            except Exception:
                pass
        try:
            self._canvas.destroy()
        except Exception:
            pass
