from random_network_generator.network_generator import NetworkGenerator
from random_network_generator.model import NetworkSnapshot
from numpy.random import RandomState
import os
from random_network_generator.utils import (
    snapshot_closure,
    add_self_and_bidirectional_links,
)

def net_to_asp(
    _net: NetworkGenerator,
    _random_state: RandomState,
    _network_path: str
):
    directory = os.path.dirname(_network_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    net = _net.generate(_random_state)

    net_complete = snapshot_closure(net)

    net_final = add_self_and_bidirectional_links(net_complete)
    
    with open(_network_path, "w") as file:
        print("% Network topology:", file=file)
        for node in net_final.nodes:
            for atom in node.reify():
                print(str(atom) + ".", file=file)

        for link in net_final.links:
            for atom in link.reify():
                print(str(atom) + ".", file=file)

def app_to_asp(
    _application_graph: NetworkSnapshot,
    _service_path: str
):
    directory = os.path.dirname(_service_path)

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(_service_path, "w") as file:
        print("\n% Services to deploy:", file=file)
        for node in _application_graph.nodes:
            for atom in node.reify():
                print(str(atom) + ".", file=file)

        print("\n% Service-to-Service latency requirements:", file=file)
        for link in _application_graph.links:
            for atom in link.reify():
                print(str(atom) + ".", file=file)
