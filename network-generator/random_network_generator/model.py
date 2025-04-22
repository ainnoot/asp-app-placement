import dataclasses
import typing
import clingo
from random_network_generator.clingo_utils import as_clingo_term

def hreq(service, expr):
	return clingo.Function('hreq', [service, expr])

def sreq(service, expr):
	return clingo.Function('sreq', [service, expr])

class Constraints:
	@staticmethod
	def requirement_expr(name, resource, value):
		return clingo.Function(name, [as_clingo_term(resource), as_clingo_term(value)])

	@staticmethod
	def reserve(name, threshold):
		return Constraints.requirement_expr('reserve', name, threshold)

	@staticmethod
	def gt(name, threshold):
		return Constraints.requirement_expr('gt', name, threshold)

	@staticmethod
	def gte(name, threshold):
		return Constraints.requirement_expr('gte', name, threshold)

	@staticmethod
	def lt(name, threshold):
		return Constraints.requirement_expr('lt', name, threshold)

	@staticmethod
	def lte(name, threshold):
		return Constraints.requirement_expr('lte', name, threshold)

	@staticmethod
	def eq(name, threshold):
		return Constraints.requirement_expr('eq', name, threshold)

	@staticmethod
	def neq(name, threshold):
		return Constraints.requirement_expr('neq', name, threshold)

@dataclasses.dataclass(frozen=True)
class Node:
    id: int
    storage_gb: int
    ram_gb: int
    availability: int
    cpu: int
    gpu: bool
    bandwidth_in: int
    bandwidth_out: int
    access_control: bool
    anti_tampering: bool
    encryption: bool
    carbon_intensity: int   # mg CO2-eq/kWh
    pue: int                # pue*10
    cost: int

    def reify(self):
        yield clingo.Function('node', [as_clingo_term(self.id)])
        attrs = set(self.__dataclass_fields__.keys())
        attrs.remove('id')		

        for k in attrs:
            yield clingo.Function(
                "node_attr",
                [
                    as_clingo_term(self.id),
                    as_clingo_term(k),
                    as_clingo_term(self.__getattribute__(k)),
                ],
            )


@dataclasses.dataclass(frozen=True)
class Link:
    source: int
    target: int
    latency: int
    bandwidth: float

    def reify(self):
        yield clingo.Function('link', [as_clingo_term(self.source), as_clingo_term(self.target)])
        yield clingo.Function(
            "link_attr",
            [
                as_clingo_term(self.source),
                as_clingo_term(self.target),
                as_clingo_term("latency"),
                as_clingo_term(self.latency),
            ],
        )

@dataclasses.dataclass(frozen=True)
class ServiceLink:
    source: str
    target: str
    latency: int

    def reify(self):
        yield sreq(
            clingo.Function('', [as_clingo_term(self.source), as_clingo_term(self.target)]),
            Constraints.lte('latency', self.latency)
        )

@dataclasses.dataclass(frozen=True)
class Service:
    id: str
    storage_gb: int			
    ram_gb: int 			
    availability: int		
    cpu: int				
    bandwidth_in: int		
    bandwidth_out: int		
    gpu: bool				
    access_control: bool
    anti_tampering: bool	
    encryption: bool		
    carbon_intensity: int   # mg CO2-eq/kWh
    pue: int                # pue*10
    cost: int               # pue*10

    def reify(self):
        service = as_clingo_term(self.id)

        yield clingo.Function("service", [service])

        for f in ('ram_gb', 'storage_gb', 'cpu', 'bandwidth_in', 'bandwidth_out'):
            yield hreq(service, Constraints.reserve(f, self.__getattribute__(f)))

        yield sreq(service, Constraints.gte('availability', self.availability))

        if self.gpu:
            yield sreq(service, Constraints.eq('gpu', self.gpu)) 

        if self.access_control:
            yield sreq(service, Constraints.eq('access_control', self.access_control))

        if self.encryption:
            yield sreq(service, Constraints.eq('encryption', self.encryption))

        if self.anti_tampering:
            yield sreq(service, Constraints.eq('anti_tampering', self.anti_tampering))
    
        yield sreq(service, Constraints.lte('carbon_intensity', self.carbon_intensity))

        yield sreq(service, Constraints.lte('pue', self.pue))

        yield sreq(service, Constraints.lte('cost', self.cost))


@dataclasses.dataclass(frozen=True)
class NetworkSnapshot:
    nodes: typing.Iterable[Node]
    links: typing.Iterable[Link]

    def __str__(self):
        string = [
            "A network on {} nodes and {} links.".format(
                len(self.nodes), len(self.links)
            )
        ]
        string.append("Nodes:\n")
        for node in self.nodes:
            string.append(
                "\t[{}] - {:.3f} MB".format(
                    node.id,
                    node.storage_gb,
                )
            )

        string.append("Links:\n")
        for link in self.links:
            string.append(
                "\t{} -- {} - {:.3f}ms {:.3f}MB/s\n".format(
                    link.source, link.target, link.latency, link.bandwidth
                )
            )

        return "".join(string)
