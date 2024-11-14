import networkx as nx
from collections import OrderedDict
import numpy as np


def analyze(G):
    # UG = G.to_undirected()
    #
    # sub_graphs = nx.connected_component_subgraphs(UG)
    #
    # for i, sg in enumerate(sub_graphs):
    #     print("subgraph {} has {} nodes".format(i, sg.number_of_nodes()))
    #     print("\tNodes:", sg.nodes(data=True))
    #     print("\tEdges:", sg.edges())
    #
    dict = get_connectedness(G)
    n = 10
    keys = list(dict.keys())[-n:]
    values = list(dict.values())[-n:]
    sorted_value_index = np.argsort(values)
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}

    print(sorted_dict[-n:])
    # xl.sort
    # y = get_betweenness(g)
    # print(y)


def get_connectedness(G):
    # Computing centrality
    degCent = nx.degree_centrality(G)

    # Descending order sorting centrality
    degCent_sorted = dict(sorted(degCent.items(), key=lambda item: item[1], reverse=True))
    return degCent_sorted


def get_betweenness(G):
    # Computing betweeness
    betCent = nx.betweenness_centrality(G, normalized=True, endpoints=True)

    # Descending order sorting betweeness
    betCent_sorted = dict(sorted(betCent.items(), key=lambda item: item[1], reverse=True))
    return betCent_sorted
