import subprocess
import sys

from time import sleep
from argparse import Namespace
from pathlib import Path

from utils import build_parser, load_config, expand_pattern, check_has_dig

from _version import __version__

def run_dig(domain, server=None, reverse=False):
    cmd = ["dig", "+short"]
    if reverse:
        cmd += ["-x", domain]
    else:
        cmd.append(domain)
        if server:
            cmd.append(f"@{server}")

    try:
        output = (
            subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        )
        return output.splitlines()
    except subprocess.CalledProcessError:
        return []


def find_cluster_owner(domain, nameservers) -> str | None:
    for ns in nameservers:
        result = run_dig(domain, server=ns)
        if result:
            print(f"Domain {domain} found in cluster at nameserver {ns}: {result[0]}")
            return result[0]
    return None


def check_ptr(ip) -> str | None:
    ptr = run_dig(ip, reverse=True)
    return ptr[0].rstrip(".") if ptr else None


def check_machines(domain: str, machines, wait_timer: float | None = None):
    active_machines = []
    for machine in machines:
        result = run_dig(domain, machine)
        # print(f"Checking {machine}, result: {result}")
        if result:
            ptr = check_ptr(result[0]) or "PTR not found"
            active_machines.append((machine, result[0], ptr))
        if wait_timer:
            sleep(wait_timer)
    return active_machines


def main() -> None:
    args: Namespace = build_parser().parse_args()
    config: dict[str, list[str]] = {}
    domain: str = args.domain

    if args.version:
        print(f"Version: {__version__}")
        sys.exit(1)

    if not check_has_dig():
        print("You need to install dig")
        sys.exit(1)

    # If provided empty string it points to "." and shouldn't resolve to a file
    if Path(args.config_file).is_file():
        try:
            config = load_config(args.config_file)
        except:
            raise
    else:
        config = load_config("config.json")

    print(f"Loaded config {config}")

    nameservers = config["nameservers"]

    # Expand machine patterns
    machines: list[str] = []
    for pattern in config["hosts"]:
        machines += expand_pattern(pattern)

    ip = find_cluster_owner(domain, nameservers)

    if not ip:
        print(f"Domain {domain} not found in specified nameservers.")
        ip = run_dig(domain)
        ip = ip[0] if ip else None

    if not ip:
        print("Could not resolve domain IP.")
        sys.exit(1)

    print(f"Domain {domain} resolves to IP: {ip}")

    ptr_record = check_ptr(ip)
    print(f"PTR/rDNS for {ip}: {ptr_record}")

    active_machines = check_machines(domain, machines, args.wait_timer)

    found = False
    for machine, machine_ip, machine_ptr in active_machines:
        print(f"Machine: {machine} has PTR: {machine_ptr}")
        if machine_ptr == ptr_record:
            print(
                f"Domain resolves through machine {machine} ({machine_ip}), matches PTR."
            )
            found = True
            break

    if not found:
        print("PTR/rDNS machine did not respond directly.")
        if active_machines:
            print("Active machines where domain responds:")
            for machine, machine_ip, machine_ptr in active_machines:
                print(f" - {machine} ({machine_ip}, PTR: {machine_ptr})")
        elif ptr_record in machines:
            print(f"Domain resolves to: {ptr_record}")
        else:
            print("Domain not found in any cluster machine.")


if __name__ == "__main__":
    main()
