from argparse import ArgumentParser
import os
from pathlib import Path
from typing import List

NET_SIZES = list(range(50,550,50))
APP_SIZES = [5, 10, 15, 20]

def get_files_from_folder(folder_path, sizes: List[str]):
    files = {
        s: [] for s in sizes
    }

    for size in files.keys():
        size_folder = os.path.join(folder_path, size)
        if os.path.exists(size_folder):
            files[size] = [os.path.join(size_folder, f) for f in os.listdir(size_folder) if f.endswith('.lp')]
    return files

def generate_instances(network_folder: str, app_folder: str, out_folder:str):
    if network_folder == None:
        net_folder = (Path(__file__).parent).as_posix()+'/generated_network'
    else:
        net_folder = network_folder

    if app_folder == None:
        app_folder = (Path(__file__).parent).as_posix()+'/generated_application'
    else:
        app_folder = app_folder

    if out_folder == None:
        out_folder = (Path(__file__).parent).as_posix()+'/generated_instances'
    else:
        out_folder = out_folder

    net_files = get_files_from_folder(net_folder, [str(s) for s in NET_SIZES])
    app_files = get_files_from_folder(app_folder, [str(s) for s in APP_SIZES])

    for size_n in net_files.keys():
        net_size_files = net_files[size_n]
        for size_a in app_files.keys():
            app_size_files = app_files[size_a]

            if not net_size_files or not app_size_files:
                continue

            for net in net_size_files:
                for app in app_size_files:
                    uuid_net = os.path.basename(net).split('-')[-1].split('.')[0]
                    uuid_app = os.path.basename(app).split('-')[-1].split('.')[0]

                    output_filename = f"i-{size_n}_{size_a}-{uuid_net}_{uuid_app}.lp"
                    output_filepath = os.path.join(out_folder, output_filename)

                    if not os.path.exists(f"{out_folder}"):
                        os.makedirs(f"{out_folder}")

                    with open(output_filepath, 'w') as output_file:
                        with open(net, 'r') as f1, open(app, 'r') as f2:
                            output_file.write(f1.read())
                            output_file.write("\n")
                            output_file.write(f2.read())

if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("network_folder", type=str, help="Path to the network folder.")
    p.add_argument("app_folder", type=str, help="Path to the application folder.")
    p.add_argument("out_folder",type=str, help="Path to the output folder.")
    args = p.parse_args()

    generate_instances(network_folder=args.network_folder,
                       app_folder=args.app_folder,
                       out_folder=args.out_folder)

