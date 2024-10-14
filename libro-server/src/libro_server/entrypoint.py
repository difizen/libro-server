import sys
from .generate_libro_config import launch_generate_libro_config
from .app import LibroApp

import argparse
from ._version import __version__


def main():
    parser = argparse.ArgumentParser(description="libro cli")
    parser.add_argument('--version', action='store_true',
                        help='show the versions of core libro packages and exit')
    args = parser.parse_args()
    if args.version:
        for package in [
            "libro",
            "libro_server",
            "libro_ai",
            # "libro_sql",
            "libro_flow",
            "jupyter_server",
        ]:
            try:
                if package == "libro_server":  # We're already here
                    version = __version__
                else:
                    mod = __import__(package)
                    version = mod.__version__
            except ImportError:
                version = "not installed"
            print(f"{package:<17}:", version)
        return

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "config":
            if len(sys.argv) > 2 and sys.argv[2] == "generate":
                launch_generate_libro_config()
            else:
                print("Unknown config command. Available: generate")
        else:
            LibroApp.launch_instance()
    else:
        LibroApp.launch_instance()
