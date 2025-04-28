from . import utils
from .model import build_model
from tqdm import tqdm

def discover_from_prices(config):
    symbols = config['data']['symbols']
    data = utils.preprocess(config)
    prices = data[[f"{s}-close_price" for s in symbols]]
    data = prices.to_numpy()
    
    model = build_model(config)
    model(data)