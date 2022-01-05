import datetime

import altair as alt
import pandas as pd

from vigilant_crypto_snatch.feargreed import AlternateMeFearAndGreedIndex


def make_fear_greed_chart(
    time_begin: datetime.datetime, time_end: datetime.datetime
) -> alt.Chart:
    fear_greed_access = AlternateMeFearAndGreedIndex()

    date_range = pd.date_range(time_begin.date(), time_end.date())
    today = datetime.date.today()
    fear_greed_df = pd.DataFrame(
        {
            "date": date_range,
            "fear_greed_index": [
                fear_greed_access.get_value(date.date(), today) for date in date_range
            ],
        }
    )
    chart = (
        alt.Chart(fear_greed_df, title="Fear & Greed Index")
        .mark_line()
        .encode(
            alt.X("date", title="Date"),
            alt.Y("fear_greed_index", title="Fear & Greed Index"),
        )
        .interactive()
    )
    return chart
