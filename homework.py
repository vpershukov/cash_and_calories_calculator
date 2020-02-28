import datetime as dt
import requests
import private_data


class Record:

    def __init__(self,amount, comment, date=None):
        self.amount = amount
        self.comment = comment
        if date is not None:
            self.date = dt.datetime.strptime(date, "%d.%m.%Y").date()
        else:
            self.date = dt.date.today()


class Calculator:

    def __init__(self, limit):
        self.limit = limit
        self.records = []

    def add_record(self, record):
        self.records.append(record)
        return self.records

    def get_today_stats(self):
        today = dt.date.today()
        day_costs = sum([record.amount for record in self.records if record.date == today])
        return day_costs

    def get_week_stats(self):
        today = dt.date.today()
        delta = dt.timedelta(days=7)
        week_costs = sum([record.amount for record in self.records if record.date >= today - delta])
        return week_costs


class CaloriesCalculator(Calculator):

    def get_calories_remained(self):
        spent = self.get_today_stats()
        if self.limit > spent:
            return "Сегодня можно съесть что-нибудь ещё, но c общей калорийностью не более {count} кКал".format(
            count = self.limit - spent
            )
        else:
            return "Хватит есть!"


class CashCalculator(Calculator):
    # Request to get currency rates
    # 1K requests per day allowed only
    url = "https://currate.ru/api/?get=rates&pairs=USDRUB,EURRUB&key={api_key}".format(
    api_key = private_data.api_key
    )
    rates = requests.get(url).json()

    USD_RATE = float(rates["data"]["USDRUB"])
    EURO_RATE = float(rates["data"]["EURRUB"])

    def get_today_cash_remained(self, currency_code="rub"):
        spent = self.get_today_stats()
        currencies = {
            "rub": ("руб", 1),
            "usd": ("USD", self.USD_RATE),
            "eur": ("Euro", self.EURO_RATE)
        }

        if self.limit > spent:
            left_limit = self.limit - spent
            if currency_code != "rub":
                left_limit = round(left_limit / currencies[currency_code][1], 2)
            return "На сегодня осталось {left_limit} {currency}".format(
                left_limit=left_limit, currency=currencies[currency_code][0]
                )
        elif self.limit == spent:
            return "Денег нет, держись"
        else:
            debt = spent - self.limit
            if currency_code != "rub":
                debt = round(debt / currencies[currency_code][1], 2)
            return "Денег нет, держись: твой долг - {debt} {currency}".format(
                debt=debt, currency=currencies[currency_code][0]
                )
