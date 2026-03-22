from __future__ import annotations

from .currency_converter import CurrencyConverter
from .exchange_rate_provider import ExchangeRateProvider


class UsdCurrencyConverter(CurrencyConverter):
    def __init__(self, rate_provider: ExchangeRateProvider) -> None:
        self._rate_provider = rate_provider

    def convert(self, amount_usd: float, target_currency: str) -> float:
        rates = self._rate_provider.get_rates()
        currency_code = target_currency.upper()

        try:
            rate = rates[currency_code]
        except KeyError as error:
            raise ValueError(f"Unsupported currency: {currency_code}") from error

        return amount_usd * rate
