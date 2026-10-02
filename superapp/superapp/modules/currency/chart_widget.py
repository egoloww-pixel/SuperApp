from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, alpha=0.3)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self._placeholder()

    def _placeholder(self):
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        self.ax.text(0.5, 0.5, "Выберите валюту и период",
                     ha="center", va="center", transform=self.ax.transAxes)
        self.canvas.draw()

    def plot(self, code: str, series: list[tuple]):
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        xs = [p[0] for p in series]
        ys = [p[1] for p in series]
        self.ax.plot(xs, ys, marker="o", markersize=3, linewidth=1.5)
        self.ax.set_title(f"Динамика курса {code} к RUB")
        self.ax.set_xlabel("Дата")
        self.ax.set_ylabel("Рубли за 1 ед.")
        self.figure.autofmt_xdate()
        self.canvas.draw()
