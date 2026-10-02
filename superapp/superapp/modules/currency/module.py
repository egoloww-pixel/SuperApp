from datetime import date, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QDateEdit
)
from PySide6.QtCore import QDate

from superapp.core.module_base import AppModule
from superapp.modules.currency.cbr_client import CbrClient
from superapp.modules.currency.chart_widget import ChartWidget


class CurrencyModule(AppModule):
    id = "currency"
    title = "Валюты"
    icon = "💱"
    ready = True

    def create_widget(self, core) -> QWidget:
        return CurrencyPage(core)


class CurrencyPage(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.client = CbrClient()

        self._build_ui()
        self._load_today()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # --- Панель управления ---
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Валюта:"))
        self.combo_ccy = QComboBox()
        for code in ["USD", "EUR", "CNY", "GBP", "JPY", "KZT", "TRY", "BYN"]:
            self.combo_ccy.addItem(code)
        controls.addWidget(self.combo_ccy)

        controls.addWidget(QLabel("С:"))
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        controls.addWidget(self.date_from)

        controls.addWidget(QLabel("По:"))
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        controls.addWidget(self.date_to)

        self.btn_refresh = QPushButton("Обновить курс")
        self.btn_refresh.clicked.connect(self._load_today)
        controls.addWidget(self.btn_refresh)

        self.btn_plot = QPushButton("Построить график")
        self.btn_plot.clicked.connect(self._load_dynamic)
        controls.addWidget(self.btn_plot)

        controls.addStretch()
        root.addLayout(controls)

        # --- Таблица текущих курсов ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Код", "Название", "Номинал", "Курс, ₽"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        root.addWidget(self.table, stretch=1)

        # --- График ---
        self.chart = ChartWidget()
        root.addWidget(self.chart, stretch=2)

    # ---------- Загрузка текущего курса ----------
    def _load_today(self):
        try:
            data = self.client.currencies_today()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить курс:\n{e}")
            return

        self.table.setRowCount(len(data))
        for row, (code, info) in enumerate(sorted(data.items())):
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(info["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(info["nominal"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{info['value']:.4f}"))
        self.table.resizeColumnsToContents()

    # ---------- Загрузка исторической динамики ----------
    def _load_dynamic(self):
        code = self.combo_ccy.currentText()
        d_from = self.date_from.date().toPython()
        d_to = self.date_to.date().toPython()
        if d_from >= d_to:
            QMessageBox.warning(self, "Период", "Дата 'С' должна быть раньше даты 'По'.")
            return

        try:
            series = self.client.dynamic(code, d_from, d_to)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить динамику:\n{e}")
            return

        if not series:
            QMessageBox.information(self, "Нет данных", "За выбранный период данных нет.")
            return

        self.chart.plot(code, series)
