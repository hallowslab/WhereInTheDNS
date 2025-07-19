import re
import json
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="Where in the DNS",
        description="Queries nameservers provided in a config file to find the machine hosting the domain",
        epilog="""
    Examples:
        witd -d example.com
        witd -cf ./config-file.json -d example.com
    """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d", "--domain", required=True, type=str, help="Domain to find"
    )
    parser.add_argument(
        "-cf",
        "--config-file",
        default="",
        type=str,
        help="Path for different configuration file",
    )
    parser.add_argument(
        "-wt", "--wait-timer", default=None, help="Time to wait between requests"
    )
    return parser


def load_config(file: str):
    with open(file, "r") as f:
        return json.load(f)


def expand_pattern(pattern: str) -> list[str] | str:
    match = re.search(r"\[([0-9]+)-([0-9]+)\]", pattern)
    if not match:
        return [pattern]

    start, end = int(match.group(1)), int(match.group(2))
    expanded: list[str] = []
    for i in range(start, end + 1):
        expanded.append(re.sub(r"\[[0-9]+-[0-9]+\]", str(i), pattern))
    return expanded
