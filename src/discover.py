from . import utils
from .model import build_model
from tqdm import tqdm
import numpy as np
from . import visualize

def discover_from_prices(config):
    symbols = config['data']['symbols']
    data = utils.preprocess(config)
    prices = data[[f"{s}-close_price" for s in symbols]]
    data = prices.to_numpy()
    data = np.log(data[1:]) - np.log(data[:-1])
    data = np.nan_to_num(data)
    
    model = build_model(config)
    model(data)


def discover_from_prices_and_volume(config):
    window = config["data"]["window"]
    model = build_model(config)
    symbols = config['data']['symbols']
    data = utils.preprocess(config)
    datetime = data.index.tolist()
    prices = data[[f"{s}-close_price" for s in symbols]].to_numpy()
    volumes = data[[f"{s}-volume" for s in symbols]].to_numpy()
    prices = prices.reshape(tuple(list(prices.shape) + [1]))
    prices = np.log(prices[1:]) - np.log(prices[:-1])
    volumes = volumes.reshape(tuple(list(volumes.shape) + [1]))
    volumes = volumes[1:]
    datetime = datetime[1:]
    union_data = {
        "prices":prices,
        "volumes":volumes,
    }
    data = np.concat(list(union_data.values()), axis=-1)
    data = np.nan_to_num(data)
    model.set_data_index({name:i for i, name in enumerate(list(union_data.keys()))})
    results = {}
    additionnal_data = []
    for i in tqdm(range(int(data.shape[0]/window))):
        window_data = data[i*window:(i+1)*window]
        window_datetime = datetime[(i+1)*window - 1]
        results[window_datetime] = model(window_data)
        additionnal_data.append({
            "datetime": window_datetime,
            "window_data": window_data
        })
    
    visualize.graph_evolution(results, additionnal_data)

    
    

