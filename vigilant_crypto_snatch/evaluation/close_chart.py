import altair as alt
import pandas as pd


def make_close_chart(data: pd.DataFrame, coin: str, fiat: str):
    chart = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("datetime", title="Date"),
            y=alt.X("close", title=f"Close {fiat}/{coin}"),
        )
        .interactive()
    )
    return chart
