# Developing

This project is written in Python. It uses [Poetry](https://python-poetry.org/) to manage the project and its dependencies.

Once you have obtained the source code via `git clone`, you can install the project into a virtual environment using `poetry install`. This will install all the dependencies and the package.

You can of course use any Python development environment that you want. Martin can recommend [PyCharm Community Edition](https://www.jetbrains.com/pycharm/). Make sure to install the “Poetry” plugin to easily set up the virtual environment.

In order to run in development mode, use Poetry:

```bash
poetry run vigilant-crypto-snatch [more command line arguments]
```

## Updating the documentation

The documentation is created with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Just edit the Markdown files in `docs`.

To locally view the documentation, use this:

```bash
poetry run mkdocs serve
```

To publish a new version to GitHub Pages, use this:

```bash
poetry run mkdocs gh-publish
```

## Code style

We try to develop this in a *Clean Code* way, with the least amount of coupling. We also follow the [Hypermodern Python](https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769) series for project layout and choice of tooling.

Code formatting is done with [Black](https://github.com/psf/black):

```bash
poetry run black src/**.py test/**.py
```