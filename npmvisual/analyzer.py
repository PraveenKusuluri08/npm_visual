import networkx as nx
from colorama import Fore, Style, init
from collections import OrderedDict
import numpy as np


def analyze(graph):
    # Existing analysis...
    print("\n--- Graph Analysis ---")

    # 1. Basic Graph Information
    print("\nGraph Information:")
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")
    print(f"Is directed? {graph.is_directed()}")

    # 2. Degree Centrality (already existing)
    analyze_degree_centrality(graph)

    # 3. Closeness Centrality (already existing)
    analyze_closeness_centrality(graph)

    # 4. Betweenness Centrality (already existing)
    analyze_betweenness_centrality(graph)

    # 5. Shortest Path (already existing)
    analyze_shortest_paths(graph)

    # 6. Strongly Connected Components (already existing)
    analyze_strongly_connected_components(graph)

    # 7. Community Detection (already existing)
    analyze_community_detection(graph)

    # 8. Clique Detection (already existing)
    # analyze_cliques(graph)

    # 9. Graph Density (already existing)
    analyze_graph_density(graph)

    # New Analysis Functions
    analyze_pagerank(graph)
    analyze_hits(graph)
    analyze_weakly_connected_components(graph)
    analyze_diameter_and_radius(graph)
    analyze_degree_distribution(graph)
    analyze_transitivity(graph)
    # analyze_rich_club(graph)
    analyze_edge_betweenness(graph)
    analyze_k_core(graph)

    print("\n--- Analysis Complete ---")


def analyze_degree_centrality(graph):
    print("\nDegree Centrality (Top 5 nodes):")
    degree_centrality = nx.degree_centrality(graph)
    sorted_degree = sorted(
        degree_centrality.items(), key=lambda item: item[1], reverse=True
    )
    for node, centrality in sorted_degree[:5]:
        print(f"{node:<20}: {centrality:.4f}")


def analyze_closeness_centrality(graph):
    print("\nCloseness Centrality (Top 5 nodes):")
    closeness_centrality = nx.closeness_centrality(graph)
    sorted_closeness = sorted(
        closeness_centrality.items(), key=lambda item: item[1], reverse=True
    )
    for node, centrality in sorted_closeness[:5]:
        print(f"{node:<20}: {centrality:.4f}")


def analyze_betweenness_centrality(graph):
    print("\nBetweenness Centrality (Top 5 nodes):")
    betweenness_centrality = nx.betweenness_centrality(graph)
    sorted_betweenness = sorted(
        betweenness_centrality.items(), key=lambda item: item[1], reverse=True
    )
    for node, centrality in sorted_betweenness[:5]:
        print(f"{node:<20}: {centrality:.4f}")


def analyze_shortest_paths(graph):
    print("\nShortest Paths (from 'react'):")
    if "react" in graph:
        shortest_paths = nx.single_source_shortest_path_length(graph, "react")
        for target, length in sorted(shortest_paths.items(), key=lambda item: item[1]):
            print(f"react -> {target}: {length}")
    else:
        print("Node 'react' not found in the graph")


def analyze_strongly_connected_components(graph):
    print("\nStrongly Connected Components (SCC):")
    scc = list(nx.strongly_connected_components(graph))
    for i, component in enumerate(scc[:5]):
        print(f"Component {i+1}: {sorted(component)}")


def analyze_community_detection(graph):
    try:
        from community import community_louvain

        print("\nCommunity Detection (Top 5 communities):")
        partition = community_louvain.best_partition(graph)
        communities = {}
        for node, community_id in partition.items():
            if community_id not in communities:
                communities[community_id] = []
            communities[community_id].append(node)
        for i, community_nodes in enumerate(list(communities.values())[:5]):
            print(f"Community {i+1}: {sorted(community_nodes)}")
    except ImportError:
        print(
            "\nCommunity Detection (Louvain) requires 'python-louvain' package. Skipping."
        )


