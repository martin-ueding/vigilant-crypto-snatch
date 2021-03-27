import os

import jinja2
import markdown

from . import configuration

report_dir = os.path.join(configuration.dirs.user_data_dir, "report")


class Renderer(object):
    def __init__(self):
        loader = jinja2.PackageLoader("vigilant_crypto_snatch", "templates")
        self.env = jinja2.Environment(loader=loader)

    def render_md(self, filename, **kwargs):
        template = self.env.get_template(filename)
        inner_md = template.render(**kwargs)
        inner_html = markdown.markdown(inner_md)
        self.render_html(filename_to_html(filename), inner_html)

    def render_html(self, filename, body, **kwargs):
        template = self.env.get_template("site.html")
        outer_html = template.render(body=body, **kwargs)
        with open(os.path.join(report_dir, filename), "w") as f:
            f.write(outer_html)


def filename_to_html(filename: str) -> str:
    return os.path.splitext(filename)[0] + ".html"
