import numpy as np
import plotly.graph_objects as go
import pandas as pd
from copy import copy


def compare(graph, previous_graph):
    graph[graph == ''] = 0
    graph[graph == 'o-o'] = 1
    graph[graph == '-->'] = 2
    previous_graph[previous_graph == ''] = 0
    previous_graph[previous_graph == 'o-o'] = 1
    previous_graph[previous_graph == '-->'] = 2
    graph = graph.astype(int)
    previous_graph = previous_graph.astype(int)
    diff = graph - previous_graph
    diff = diff==previous_graph
    unique, counts = np.unique(diff, return_counts=True)
    occurences = dict(zip([str(u) for u in unique], [int(c) for c in counts]))
    return float(occurences['False']/(occurences['True'] + occurences['False']))

def graph_evolution(results):
    to_plot = []
    datetime = list(results.keys())
    nb_connections = []
    nb_directed_connections = []
    changes = []
    previous_graph = None
    for model_results in results.values():
        graph = model_results['graph']
        unique, counts = np.unique(graph, return_counts=True)
        occurences = dict(zip([str(u) for u in unique], [int(c) for c in counts]))
        nb_connection = float(1 - occurences.get('',0)/np.prod(list(graph.shape)))
        nb_directed_connection = float(occurences.get('-->',0)/np.prod(list(graph.shape)))
        nb_connections.append(nb_connection)
        nb_directed_connections.append(nb_directed_connection)
        if previous_graph is None:
            changes.append(0)
        else:
            changes.append(compare(graph, previous_graph))
        previous_graph = copy(graph)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=datetime, y=nb_connections,
                    mode='lines',
                    name='nb_connections'))
    fig.add_trace(go.Scatter(x=datetime, y=nb_directed_connections,
                    mode='lines',
                    name='nb_directed_connection'))
    fig.add_trace(go.Scatter(x=datetime, y=changes,
                    mode='lines',
                    name='changes'))
    fig.add_trace(go.Scatter(x=datetime, y=[c-n for c,n in zip(changes,nb_connections)],
                    mode='lines',
                    name='nb_connections'))
    fig.show()