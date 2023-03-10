import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import to_agraph
import numpy as np
import imageio
import string


def list_to_dict(nom_etats, liste):
    dictionary = dict()
    for nom_i in range(len(nom_etats)):
        dictionary[nom_etats[nom_i]] = liste[nom_i]
    return dictionary


def size_edges(states):
    n_states = len(states)
    if n_states == 2:
        return 4
    elif 3 <= n_states <= 4:
        return 5
    else:
        return 4


def create_image_by_id(id_, g_print, id_image):
    for i, n in enumerate(g_print.edges(data=True)):
        if n[-1]['id'] == id_:
            n[-1]['color'] = 'green'
        else:
            n[-1]['color'] = 'black'

    save_image(g_print, id_image)
    letters = list(string.ascii_uppercase)
    if len(id_) > 3 or id_[-1].isnumeric():
        id_tmp = id_[-3:]
        for l in letters:
            if l in id_tmp:
                id_ = id_tmp[id_tmp.index(l):]
                for i, n in enumerate(g_print.nodes(data=True)):
                    if n[-1]['id'] == id_:
                        n[-1]['fillcolor'] = 'green'
                    else:
                        n[-1]['fillcolor'] = 'white'
    else:
        id_ = id_[-1]
        for i, n in enumerate(g_print.nodes(data=True)):
            if n[-1]['id'] == id_:
                n[-1]['fillcolor'] = 'green'
            else:
                n[-1]['fillcolor'] = 'white'


    save_image(g_print, id_image + 1)


def save_image(g_print, id_):
    A = to_agraph(g_print)
    A.layout()
    name_image = f"image_{id_}.png"
    A.draw('tmp/' + name_image)


def print_graph(etats):
    # Define the states
    states = list(etats.keys())
    # print(f"S0: {etats['S0'].have_decision},  {etats['S0'].transitions}")
    # print(f"S1: {etats['S1'].have_decision},  {etats['S1'].transitions}")
    # print(f"S2: {etats['S2'].have_decision},  {etats['S2'].transitions}")

    # Define the actions
    color_actions = ['blue', 'magenta', 'cyan', 'red', 'yellow']
    actions = dict()

    actual_state_color = '#606060'

    # Define the transition probabilities
    P = dict()
    for etat in states:
        if etats[etat].have_decision:
            P[etat] = dict()
            for action, probs in etats[etat].transitions.items():
                P[etat][action] = list_to_dict(states, probs)
        else:
            P[etat] = list_to_dict(states, etats[etat].transitions['MC'])

    # Create the graph
    G = nx.MultiDiGraph()

    # Add the states as nodes
    # G.add_nodes_from(states, size=5)
    [G.add_node(s, id=s, style='filled', fillcolor='white', shape='circle', fixedsize='true', width=1) for s in states]

    s_edges = size_edges(states)

    # Add the actions as edges
    for state in states:
        if list(P[state].keys())[0] not in states:  # if there are actions
            for action in P[state].keys():
                if action not in list(actions.keys()):
                    actions[action] = color_actions.pop(0)  # to choose one color for the action
                for next_state in P[state][action]:
                    prob = P[state][action][next_state]
                    if prob > 0:
                        G.add_edge(state, next_state, id=f"{state}{action}{next_state}", label=f"{action} ({prob:.2f})", len=s_edges, color=actions[action], font_size=5)
        else:
            for next_state in P[state]:
                prob = P[state][next_state]
                if prob > 0:
                    G.add_edge(state, next_state, id=f"{state}{next_state}", label=f"({prob:.2f})", len=s_edges, color='black')

    save_image(G, 'init')
    return G


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


# Gif :
# # Markov chain parameters
# states = [(0, 0),
#           (1, 0),
#           (2, 0), ]
#
# Q = [[0.2, 0.3, 0.5],
#      [0.1, 0.2, 0.7],
#      [0.3, 0.7, 0]
#      ]
#
# # Sampling the markov chain over 100 steps
# N_steps = 100
# node_ind = 0
# node_sel = [node_ind]
# for i in range(N_steps):
#     temp_ni = np.random.choice(3, p=Q[node_ind])
#     node_sel.append(temp_ni)
#     node_ind = temp_ni
#
# # Setting up network
# G = nx.MultiDiGraph()
# [G.add_node(s, style='filled', fillcolor='white', shape='circle', fixedsize='true', width=0.5) for s in states]
#
# labels = {}
# edge_labels = {}
#
# for i, origin_state in enumerate(states):
#     for j, destination_state in enumerate(states):
#         rate = Q[i][j]
#         if rate > 0:
#             G.add_edge(origin_state, destination_state, weight=rate, label="{:.02f}".format(rate), len=2)
#
# A = to_agraph(G)
# A.layout()
# A.draw('test.png')

# # Setting up node color for each iteration
# for k in range(N_steps):
#     for i, n in enumerate(G.nodes(data=True)):
#         if i == node_sel[k]:
#             n[1]['fillcolor'] = 'blue'
#         else:
#             n[1]['fillcolor'] = 'white'
#
#     A = to_agraph(G)
#     A.layout()
#     A.draw('net_' + str(k) + '.png')
#
# # Create gif with imageio
# images = []
# filenames = ['net_' + str(k) + '.png' for k in range(N_steps)]
# for filename in filenames:
#     images.append(imageio.v2.imread(filename))
# imageio.mimsave('markov_chain.gif', images, fps=3)





# Draw the graph
# pos = nx.spring_layout(G)
# nx.draw_networkx(G, pos, with_labels=True)
# edge_labels = nx.get_edge_attributes(G, "label")
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
# plt.show()
