import datetime
from typing import Dict

from vigilant_crypto_snatch.feargreed.interface import FearAndGreedException
from vigilant_crypto_snatch.feargreed.interface import FearAndGreedIndex
from vigilant_crypto_snatch.myrequests import HttpRequestError
from vigilant_crypto_snatch.myrequests import perform_http_request


def alternative_me_fear_and_greed() -> Dict:
    return perform_http_request("https://api.alternative.me/fng/")


def stub_alternative_me_fear_and_greed() -> Dict:
    return {
        "name": "Fear and Greed Index",
        "data": [
            {
                "value": "25",
                "value_classification": "Extreme Fear",
                "timestamp": "1639958400",
                "time_until_update": "62507",
            }
        ],
        "metadata": {"error": None},
    }


class AlternateMeFearAndGreedIndex(FearAndGreedIndex):
    def __init__(self, test=False):
        if test:
            self.api = stub_alternative_me_fear_and_greed
        else:
            self.api = alternative_me_fear_and_greed

    def get_value(self, now: datetime.datetime) -> int:
        try:
            response = self.api()
            return int(response["data"][0]["value"])
        except KeyError as e:
            raise FearAndGreedException("Data key was missing in API response") from e
        except HttpRequestError as e:
            raise FearAndGreedException(
                "Connection error to the Fear & Greed API"
            ) from e
