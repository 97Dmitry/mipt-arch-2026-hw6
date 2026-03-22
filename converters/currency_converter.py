from __future__ import annotations

from abc import ABC, abstractmethod


class CurrencyConverter(ABC):
    @abstractmethod
    def convert(self, amount_usd: float, target_currency: str) -> float:
        """Convert an amount in USD to the requested target currency."""
