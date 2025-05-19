import numpy as np
import plotly.graph_objects as go
import pandas as pd
from copy import copy
import os
import datetime as dt
from plotly.subplots import make_subplots
from sklearn.metrics import precision_recall_fscore_support
import pytz

def compare(graph, previous_graph):
    graph[graph == ''] = 0
    graph[graph == 'o-o'] = 1
    graph[graph == '-->'] = 1
    previous_graph[previous_graph == ''] = 0
    previous_graph[previous_graph == 'o-o'] = 1
    previous_graph[previous_graph == '-->'] = 1
    graph = graph.astype(int)
    previous_graph = previous_graph.astype(int)
    results = []
    for g, p_g in zip(graph, previous_graph):
        results.append(list(precision_recall_fscore_support(p_g, g, average='micro'))[:-1])
    results = np.mean(results, axis=0)
    return {
        "precision": float(results[0]),
        "recall": float(results[1]),
        "fbeta_score": float(results[2]),
    }
    unique, counts = np.unique(diff, return_counts=True)
    occurences = dict(zip([str(u) for u in unique], [int(c) for c in counts]))
    return float(occurences['False']/(occurences['True'] + occurences['False']))

def load_data(year, start_date=None, end_date=None):
    df = None
    for filename in os.listdir(f"DATA/financial_market_data/{year}"):
        filename_ = filename[:-4]
        _, month, day = filename_.split(" ")
        if not start_date is None and dt.datetime(year=year, month=int(month), day=int(day)) < start_date:
            continue
        if not end_date is None and dt.datetime(year=year, month=int(month), day=int(day)) > end_date:
            continue
        df_ = pd.read_csv(f"DATA/financial_market_data/{year}/{filename}",delimiter=",")
        df_["datetime"] = pd.to_datetime(df_["TimeStamp"], format='ISO8601')
        df_ = df_[["datetime", "/ES","/NQ","/RTY","SPY","QQQ","IWM","AAPL","MSFT","NVDA"]]
        df = pd.concat([df, df_], axis=0) if not df is None else df_
    return df


def load_financial_tradi_data(datetime):
    start_date = datetime[0]
    end_date = datetime[-1]
    df = None
    if start_date.year == end_date.year:
        # load only one year folder
        df = load_data(year=int(start_date.year), start_date=start_date,end_date=end_date)
    else:
        for i in range(int(end_date.year) - int(start_date.year) + 1):
            if i == 0:
                df_ = load_data(year=int(start_date.year) + i, start_date=start_date)
            elif i == int(end_date.year) - int(start_date.year):
                df_ = load_data(year=int(start_date.year) + i, end_date=end_date)
            else:
                df_ = load_data(year=int(start_date.year) + i)
            if not df_ is None:
                df = pd.concat([df, df_], axis=0) if not df is None else df_
    df.reset_index(drop=True, inplace=True)
    # pas = int(df.shape[0]/len(datetime))
    # if pas > 1:
    #     df = df.iloc[[i*pas for i in range(len(datetime))]]
    return df
    
def decay_to_new_york_timezone(datetime):
    timestamp = [d.timestamp() for d in datetime]
    utc_0_timezone = pytz.timezone("Etc/UTC")
    new_york_timezone = pytz.timezone("America/New_York")
    utc_timestamp = [utc_0_timezone.normalize(utc_0_timezone.localize(t)) for t in datetime]
    localized_timestamp = [t.astimezone(new_york_timezone) for t in utc_timestamp]
    return localized_timestamp

def graph_evolution(results, additionnal_data):
    datetime = list(results.keys())
    financial_tradi_data = load_financial_tradi_data(datetime)
    datetime = decay_to_new_york_timezone(datetime)
    nb_connections = []
    nb_directed_connections = []
    compares = []
    previous_graph = None
    for model_results in results.values():
        graph = model_results['graph']
        unique, counts = np.unique(graph, return_counts=True)
        occurences = dict(zip([str(u) for u in unique], [int(c) for c in counts]))
        nb_connection = float(1 - occurences.get('',0)/np.prod(list(graph.shape)))
        nb_directed_connection = float(occurences.get('-->',0)/np.prod(list(graph.shape)))
        nb_connections.append(nb_connection)
        nb_directed_connections.append(nb_directed_connection)
        if not previous_graph is None:
            compares.append(compare(graph, previous_graph))
        previous_graph = copy(graph)

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1,
                    specs=[[{"secondary_y": True}], [{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=datetime[1:], y=[c["precision"] for c in compares],
                    mode='lines',
                    name='precision'), secondary_y=False, row=1, col=1)
    fig.add_trace(go.Scatter(x=datetime[1:], y=[1 - c["recall"] for c in compares],
                    mode='lines',
                    name='false positive rate'), secondary_y=False, row=1, col=1)
    fig.add_trace(go.Scatter(x=financial_tradi_data["datetime"], y=financial_tradi_data["SPY"],
                    mode='lines',
                    name='SPY'), secondary_y=True, row=1, col=1)
    fig.show()