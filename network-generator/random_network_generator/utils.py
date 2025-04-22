"""
A Network object models a (simplified) network topology, ...
"""

import time

import networkx as nx
from numpy.random import RandomState
import itertools
from random_network_generator.model import *
from random_network_generator.clingo_utils import as_clingo_term
# from loguru import logger


def prune_network(
    network: NetworkSnapshot, shut_down_probability: float, random_state: RandomState
) -> NetworkSnapshot:
    """
    Kills some nodes within the network and corresponding links.
    """

    alive_nodes = [
        node for node in network.nodes if random_state.random() > shut_down_probability
    ]
    alive_node_ids = set(x.id for x in alive_nodes)
    alive_links = [
        link
        for link in network.links
        if link.source in alive_node_ids and link.target in alive_node_ids
    ]
    return NetworkSnapshot(alive_nodes, alive_links)


def as_nx_graph(network: NetworkSnapshot) -> nx.Graph:
    """
    Maps a NetworkSnapshot into a nx.Graph, preserving atttributes on links and nodes.
    """

    graph = nx.Graph()
    for node in network.nodes:
        graph.add_node(node.id, storage=node.storage_gb, cost=node.cost)

    for link in network.links:
        graph.add_edge(
            link.source, link.target, latency=link.latency, bandwidth=link.bandwidth
        )

    return graph


def snapshot_closure(network: NetworkSnapshot) -> NetworkSnapshot:
    closure_computation_start = time.time()
    """
    Computes transitive closure of the network, introducing virtual edges and assigning them the worst-possible latency and bandwidth.
    """

    def virtual_link(i, j):
        # Sum of latencies
        latency = paths[i][0][j]

        # Bandwidths along the shortest path i--j
        path = paths[i][1][j]

        # The virtual link has the sum of latencies & minimum bandwidth
        link = Link(
            i,
            j,
            latency,
            min(
                graph.edges[path[x], path[x + 1]]["bandwidth"]
                for x in range(len(path) - 1)
            ),
        )

        return link

    graph = as_nx_graph(network)
    node_ids = [int(x) for x in graph.nodes]

    paths = dict(nx.all_pairs_dijkstra(graph, weight="latency"))

    links = []
    for i, j in itertools.combinations(node_ids, 2):
        if not (i, j) in graph.edges:
            try:
                links.append(virtual_link(i, j))
            except:
                pass

    closure_computation_end = time.time()

    # logger.debug(
    #     "Closure computation: {:.3f}s".format(
    #         closure_computation_end - closure_computation_start
    #     )
    # )

    links.extend(network.links)
    return NetworkSnapshot(network.nodes, links)


def add_self_and_bidirectional_links(network: NetworkSnapshot) -> NetworkSnapshot:
    """
    Adds self-links with latency 0 and ensures bidirectional links with the same latency.
    """
    graph = as_nx_graph(network)

    links = []

    # Add self-links with latency 0
    for node in network.nodes:
        if not (node.id, node.id) in graph.edges:
            try:
                links.append(Link(node.id, node.id, 0, node.bandwidth_mbps))
            except:
                pass
    # Ensure bidirectional links with the same latency
    for link in network.links:
        if (link.target, link.source) in graph.edges:
            try:
                links.append(
                    Link(link.target, link.source, link.latency, link.bandwidth)
                )
            except:
                pass

    links.extend(network.links)
    return NetworkSnapshot(network.nodes, links)
