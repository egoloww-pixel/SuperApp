from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from superapp.core.module_base import AppModule


class NotesModule(AppModule):
    id = "notes"
    title = "Заметки"
    icon = "📝"
    ready = False

    def create_widget(self, core) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Модуль «Заметки» в разработке 🚧")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        return w
