# Trigger Simulator

It is not inherently clear how triggers should be set. There are multiple variables that have to be tuned for *each* trigger:

- Time delay
- Cooloff
- Drop percentage
- Fiat volume

We can try to verify a given strategy using historical data. We can also use the historical data to get an idea of a good strategy. Then we just simulate the given triggers and see how they perform.

We provide a fun experimentation interface which is built with [Streamlit](https://streamlit.io/) and runs directly in your browser.

![](streamlit.png)

This interface can be [used online using the hosted version](https://share.streamlit.io/martin-ueding/vigilant-crypto-snatch/vigilant_crypto_snatch/streamlit_ui.py). Alternatively it can be started locally using the `evaluate` subcommand without any additional parameters:

```
vigilant-crypto-snatch evaluate
```

You can then select a crypto and a fiat currency to use for the analysis. Then you can just switch between the various tools that are offered. These are described below.

## Possible errors

It might be possible that you cannot start the Streamlit interface. The most basic error could be an `ImportError` saying that the package `altair` or `streamlit` could not be imported. In that case you haven't installed the evaluation extra. See the installation instructions on the front page.

While starting it, you might get an error about too many files connected via inotify. In this case you need to create a file at `.streamlit/config.toml` and give it this content:

```toml
[server]
fileWatcherType = "none"
```

## Price tool

Here you can just see the prices that we got from the historical API. This is nothing special, just a plot.

> ![](price-plot.png)

These plots are slightly interactive, so you can make them fullscreen and they will render with higher quality.

## Trigger simulation tool

You simulate triggers on historical data. You can limit the evaluation data to a given range. Unfortunately Streamlit doesn't support a range slider yet, so the numbers don't make so much sense. The actual date is shown right below and will be updated as you move the slider.

> ![](triggers-date-range.png)

You can simulate as many triggers as you like. Set the number that you want and then just select the type of trigger and tune the parameters to your liking.

> ![](trigger-parameters.png)

It will give you a summary table looks like this:

![](triggers-summary-table.png)

You can make this table full screen and also sort by any column. Just click on a column header and it will sort.

You will also get a plot which shows the amount of money you have invested as well as the value of the crypto assets aquired. With this you can get a sense on the gains.

> ![](trigger-plot.png)

The plot is interactive, you can pan and zoom with the mouse.

You also have a table with the trades that were performed.

> ![](trigger-table.png)

In case the trigger has not been executed once, you will of course get a message.

## Drop survey tool

Fiddling with individual triggers can be informative, but a more meta view could be very helpful. For this all sorts of drop triggers are performed, with a grid of various delays and various drop percentages.

You can control the ranges of both with two-way sliders.

> ![](drop-sliders.png)

Each time such a trigger is executed a fixed unit of fiat currency is invested. At the end of the time period the amount of crypto currency is normalized by the amount of fiat currency spent. This will show the most efficient triggers. It doesn't show how often these triggers have been used, or how much crypto currency you will have in the end.

> ![](drop-heatmap.png)

In the resulting heat map you can see colored areas where the most gains are in a dark red. In regions where the trigger has never been executed, you will just see black. These regions indicate that there was no such drop in the period looked at.

Likely there will be one really dark area. This is an artefact from a single large drop in the past three months. Of course this is the best drop trigger for that particluar period, but it does not really generalize. So be wary that different historical periods look differently.

Use this plot to get a general sense of fluctuations in the market and which triggers would fire often and form a good base strategy. In the above image, having a trigger at around 10 % and 24 hours delay seems to be a reasonable choice.

You might still want to include some really ambitious triggers such that you can realize large gains. For instance having one for 25 % within 48 hours could be a good idea.

## Trade overview

When you use the evaluation interface locally with your database, you can also see an overview over all the recorded trades from the software.

There is one plot similar to the one shown by investment portfolio services. You can see the value of your bought coins and the spent fiat over time. The spent money is with the solid line, the value of your coins in the solid area. The plot is only updated when there is another trade, it doesn't try to look up historical prices in between.

![](evaluation-value-investment.svg)

Then there is an overview over the amount of fiat that was spent over the months:

![](evaluations-fiat-month.svg)

This can help you to keep your budget in check and potentially reduce the triggers a bit.

### Value with current price

Then we have plots which are potentially confusing because they compare historic investments with the current price. This means that the plots will change whenever you look at them again. It makes it a bit hard to evaluate the strategy, but perhaps they can be useful still.

One is with the gains from each trigger execution, compared to the current price:

![](evaluation-gains-individual.svg)

And also grouped by month:

![](evaluation-gains-month.svg)

Depending on the current price, everything will be shift up or down. It will change historic benefits as well. Likely the first plot is the easiest to understand.