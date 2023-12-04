import os
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin
from libro_server.handler import ErrorHandler, TemplateHandler

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "template")

class LibroApp(ExtensionAppJinjaMixin, ExtensionApp):

    # -------------- Required traits --------------
    name = "libro"
    default_url = "/libro"
    load_other_extensions = True
    file_url_prefix = "/libro-render"

    # Local path to static files directory.
    static_paths = [DEFAULT_STATIC_FILES_PATH]

    # Local path to templates directory.
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    # ----------- add custom traits below ---------

    def initialize_settings(self):
        """Initialize settings."""
        # Update the self.settings trait to pass extra
        # settings to the underlying Tornado Web Application.
        self.log.info(f"Config {self.config}")

    def initialize_handlers(self):
        """Initialize handlers."""
        self.log.info(f"init handles")
        self.handlers.extend(
            [
                (rf"/{self.name}/?", TemplateHandler),
                (rf"/{self.name}/(.*)", ErrorHandler),
            ]
        )

# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = LibroApp.launch_instance

if __name__ == "__main__":
    main()
