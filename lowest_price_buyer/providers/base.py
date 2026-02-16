from __future__ import annotations

from abc import ABC, abstractmethod

import requests

from lowest_price_buyer.models import Offer


class ProviderError(RuntimeError):
    pass


class BaseProvider(ABC):
    name: str

    @abstractmethod
    def fetch(self, keyword: str, max_results: int = 5) -> list[Offer]:
        raise NotImplementedError


def fetch_json(url: str, params: dict, timeout: int = 20) -> dict:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()
