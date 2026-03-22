from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class ExchangeRateProvider:
    def __init__(
        self,
        api_url: str = "https://api.exchangerate-api.com/v4/latest/USD",
        cache_file: str = "exchange_rates.json",
        cache_expiry_seconds: int = 3600,
        max_retries: int = 3,
        retry_delay_seconds: int = 2,
    ) -> None:
        self.api_url = api_url
        self.cache_file = Path(cache_file)
        self.cache_expiry_seconds = cache_expiry_seconds
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.logger = logging.getLogger(__name__)

    def get_rates(self) -> dict[str, float]:
        cached_rates = self._load_from_cache()
        if cached_rates is not None:
            return cached_rates

        return self._load_from_api()

    def _load_from_cache(self) -> dict[str, float] | None:
        if not self.cache_file.exists():
            return None

        try:
            with self.cache_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            self.logger.warning("Failed to read cache file: %s", error)
            return None

        timestamp = data.get("timestamp")
        rates = data.get("rates")
        if not isinstance(timestamp, (int, float)) or not isinstance(rates, dict):
            self.logger.warning("Cache file has an invalid format.")
            return None

        if time.time() - timestamp >= self.cache_expiry_seconds:
            return None

        return rates

    def _save_to_cache(self, rates: dict[str, float]) -> None:
        payload = {"timestamp": time.time(), "rates": rates}
        try:
            with self.cache_file.open("w", encoding="utf-8") as file:
                json.dump(payload, file)
        except OSError as error:
            self.logger.warning("Failed to save cache file: %s", error)

    def _load_from_api(self) -> dict[str, float]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with urlopen(self.api_url, timeout=10) as response:
                    data = json.load(response)
                rates = data["rates"]
                if not isinstance(rates, dict):
                    raise ValueError("API returned invalid rates format.")

                self._save_to_cache(rates)
                return rates
            except (HTTPError, URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
                last_error = error
                self.logger.warning(
                    "Failed to fetch exchange rates (attempt %s/%s): %s",
                    attempt,
                    self.max_retries,
                    error,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_seconds)

        raise RuntimeError("Unable to fetch exchange rates.") from last_error