def analyze_cliques(graph):
    print("\nCliques in the graph:")
    cliques = list(nx.find_cliques(graph))
    for i, clique in enumerate(cliques[:5]):
        print(f"Clique {i + 1}: {sorted(clique)}")


def analyze_graph_density(graph):
    print(f"\nGraph Density: {nx.density(graph):.4f}")


def analyze_pagerank(graph):
    print("\nPageRank (Top 5 nodes):")
    pagerank = nx.pagerank(graph)
    sorted_pagerank = sorted(pagerank.items(), key=lambda item: item[1], reverse=True)
    for node, rank in sorted_pagerank[:5]:
        print(f"{node:<20}: {rank:.4f}")


def analyze_hits(graph):
    print("\nHITS Algorithm (Top 5 Hubs and Authorities):")
    hubs, authorities = nx.hits(graph)
    sorted_hubs = sorted(hubs.items(), key=lambda item: item[1], reverse=True)
    sorted_authorities = sorted(
        authorities.items(), key=lambda item: item[1], reverse=True
    )

    print("\nTop Hubs:")
    for node, hub_score in sorted_hubs[:5]:
        print(f"{node:<20}: {hub_score:.4f}")

    print("\nTop Authorities:")
    for node, authority_score in sorted_authorities[:5]:
        print(f"{node:<20}: {authority_score:.4f}")


def analyze_weakly_connected_components(graph):
    print("\nWeakly Connected Components (Top 5):")
    weakly_connected_components = list(nx.weakly_connected_components(graph))
    for i, component in enumerate(weakly_connected_components[:5]):
        print(f"Component {i+1}: {sorted(component)}")


def analyze_diameter_and_radius(graph):
    print("\nGraph Diameter and Radius:")
    if nx.is_strongly_connected(graph):
        eccentricities = nx.eccentricity(graph)
        diameter = max(eccentricities.values())
        radius = min(eccentricities.values())
        print(f"Graph Diameter: {diameter}")
        print(f"Graph Radius: {radius}")
    else:
        print("Graph is not strongly connected. Skipping diameter and radius.")


def analyze_strongly_connected_components(graph):
    print("\nStrongly Connected Components (SCC):")
    scc = list(nx.strongly_connected_components(graph))
    for i, component in enumerate(scc[:5]):
        print(f"Component {i+1}: {sorted(component)}")


def analyze_degree_distribution(graph):
    print("\nIn-Degree and Out-Degree Distribution:")
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    sorted_in_degrees = sorted(
        in_degrees.items(), key=lambda item: item[1], reverse=True
    )
    sorted_out_degrees = sorted(
        out_degrees.items(), key=lambda item: item[1], reverse=True
    )

    print("\nTop 5 Nodes by In-Degree:")
    for node, degree in sorted_in_degrees[:5]:
        print(f"{node:<20}: {degree}")

    print("\nTop 5 Nodes by Out-Degree:")
    for node, degree in sorted_out_degrees[:5]:
        print(f"{node:<20}: {degree}")


def analyze_transitivity(graph):
    print("\nGraph Transitivity:")
    transitivity = nx.transitivity(graph)
    print(f"Transitivity: {transitivity:.4f}")


def analyze_rich_club(graph):
    print("\nRich-Club Coefficient:")
    rich_club = nx.rich_club_coefficient(graph)
    for degree, coefficient in rich_club.items():
        print(f"Degree {degree}: Rich-club coefficient: {coefficient:.4f}")


def analyze_edge_betweenness(graph):
    print("\nEdge Betweenness Centrality (Top 5 edges):")
    edge_betweenness = nx.edge_betweenness_centrality(graph)
    sorted_edge_betweenness = sorted(
        edge_betweenness.items(), key=lambda item: item[1], reverse=True
    )
    for edge, centrality in sorted_edge_betweenness[:5]:
        print(f"Edge {edge}: {centrality:.4f}")


def analyze_k_core(graph, k=3):
    print(f"\nK-Core Decomposition (k={k}):")
    k_core = nx.k_core(graph, k=k)
    print(f"K-Core (k={k}) nodes: {sorted(k_core.nodes())}")
