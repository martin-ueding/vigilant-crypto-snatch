import datetime
from typing import Dict

from ..myrequests import HttpRequestError
from ..myrequests import perform_http_request
from .interface import FearAndGreedException
from .interface import FearAndGreedIndex


def alternative_me_fear_and_greed(limit: int = 1) -> Dict:
    return perform_http_request(f"https://api.alternative.me/fng/?limit={limit}")


def stub_alternative_me_fear_and_greed(limit: int) -> Dict:
    assert limit <= 2, "Larger limits than 2 are not supported by the stub."
    return {
        "name": "Fear and Greed Index",
        "data": [
            {
                "value": "45",
                "value_classification": "Fear",
                "timestamp": "1640131200",
                "time_until_update": "44701",
            },
            {"value": "27", "value_classification": "Fear", "timestamp": "1640044800"},
        ],
        "metadata": {"error": None},
    }


cached_values: Dict[datetime.date, int] = {}


class AlternateMeFearAndGreedIndex(FearAndGreedIndex):
    def __init__(self, test=False):
        if test:
            self.api = stub_alternative_me_fear_and_greed
        else:
            self.api = alternative_me_fear_and_greed

    def get_value(self, now: datetime.date, today: datetime.date) -> int:
        if now not in cached_values:
            days_since = (today - now).days + 1
            try:
                response = self.api(days_since)
                for elem in response["data"]:
                    then = datetime.date.fromtimestamp(int(elem["timestamp"]))
                    cached_values[then] = int(elem["value"])
                print(cached_values)
            except KeyError as e:
                raise FearAndGreedException(
                    "Data key was missing in API response"
                ) from e
            except HttpRequestError as e:
                raise FearAndGreedException(
                    "Connection error to the Fear & Greed API"
                ) from e

        return cached_values[now]
