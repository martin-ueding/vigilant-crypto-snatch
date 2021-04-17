import sys

import streamlit as st
import streamlit.cli as st_cli
import altair as alt
import pandas as pd
import numpy as np

from vigilant_crypto_snatch import evaluation
from vigilant_crypto_snatch import configuration


def ui():
    config = configuration.load_config()
    st.title('Vigilant Crypto Snatch Evaluation')

    coin = st.selectbox('Coin', ['BTC', 'ETH'])
    fiat = st.selectbox('Fiat', ['EUR', 'USD'])

    data = evaluation.get_hourly_data(coin, fiat, config["cryptocompare"]["api_key"])
    data = evaluation.make_dataframe_from_json(data)

    st.markdown('# Close price')

    st.dataframe(data)

    close_chart = alt.Chart(data).mark_line().encode(x=alt.X('datetime', title='Date'), y=alt.X('close', title=f'Close {fiat}/{coin}'))
    st.altair_chart(close_chart, use_container_width=True)
    # st.line_chart(data['close'])

    st.markdown('# Drop survey')

    range_delay = st.slider('Delay / hours', min_value=1, max_value=14*24, value=(1, 48))
    range_percentage = st.slider('Drop / %', min_value=0, max_value=100, value=(1, 30))
    print(range_percentage)
    hours, drops, factors = evaluation.drop_survey(data, np.arange(*range_delay), np.linspace(*range_percentage, 15) / 100.0)
    x, y = np.meshgrid(hours, drops)
    survey_long = pd.DataFrame({'hours': x.ravel(),
                     'drop': [f'{yy:05.2f}' for yy in y.ravel() * 100],
                     'factor': factors.ravel()})

    survey_chart = alt.Chart(survey_long).mark_rect().encode(
        x=alt.X('hours:O', title='Delay / hours'),
        y=alt.Y('drop:O', title='Drop / %'),
        color=alt.Color('factor:Q', title=f'{coin}/{fiat}', scale=alt.Scale(scheme='turbo'))
    )
    st.altair_chart(survey_chart, use_container_width=True)


if __name__ == '__main__' and st._is_running_with_streamlit:
    ui()

def main(options):
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(st_cli.main())