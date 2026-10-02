"""Модуль «Калькулятор»: базовые арифметические операции."""
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox,
)

from superapp.core.module_base import AppModule


ALLOWED = re.compile(r"^[0-9+\-*/(). %]+$")


class CalculatorModule(AppModule):
    id = "calculator"
    title = "Калькулятор"
    icon = "🧮"
    ready = True

    def create_widget(self, core) -> QWidget:
        return CalculatorPage(core)


class CalculatorPage(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        # --- Дисплей ---
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(64)
        self.display.setStyleSheet(
            "QLineEdit{font-size:28px;padding:8px 12px;"
            "background:#fff;border:1px solid #c9cfdb;border-radius:6px;}"
        )
        self.display.returnPressed.connect(self._evaluate)
        root.addWidget(self.display)

        # --- Подсказка ---
        hint = QLabel("Поддерживается ввод с клавиатуры. Enter — вычислить, C — очистить.")
        hint.setStyleSheet("color:#777;font-size:12px;")
        root.addWidget(hint)

        # --- Сетка кнопок ---
        grid = QGridLayout()
        grid.setSpacing(8)

        layout = [
            ["C",  "(", ")", "/"],
            ["7",  "8", "9", "*"],
            ["4",  "5", "6", "-"],
            ["1",  "2", "3", "+"],
            ["0",  ".", "⌫", "="],
        ]

        for r, row in enumerate(layout):
            for c, label in enumerate(row):
                btn = QPushButton(label)
                btn.setFixedHeight(56)
                btn.setStyleSheet(self._button_style(label))
                btn.clicked.connect(lambda _, t=label: self._on_button(t))
                grid.addWidget(btn, r, c)

        root.addLayout(grid)
        root.addStretch()

    @staticmethod
    def _button_style(label: str) -> str:
        base = (
            "QPushButton{font-size:18px;font-weight:600;"
            "background:#fff;border:1px solid #c9cfdb;border-radius:6px;}"
            "QPushButton:hover{background:#f2f5fb;}"
            "QPushButton:pressed{background:#e6ecf7;}"
        )
        if label == "=":
            base += "QPushButton{background:#4c8bf5;color:white;border:none;}"
        elif label in {"C", "⌫"}:
            base += "QPushButton{background:#fdecec;color:#c0392b;border-color:#f5c6c6;}"
        elif label in {"/", "*", "-", "+"}:
            base += "QPushButton{background:#eef3ff;color:#2c5fb8;}"
        return base

    # ---------- Логика ----------
    def _on_button(self, label: str):
        if label == "C":
            self.display.clear()
        elif label == "⌫":
            self.display.setText(self.display.text()[:-1])
        elif label == "=":
            self._evaluate()
        else:
            self.display.insert(label)

    def _evaluate(self):
        expr = self.display.text().strip()
        if not expr:
            return
        if not ALLOWED.match(expr):
            QMessageBox.warning(self, "Ошибка", "Недопустимые символы в выражении.")
            return
        try:
            result = eval(expr, {"__builtins__": {}}, {})  # без builtins
        except ZeroDivisionError:
            QMessageBox.warning(self, "Ошибка", "Деление на ноль.")
            return
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Не удалось вычислить выражение.")
            return

        if isinstance(result, float) and result.is_integer():
            result = int(result)
        self.display.setText(str(result))
        if self.core:
            self.core.publish("calculator.evaluated", expr)

    # ---------- Клавиатура ----------
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._evaluate()
        elif key == Qt.Key_Escape:
            self.display.clear()
        elif key == Qt.Key_Backspace:
            self.display.setText(self.display.text()[:-1])
        else:
            # Разрешаем набор цифр и операторов
            text = event.text()
            if text and text in "0123456789+-*/(). ":
                self.display.insert(text)
            else:
                super().keyPressEvent(event)
