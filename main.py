from converters import ExchangeRateProvider, UsdCurrencyConverter


SUPPORTED_CURRENCIES = ("RUB", "EUR", "GBP", "CNY")


def read_amount() -> float:
    raw_value = input("Введите значение в USD:\n")
    try:
        return float(raw_value)
    except ValueError as error:
        raise ValueError("Введите число, например 10 или 10.5.") from error


def main() -> None:
    try:
        amount = read_amount()
        converter = UsdCurrencyConverter(ExchangeRateProvider())

        for currency in SUPPORTED_CURRENCIES:
            converted_amount = converter.convert(amount, currency)
            print(f"{amount} USD to {currency}: {converted_amount:.2f}")
    except (RuntimeError, ValueError) as error:
        print(f"Ошибка: {error}")

if __name__ == "__main__":
    main()
