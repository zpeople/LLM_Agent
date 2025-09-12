
import os
import sys
try:
    get_ipython
    current_dir = os.getcwd()
except NameError:
    current_dir = os.path.dirname(os.path.abspath(__file__))

# Set path，temporary path expansion
project_dir = os.path.abspath(os.path.join(current_dir, ''))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from pathlib import Path
import yaml

def get_yaml_config(agents_config_file):
    agents_config_path= os.path.join(project_dir,agents_config_file)
    def load_yaml(config_path: Path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"File not found: {config_path}")
            raise
    try:
        agents_config = load_yaml(agents_config_path)
    except FileNotFoundError:
        print(
            f"Agent config file not found at {agents_config_path}. "
            "Proceeding with empty agent configurations."
        )
        agents_config = {}
    return agents_config