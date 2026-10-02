"""Боковая навигационная панель."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class Sidebar(QListWidget):
    """Список модулей; данные — id модуля в Qt.UserRole."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("Sidebar")

    def add_module(self, module) -> None:
        label = f"{module.icon}  {module.title}"
        if not module.ready:
            label += "  (скоро)"
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, module.id)
        self.addItem(item)
