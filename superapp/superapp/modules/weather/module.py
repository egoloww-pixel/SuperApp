"""Модуль «Погода»: текущая погода + прогноз на 5 дней."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QGridLayout,
)

from superapp.core.module_base import AppModule
from superapp.modules.weather.openweather_client import OpenMeteoClient


WEATHER_CODES = {
    0: "☀️ Ясно", 1: "🌤 Преимущ. ясно", 2: "⛅ Переменная облачность",
    3: "☁️ Пасмурно", 45: "🌫 Туман", 48: "🌫 Изморозь",
    51: "🌦 Слабая морось", 53: "🌦 Морось", 55: "🌦 Сильная морось",
    61: "🌧 Слабый дождь", 63: "🌧 Дождь", 65: "🌧 Сильный дождь",
    71: "🌨 Слабый снег", 73: "🌨 Снег", 75: "🌨 Сильный снег",
    80: "🌦 Ливень", 81: "🌦 Сильный ливень", 82: "⛈ Очень сильный ливень",
    95: "⛈ Гроза", 96: "⛈ Гроза с градом", 99: "⛈ Сильная гроза",
}


class WeatherModule(AppModule):
    id = "weather"
    title = "Погода"
    icon = "🌤"
    ready = True

    def create_widget(self, core) -> QWidget:
        return WeatherPage(core)


class WeatherPage(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.client = OpenMeteoClient()
        self._place = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # --- Поиск города ---
        row = QHBoxLayout()
        self.input_city = QLineEdit()
        self.input_city.setPlaceholderText("Введите город, например: Москва")
        self.input_city.returnPressed.connect(self._search)
        row.addWidget(self.input_city, stretch=1)

        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self._search)
        row.addWidget(self.btn_search)
        root.addLayout(row)

        # --- Карточка текущей погоды ---
        self.card = QFrame()
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setStyleSheet(
            "QFrame{background:#ffffff;border:1px solid #dde2ec;border-radius:6px;}"
        )
        card_layout = QGridLayout(self.card)

        self.lbl_city = QLabel("—")
        self.lbl_city.setStyleSheet("font-size:18px;font-weight:600;")
        card_layout.addWidget(self.lbl_city, 0, 0, 1, 2)

        self.lbl_cond = QLabel("Введите город и нажмите «Найти»")
        self.lbl_cond.setStyleSheet("color:#666;")
        card_layout.addWidget(self.lbl_cond, 1, 0, 1, 2)

        self.lbl_temp = QLabel("—")
        self.lbl_temp.setStyleSheet("font-size:42px;font-weight:700;color:#4c8bf5;")
        card_layout.addWidget(self.lbl_temp, 2, 0, 1, 2)

        self.lbl_hum = QLabel("Влажность: —")
        self.lbl_wind = QLabel("Ветер: —")
        card_layout.addWidget(self.lbl_hum, 3, 0)
        card_layout.addWidget(self.lbl_wind, 3, 1)

        root.addWidget(self.card)

        # --- Прогноз на 5 дней ---
        root.addWidget(QLabel("Прогноз на 5 дней"))
        self.forecast_grid = QGridLayout()
        root.addLayout(self.forecast_grid)
        root.addStretch()

    def _search(self):
        city = self.input_city.text().strip()
        if not city:
            return
        try:
            place = self.client.geocode(city)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Сбой запроса:\n{e}")
            return
        if not place:
            QMessageBox.information(self, "Не найдено", f"Город «{city}» не найден.")
            return
        self._place = place
        self._load_all()

    def _load_all(self):
        p = self._place
        try:
            cur = self.client.current(p["latitude"], p["longitude"])
            fc = self.client.forecast(p["latitude"], p["longitude"], days=5)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить погоду:\n{e}")
            return

        self.lbl_city.setText(f"{p['name']}, {p['country']}")
        self.lbl_cond.setText(WEATHER_CODES.get(cur["code"], "—"))
        self.lbl_temp.setText(f"{cur['temperature']:.0f} °C")
        self.lbl_hum.setText(f"Влажность: {cur['humidity']} %")
        self.lbl_wind.setText(f"Ветер: {cur['wind']:.1f} км/ч")

        # Очищаем старый прогноз
        while self.forecast_grid.count():
            item = self.forecast_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for col, (d, tmax, tmin) in enumerate(
            zip(fc["dates"], fc["temp_max"], fc["temp_min"])
        ):
            box = QFrame()
            box.setStyleSheet(
                "QFrame{background:#fff;border:1px solid #dde2ec;border-radius:6px;}"
                "QLabel{border:none;}"
            )
            vb = QVBoxLayout(box)
            day = QLabel(d[5:])          # MM-DD
            hi = QLabel(f"{tmax:.0f}°")
            lo = QLabel(f"{tmin:.0f}°")
            hi.setStyleSheet("font-weight:700;color:#e5534b;")
            lo.setStyleSheet("font-weight:700;color:#4c8bf5;")
            day.setAlignment(Qt.AlignCenter)
            hi.setAlignment(Qt.AlignCenter)
            lo.setAlignment(Qt.AlignCenter)
            vb.addWidget(day)
            vb.addWidget(hi)
            vb.addWidget(lo)
            self.forecast_grid.addWidget(box, 0, col)

        if self.core:
            self.core.publish("weather.updated", p["name"])
