import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger()


class BinanceClientError(Exception):
    pass


class BinanceFuturesClient:
    """Thin wrapper around Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        params = params or {}

        if signed:
            params = self._sign(params)

        logger.debug("API REQUEST  | %s %s | params: %s", method.upper(), endpoint, params)

        try:
            response = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error while calling %s: %s", url, exc)
            raise BinanceClientError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out for %s", url)
            raise BinanceClientError("Request timed out. Please try again.")

        logger.debug(
            "API RESPONSE | %s %s | status: %s | body: %s",
            method.upper(),
            endpoint,
            response.status_code,
            response.text,
        )

        try:
            data = response.json()
        except ValueError:
            raise BinanceClientError(f"Non-JSON response from API: {response.text}")

        if response.status_code != 200:
            code = data.get("code", response.status_code)
            msg = data.get("msg", response.text)
            logger.error("API error %s: %s", code, msg)
            raise BinanceClientError(f"API error {code}: {msg}")

        return data

    # ------------------------------------------------------------------ #
    #  Public methods                                                      #
    # ------------------------------------------------------------------ #

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def new_order(self, **kwargs) -> Dict[str, Any]:
        """Place a new futures order. All keyword args are passed to the API."""
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )
