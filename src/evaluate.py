from . import utils
from .model import build_model
from tqdm import tqdm

def evaluate(config):
    window = config["model"]["window"]
    horizon = config["model"]["horizon"]
    visualize = config.get("visualize", False)
    print("LOAD DATA...")
    data = utils.preprocess(config)
    assert data.shape[0] >= window + horizon
    print("DONE")

    print("BUILD MODEL...")
    model = build_model(config)
    print("DONE")

    print("LAUNCH...")
    metrics = []
    for i in tqdm(range(window, data.shape[0] - horizon)):
        window_data = data.iloc[i-window:i,:]
        horizon_data = data.iloc[i:i + horizon,:]
        preds = model(window_data)
        metric = utils.metrics.evaluate_predictions(preds, horizon_data)
        metrics.append(metric)
    
    print("DONE")

    if visualize:
        print("VISUALIZE")
        pass
    

