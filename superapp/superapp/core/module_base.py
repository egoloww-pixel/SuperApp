from PySide6.QtWidgets import QWidget


class AppModule:
    """Базовый интерфейс утилиты SuperApp."""

    #: Уникальный идентификатор
    id: str = "base"
    #: Отображаемое имя
    title: str = "Модуль"
    #: Иконка (эмодзи или путь)
    icon: str = "🧩"
    #: Готов ли модуль к работе
    ready: bool = True

    def create_widget(self, core) -> QWidget:
        raise NotImplementedError
