from pathlib import Path
from network_generator import generate_network
from instances_gen_script import generate_instances, APP_SIZES, NET_SIZES
from application_generation import generate_services
from numpy.random import RandomState

P=0.25

if __name__ == "__main__":

    path = (Path(__file__).parent).as_posix()

    rng = RandomState(0)

    ## NETWORKs GENERATION
    print(f"NETWORKs GENERATION...")
    for i in range(10):
        for size in NET_SIZES:
            generate_network(seed=rng.randint(0, 9999),
                             nodes_config=f"{path}/random_network_generator/nodes_config.yaml",
                             nodes_number=size,
                             network_dir=None,
                             min_latency=10,
                             max_latency=50
                             )

    ## APPLICATIONs GENERATION
    print(f"APPLICATIONs GENERATION...")
    for i in range(10):
        for size in APP_SIZES:
            generate_services(seed=rng.randint(0, 9999), 
                              services_config="random_network_generator/services_config.yaml", 
                              services_number=size, 
                              services_dir="generated_application", 
                              probability=P)

    ## INSTANCEs GENERATION
    print(f"INSTANCEs GENERATION...")
    generate_instances(None, None, None)
    
