import sys
from .generate_libro_config import launch_generate_libro_config
from .app import LibroApp

# 用于处理不同的子命令
def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "config":
            if len(sys.argv) > 2 and sys.argv[2] == "generate":
                launch_generate_libro_config()
            else:
                print("Unknown config command. Available: generate")
        else:
            print(f"Unknown command: {command}")
    else:
        LibroApp.launch_instance()
