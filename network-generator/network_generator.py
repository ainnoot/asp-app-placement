import sys
from numpy.random import RandomState
from random_network_generator.network_generator import *
from random_network_generator.nx_wrappers import (
    BarabasiAlbert,
    ErdosRenyi,
    TruncatedBarabasiAlbert,
    RandomInternet,
    WattsStrogatz,
    CompleteGraph,
)
from random_network_generator.attribute import (
    MultiModal,
    UniformDiscrete,
    UniqueStringIdentifier,
)
import networkx as nx
from random_network_generator.model import Node
from random_network_generator.asp_generator import net_to_asp
from argparse import ArgumentParser
import uuid

def parse_args():
    p = ArgumentParser()
    p.add_argument("--seed", "-s", type=int, default=42, help="Seed to generate the network.")
    p.add_argument('--nodes-config', type=str, help="Path to the nodes configuration file (.yaml)")
    p.add_argument('--nodes-number', "-n", required=True, type=int, help="Number of nodes in the network")
    p.add_argument("--network-dir", default=None, type=str, help="Network facts output path.")
    p.add_argument("--latency-min", "-l", type=int, default=30, help="Minimun latency value for link generation")
    p.add_argument("--latency-max", "-L", type=int, default=500, help="Maximum latency value for link generation")

    return p.parse_args()

def generate_network(seed: int, nodes_config: str, nodes_number: int, network_dir: str, min_latency: int, max_latency: int):

    if nodes_config is not None:
        NodesConfigurations.set_nodes_config(nodes_config)

    r = RandomState(seed)

    if network_dir != None:
        base_out_path = network_dir
    else:
        base_out_path = (Path(__file__).parent).as_posix()
    
    network = NetworkGenerator(
        False,  ## Set to True if you want a complete Graph
        BarabasiAlbert(n=nodes_number, m=1),
        # ErdosRenyi(n=153, p=0.05),
        # BarabasiAlbert(n=153, m=3),
        # RandomInternet(n=153),
        # WattsStrogatz(n=153, k=4, p=0.1),
        NodeGenerator(
            node_type=UniformDiscrete('router','server','pc','iot')
        ),
        LinkGenerator(
            latency=UniformDiscrete(25, 50, 100, 250),
            bandwidth=UniformDiscrete(*list(range(1000, 2000))),
        ),
    )

    base_out_path += f"/generated_network/{nodes_number}/n-{nodes_number}-{str(uuid.uuid4())[:8]}.lp"

    net_to_asp(network, r, base_out_path)


if __name__ == "__main__":
    args = parse_args()

    generate_network(seed=args.seed, 
                     nodes_config=args.nodes_config, 
                     nodes_number=args.nodes_number,
                     network_dir=args.network_dir, 
                     min_latency=args.latency_min,
                     max_latency=args.latency_max)
    



    

    
