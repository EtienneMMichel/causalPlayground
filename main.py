import yaml
import sys
import json
import os

from src.discover import *

if __name__ == "__main__":
    config = yaml.safe_load(open(sys.argv[1], "r"))
    eval(f"{config['mode']}(config)")