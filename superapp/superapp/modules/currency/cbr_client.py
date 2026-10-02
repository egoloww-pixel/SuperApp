from datetime import date, timedelta
import xml.etree.ElementTree as ET
import requests


CBR_DAILY = "https://www.cbr.ru/scripts/XML_daily.asp"
CBR_DYNAMIC = "https://www.cbr.ru/scripts/XML_dynamic.asp"


class CbrClient:
    """Клиент API ЦБ РФ."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._session = requests.Session()

    def currencies_today(self) -> dict[str, dict]:
        """Возвращает {CharCode: {name, nominal, value, date}}."""
        r = self._session.get(CBR_DAILY, timeout=self.timeout)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        result = {}
        cbr_date = root.attrib.get("Date", "")
        for v in root.findall("Valute"):
            code = v.findtext("CharCode")
            result[code] = {
                "name": v.findtext("Name"),
                "nominal": int(v.findtext("Nominal")),
                "value": float(v.findtext("Value").replace(",", ".")),
                "date": cbr_date,
            }
        return result

    def dynamic(self, code: str, date_from: date, date_to: date) -> list[tuple[date, float]]:
        """Историческая динамика курса (за 1 единицу валюты)."""
        params = {
            "date_req1": date_from.strftime("%d/%m/%Y"),
            "date_req2": date_to.strftime("%d/%m/%Y"),
            "VAL_NM_RQ": self._valute_id(code),
        }
        r = self._session.get(CBR_DYNAMIC, params=params, timeout=self.timeout)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        points = []
        for rec in root.findall("Record"):
            d = rec.attrib["Date"]  # DD.MM.YYYY
            day, month, year = map(int, d.split("."))
            value = float(rec.findtext("Value").replace(",", "."))
            nominal = int(rec.findtext("Nominal"))
            points.append((date(year, month, day), value / nominal))
        return points

    def _valute_id(self, code: str) -> str:
        """Внутренний ID валюты на cbr.ru (например, R01235 для USD)."""
        mapping = {
            "USD": "R01235",
            "EUR": "R01239",
            "CNY": "R01375",
            "GBP": "R01035",
            "JPY": "R01820",
            "KZT": "R01335",
            "TRY": "R01700",
            "BYN": "R01090",
        }
        if code not in mapping:
            raise ValueError(f"Нет ID для валюты {code}")
        return mapping[code]
