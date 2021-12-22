import altair as alt
import pandas as pd


def make_close_chart(data: pd.DataFrame, coin: str, fiat: str) -> alt.Chart:
    chart = (
        alt.Chart(data, title="Coin Closing Price")
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Date"),
            y=alt.X("close", title=f"Close {fiat}/{coin}"),
        )
        .interactive()
    )
    return chart
