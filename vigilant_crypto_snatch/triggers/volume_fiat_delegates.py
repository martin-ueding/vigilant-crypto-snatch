from ..marketplace import Marketplace


class VolumeFiatDelegate(object):
    def get_volume_fiat(self) -> float:
        raise NotImplementedError()  # pragma: no cover


class FixedVolumeFiatDelegate(VolumeFiatDelegate):
    def __init__(self, volume_fiat: float):
        self.volume_fiat = volume_fiat

    def get_volume_fiat(self) -> float:
        return self.volume_fiat

    def __str__(self) -> str:
        return f"Fixed(volume_fiat={self.volume_fiat})"  # pragma: no cover


class RatioVolumeFiatDelegate(VolumeFiatDelegate):
    def __init__(self, fiat: str, percentage_fiat: float, market: Marketplace):
        self.fiat = fiat
        self.market = market
        self.percentage_fiat = percentage_fiat

    def get_volume_fiat(self) -> float:
        balances = self.market.get_balance()
        balance_fiat = balances[self.fiat]
        return balance_fiat * self.percentage_fiat / 100

    def __str__(self) -> str:
        return f"Ratio(percentage_fiat={self.percentage_fiat})"  # pragma: no cover
