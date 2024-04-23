import json
from jupyter_server.base.handlers import JupyterHandler, APIHandler
from jupyter_server.extension.handler import (
    ExtensionHandlerMixin,
    ExtensionHandlerJinjaMixin,
)
from jupyterlab_server import LabHandler
from tornado import template, web


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):  # type: ignore
    """The base template handler."""

    pass


class TemplateHandler(BaseTemplateHandler):
    """A template handler."""

    def get(self):
        """Optionally, you can print(self.get_template('simple1.html'))"""
        self.write(self.render_template("libro.html"))


class ErrorHandler(BaseTemplateHandler):
    """An error handler."""

    def get(self, path):
        """Write_error renders template from error.html file."""
        self.write_error(400)


class LibroLabHandler(LabHandler):
    """Render the JupyterLab View."""

    @web.authenticated
    @web.removeslash
    def get(self, mode=None, workspace=None, tree=None) -> None:
        """Get the JupyterLab html page."""
        workspace = (
            "default" if workspace is None else workspace.replace("/workspaces/", "")
        )
        tree_path = "" if tree is None else tree.replace("/tree/", "")

        page_config = self.get_page_config()

        # Add parameters parsed from the URL
        if mode == "doc":
            page_config["mode"] = "single-document"
        else:
            page_config["mode"] = "multiple-document"

        page_config["workspace"] = workspace
        page_config["treePath"] = tree_path

        # Write the template with the config.
        tpl = self.render_template(
            "libro.html", page_config=page_config
        )  # type:ignore[no-untyped-call]
        self.write(tpl)
