"""Точка входа SuperApp."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from superapp.core.app_core import AppCore
from superapp.ui.main_window import MainWindow
from superapp.modules.currency.module import CurrencyModule
from superapp.modules.weather.module import WeatherModule
from superapp.modules.calculator.module import CalculatorModule
from superapp.modules.notes.module import NotesModule


def load_stylesheet(app: QApplication) -> None:
    """Загружает QSS-тему, если файл существует."""
    qss = Path(__file__).parent / "superapp" / "resources" / "styles.qss"
    if qss.exists():
        app.setStyleSheet(qss.read_text(encoding="utf-8"))


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SuperApp")
    app.setOrganizationName("SuperApp")

    load_stylesheet(app)

    core = AppCore()
    core.register(CurrencyModule)      # 💱 Валюты
    core.register(WeatherModule)       # 🌤 Погода
    core.register(CalculatorModule)    # 🧮 Калькулятор
    core.register(NotesModule)         # 📝 Заметки (заглушка)

    window = MainWindow(core)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
