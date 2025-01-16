from typing import Any
import yaml


def load_config(file_path: str) -> Any:
    with open(file=file_path, mode="r") as conf_file:
        return yaml.safe_load(conf_file)
    
