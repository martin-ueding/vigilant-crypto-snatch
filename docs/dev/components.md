# Components

This project aims to be organized according to the [*Clean Architecture*](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html). There are many components, and they only depend on each other in a acyclic way.

On this page we will go through all the components and how they interact with each other. This shall give you an overview of the architecture of this software.

## Core

At the center there are the core entities, the data classes which don't depend on anything else. These are the classes representing `Price` and `Trade`, as well as the specification for the triggers, the `TriggerSpec`.

[![](graphs/core.svg)](graphs/core.svg)

These are implemented as `dataclasses`.

## Datastore

The next component is the data storage. We have an interface which allows to store price and trade objects and retrieve them. We also have a clean-up operation, and two specific queries.

[![](graphs/datastore.svg)](graphs/datastore.svg)

It is implemented using simple lists for testing, and also using the SQL Alchemy library. One can see that although this depends on an external library, it is only used in a concrete implementation of the interface. The other code doesn't expliclty depend on this storage implementation but only on the interface. And thus we have decoupled it.

## Marketplace

Since we buy crypto currency, we need to have a marketplace. This is also hidden behind the `Marketplace` interface which offers a few functions. It is not a complete wrapper of any particular marketplace, but just what we need in this project.

[![](graphs/marketplace.svg)](graphs/marketplace.svg)

There are two concrete implementations, namely for the Kraken and Bitstamp exchanges. These implementations depend on the external libraries. Again the remainder of the code only depends on the interface.

## Historical

In order to find drops, we need to know the prices in the past. These are provided by a historical source, which delivers price objects.

[![](graphs/historical.svg)](graphs/historical.svg)

There are many different implementations. One just asks the marketplace for the current price, that only works when the specified time is right now. For older times we can have a look into the database. But if there is no appropriate price available, it will ask on Crypto Compare. To the remainder of the program everything is hidden behind that interface.

## Triggers

The triggers get specified by the user. I have generalized the trigger concept such that it just handles regular actions. These also include database cleaning and sending a Telegram notification.

[![](graphs/triggers.svg)](graphs/triggers.svg)

The buy trigger uses two *delegates* as part of the *strategy pattern*. One is used to determine the amount of fiat money to spend, the other is whether the trigger should be considered active. This lets us mix and match these algorithms without having an exploding inheritance hierarchy.

Dependencies to other parts of the code are via the interfaces only, this way it is decoupled.

## Configuration

The configuration shall be independent of the file format used, it should provide some migrations and so on. All the parsing should be done there as well. At the moment I have a bunch of free functions, and they pass around lists and dicts.

[![](graphs/configuration.svg)](graphs/configuration.svg)

I am not that happy with that yet, I would like to have an interface there as well in order to mock that for tests.

## Telegram

The message sending to Telegram is implemented as a logger with the Python standard library `logging` facilities. I have a logger which extends the handler. In this way I depend on something external, but it is pluggable via the logging handler mechanism in the standard library.

[![](graphs/telegram.svg)](graphs/telegram.svg)

I use the *requests* library for the HTTP requests, which I did not hide behind an interface.

## Commands

The main commands then import a bunch of the concrete classes and instantiates that. This is okay, because that is on the outside ring of my architecture.

[![](graphs/commands.svg)](graphs/commands.svg)

## Everything

I also have a diagram where everything is put together. It is quite big, so click on it to view the full graphics.

[![](graphs/vigilant_crypto_snatch.svg)](graphs/vigilant_crypto_snatch.svg)

It is a bit harder to see, but the dependencies are acyclic. You can also see this from this page, where I was able to introduce the parts without having to forward declare something to be used later. Everything neatly built atop of existing things only.