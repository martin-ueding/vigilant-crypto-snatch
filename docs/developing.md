# Developing

If you want to contribute, that's awesome! It is best if you get in touch first, then we can discuss the best way to add your idea.

We try to develop this in a *Clean Code* way, with the least amount of coupling. We also follow the [Hypermodern Python](https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769) series for project layout and choice of tooling.

## Development setup

This project is written in Python. It uses [Poetry](https://python-poetry.org/) to manage the project and its dependencies.

Once you have obtained the source code via `git clone`, you can install the project into a virtual environment using `poetry install`. This will install all the dependencies and the package.

You can of course use any Python development environment that you want. Martin can recommend [PyCharm Community Edition](https://www.jetbrains.com/pycharm/). Make sure to install the “Poetry” plugin to easily set up the virtual environment.

In order to run in development mode, use Poetry:

```bash
poetry run vigilant-crypto-snatch [more command line arguments]
```

You can run the tests with `pytest`:

```bash
poetry run pytest
```

In order to determine test coverage, use this:

```bash
poetry run coverage run --source=src -m pytest
poetry run coverage html
```

We use the [pre-commit tool](https://pre-commit.com/). So also run `pre-commit install` to set it up. This will take care of code formatting with [Black](https://github.com/psf/black), static type checking, unit test and test coverage on every commit.

## Updating the documentation

The documentation is created with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Just edit the Markdown files in `docs`.

To locally view the documentation, use this:

```bash
poetry run mkdocs serve
```

## New release

In order to create a new release, we use the `make-release` script. It requires the access credentials to GitHub and PyPI and Codecov, so only Martin can do that at this point.