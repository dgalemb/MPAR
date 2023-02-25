from __future__ import division  # Only for how I'm writing the transition matrix
import networkx as nx  # For the magic
import matplotlib.pyplot as plt  # For plotting

import numpy as np
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import matplotlib.pyplot as pl

def print_graph():
    # create state space and initial state probabilities
    states = [(0, 0),
          (1, 0),
          (2, 0),
          (3, 0),
          (4, 0),
          (0, 1),
          (1, 1),
          (2, 1),
          (3, 1),
          (4, 1),
          (0, 2),
          (1, 2),
          (2, 2),
          (3, 2),
          (4, 2),
          (0, 3),
          (1, 3),
          (2, 3),
          (3, 3),
          (0, 4),
          (1, 4),
          (2, 4)]
    Q = [[-5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1/2, -6, 5, 0, 0, 1/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1, -7, 5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, -7, 5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, -2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1/5, 0, 0, 0, 0, -26/5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1/5, 0, 0, 0, 1/2, -31/5, 5, 0, 0, 1/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1/5, 0, 0, 0, 1, -36/5, 5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1/5, 0, 0, 0, 1, -36/5, 5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1/5, 0, 0, 0, 1, -11/5, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 2/5, 0, 0, 0, 0, -27/5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1/2, -32/5, 5, 0, 0, 1/2, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1, -37/5, 5, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1, -37/5, 5, 0, 0, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1, -12/5, 0, 0, 0, 1, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 0, -27/5, 5, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1/2, -32/5, 5, 0, 1/2, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1/2, -32/5, 5, 0, 1/2, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, 1/2, -7/5, 0, 0, 1/2],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, -27/5, 5, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, -27/5, 5],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2/5, 0, 0, 0, -2/5]]

    G = nx.MultiDiGraph()
    labels={}
    edge_labels={}

    for i, origin_state in enumerate(states):
        for j, destination_state in enumerate(states):
            rate = Q[i][j]
            if rate > 0:
                G.add_edge(origin_state,
                           destination_state,
                           weight=rate,
                           label="{:.02f}".format(rate))
                edge_labels[(origin_state, destination_state)] = label="{:.02f}".format(rate)

    plt.figure(figsize=(14,7))
    node_size = 200
    pos = {state:list(state) for state in states}
    nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_weight=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    plt.axis('off')
    plt.show()

    write_dot(G, 'mc.dot')

def print_graph2():
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(1, 5)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)

    # explicitly set positions
    pos = {1: (0, 0), 2: (-1, 0.3), 3: (2, 0.17), 4: (4, 0.255), 5: (5, 0.03)}

    options = {
        "font_size": 36,
        "node_size": 3000,
        "node_color": "white",
        "edgecolors": "black",
        "linewidths": 5,
        "width": 5,
    }
    nx.draw_networkx(G, pos, **options)

    # Set margins for the axes so that nodes aren't clipped
    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.show()
