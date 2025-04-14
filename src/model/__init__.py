from .dummy import *


def build_model(config):
    return eval(f"{config['model']['name']}(config)")