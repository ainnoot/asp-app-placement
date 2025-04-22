from numpy.random import RandomState
from random_network_generator.model import Link, Node, Service, NetworkSnapshot, ServiceLink
from random_network_generator.attribute import AttributeGenerator
from random_network_generator.nx_wrappers import GraphGenerator
from dataclasses import dataclass
import yaml
import os
from pathlib import Path


"""
A Network object models a network of devices. In our model, Nodes are characterized by storage costs and available storage. 
Links are characterized by latencies and bandwidths.
"""


class NodesConfigurations:
	services_config=(Path(__file__).parent / 'services_config.yaml').as_posix()
	nodes_config=(Path(__file__).parent / 'nodes_config.yaml').as_posix()

	@staticmethod
	def set_services_config(filename):
		NodesConfigurations.services_config=Path(filename).as_posix()

	@staticmethod
	def set_nodes_config(filename):
		NodesConfigurations.nodes_config=Path(filename).as_posix()

@dataclass(frozen=True)
class NodeGenerator:
    node_type: AttributeGenerator

    '''
    id: int
    storage_gb: int
    ram_gb: int
    availability: int
    cpu: int
    bandwidth_mbps: int
    access_control: bool
    anti_tampering: bool
    encryption: bool
    gpu: bool
    carbon_intensity: int
    pue: int
    cost: int
    '''

    def load_configurations(self):
        try:
            with open(NodesConfigurations.nodes_config, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {NodesConfigurations.nodes_config}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")


    def get_matching_configs(self, _node_type):
        configs = self.load_configurations()['nodes']
        type_groups = {
            'router': ['enterprise_router', 'home_router'],
            'server': ['application_server', 'database_server'],
            'pc': ['workstation_pc', 'office_pc'],
            'iot': ['smart_thermostat', 'security_camera']
        }
        
        if _node_type.lower() in list(type_groups.keys()):
            matching_nodes = type_groups[_node_type.lower()]
            return {name: configs[_node_type.lower()][name] for name in matching_nodes}
        else:
            return {}

    def generate(self, i, random_state: RandomState) -> Node:

        _node_type =  self.node_type.generate(random_state=random_state)

        matching_configs = self.get_matching_configs(_node_type)
        
        if not matching_configs:
            raise ValueError(f"No configurations found for node type: {_node_type}")
        
        template_name = random_state.choice(list(matching_configs.keys()))
        template = matching_configs[template_name]
        
        return Node(
            i,
            storage_gb=int(template['storage_gb']),
            ram_gb=int(template['ram_gb']),
            availability=float(template['availability']),
            cpu=int(template['cpu']),
            gpu=bool(template.get('gpu', False)),
            bandwidth_in=int(template['bandwidth_in']),
            bandwidth_out=int(template['bandwidth_out']),
            access_control=bool(template.get('access_control', False)),
            anti_tampering=bool(template.get('anti_tampering', False)),
            encryption=bool(template.get('encryption', False)),
            carbon_intensity=int(template['carbon_intensity']*1000),
            pue=int(template['pue']*10),
            cost=int(template['cost'])
        )


@dataclass(frozen=True)
class LinkGenerator:
    latency: AttributeGenerator
    bandwidth: AttributeGenerator

    def generate(self, i, j, random_state: RandomState) -> Link:
        return Link(
            i,
            j,
            self.latency.generate(random_state),
            self.bandwidth.generate(random_state),
        )


@dataclass(frozen=True)
class ServiceLinkGenerator:
    latency: AttributeGenerator

    def generate(self, source, target, random_state: RandomState) -> ServiceLink:
        return ServiceLink(
            source,
            target,
            self.latency.generate(random_state),
        )

@dataclass(frozen=True)
class ServiceGenerator:
    service_type: AttributeGenerator
    service_counts = {}

    def reset_count(self):
        self.service_counts.clear()
   
    def load_configurations(self):
        try:
            with open(NodesConfigurations.services_config, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {NodesConfigurations.services_config}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get_matching_configs(self, _service_name) -> str:
        configs = self.load_configurations()['services']
        if _service_name.lower() in configs:
            return configs[_service_name.lower()]
        else:
            return {}
    
    def generate(self, random_state: RandomState) -> Service:
        
        _service_type =  self.service_type.generate(random_state=random_state)

        template = self.get_matching_configs(_service_type)
        
        if _service_type not in self.service_counts:
            self.service_counts[_service_type] = 0
        self.service_counts[_service_type] += 1
        
        service_id = f"{self.service_counts[_service_type]}_{_service_type}"
        
        if not template:
            raise ValueError(f"No configurations found for service type: {_service_type}")
        
        return Service(
            id=str(service_id), 
            storage_gb=int(template['storage_gb']),
            ram_gb=int(template['ram_gb']),
            availability=float(template['availability']),
            cpu=int(template['cpu']),
            bandwidth_in=int(template['bandwidth_in']),
            bandwidth_out=int(template['bandwidth_out']),
            gpu=bool(template['gpu']),
            access_control=bool(template['access_control']),
            anti_tampering=bool(template['anti_tampering']),
            encryption=bool(template['encryption']),
            carbon_intensity=int(template['carbon_intensity']*1000),
            pue=int(template['pue']*10),
            cost=int(template['cost']),
        )


@dataclass(frozen=True)
class ApplicationGenerator:
    topology: GraphGenerator  # non sono sicuro, gli attributi dei link cambiano.
    node: ServiceGenerator
    link: AttributeGenerator  # penso l'unico link-attr sarà latency
    
    def generate(self, random_state: RandomState) -> NetworkSnapshot:
        self.node.reset_count()
        g = self.topology.generate(random_state)
        generated_nodes = {node_key: self.node.generate(random_state) for node_key in g.nodes}
        
        return NetworkSnapshot(
            list(generated_nodes.values()),
            [self.link.generate(generated_nodes[i].id, generated_nodes[j].id, random_state) for i, j in g.edges], # brutto ma dovrebbe funzionare
        )


@dataclass(frozen=True)
class NetworkGenerator:
    complete: bool
    topology: GraphGenerator
    node: NodeGenerator
    link: LinkGenerator

    def generate(self, random_state: RandomState) -> NetworkSnapshot:
        if not self.complete:
            g = self.topology.generate(random_state)
        else:
            g = self.topology.generate()

        return NetworkSnapshot(
            [self.node.generate(i, random_state) for i in g.nodes],
            [self.link.generate(i, j, random_state) for i, j in g.edges],
        )
