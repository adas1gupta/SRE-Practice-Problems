import argparse
import os

parser = argparse.ArgumentParser(description="cgroups resource enforcer")
parser.add_argument("--name", required=True, help="Name for the cgroup")
args = parser.parse_args() # parses into key value pairs, but in a namespace, not a dict (e.g, "name": ?)

cgroup_name = args.name

os.makedirs(f"/sys/fs/cgroup/{cgroup_name}/")

