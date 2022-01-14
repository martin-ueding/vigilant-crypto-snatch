import altair as alt
import pandas as pd

from ..core import AssetPair


def make_close_chart(data: pd.DataFrame, asset_pair: AssetPair) -> alt.Chart:
    chart = (
        alt.Chart(data, title="Coin Closing Price")
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Date"),
            y=alt.X("close", title=f"Close {asset_pair.fiat}/{asset_pair.coin}"),
        )
        .interactive()
    )
    return chart
