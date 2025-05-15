from .dummy import *
from .pcmci import *
from .multi_graph import *


def build_model(config):
    return eval(f"{config['model']['name']}(config)")