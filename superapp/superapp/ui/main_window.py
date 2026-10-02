from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, QListWidgetItem,
    QStackedWidget, QLabel, QVBoxLayout
)


class MainWindow(QMainWindow):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setWindowTitle("SuperApp")
        self.resize(1100, 720)

        # --- Центральный виджет ---
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Sidebar ---
        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        self.nav.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self.nav)

        # --- Stacked pages ---
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        # --- Заголовок ---
        header = QLabel("SuperApp — модульные утилиты")
        header.setStyleSheet("padding:8px 16px; font-size:14px; color:#555;")
        self.setStatusBar(self.statusBar())
        self.statusBar().addWidget(header)

        self._populate()

    def _populate(self):
        for mod in self.core.modules():
            item = QListWidgetItem(f"{mod.icon}  {mod.title}" +
                                   ("" if mod.ready else "  (скоро)"))
            item.setData(Qt.UserRole, mod.id)
            self.nav.addItem(item)

            widget = mod.create_widget(self.core)
            self.stack.addWidget(widget)

        if self.nav.count() > 0:
            self.nav.setCurrentRow(0)

    def _on_nav_changed(self, row: int):
        if 0 <= row < self.stack.count():
            self.stack.setCurrentIndex(row)
