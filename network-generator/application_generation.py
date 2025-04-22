import sys
from numpy.random import RandomState
import uuid
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
    UniformContinuous,
)
from random_network_generator.asp_generator import net_to_asp
from argparse import ArgumentParser
from random_network_generator.asp_generator import app_to_asp


def generate_services(seed:int, services_config: str, services_number: int, services_dir: str, probability:float):

    if services_config is not None:
        NodesConfigurations.set_services_config(services_config)

    r = RandomState(seed)

    base_out_path = services_dir

    net_size = services_number

    generator = ApplicationGenerator(
        ErdosRenyi(n=net_size, p=probability),
        ServiceGenerator(
            service_type=UniformDiscrete('ml_optimiser','video_stream_processor','data_analytics','iot_controller','web_server', 'database_service', 'cloud_storage_service')
            ),
        ServiceLinkGenerator(
            latency=UniformDiscrete(50, 100, 150, 250, 500)
        )
    )
    
    generated_application = generator.generate(r)
    
    app_to_asp(generated_application, f"{base_out_path}/{services_number}/a-{services_number}-{uuid.uuid4().hex[:8]}.lp")

if __name__ == "__main__":

    APP_SIZE = [5, 10, 15] 
    P = 0.6
       
    for size in APP_SIZE:
        generate_services(42, "random_network_generator/services_config.yaml", size, "generated_application", P)
