# WhereInTheDNS(WITD)

WhereInTheDNS(WITD) is a tool to identify where a domain is hosted within a DNS cluster, check which machine holds the PTR/rDNS records, and determine if the domain is being resolved by internal or external machines.

## Features
- Query multiple nameservers to locate domain zones in a cluster
- Identify the responsible machine for PTR / rDNS records
- Use configurable cluster definitions via JSON
- Build cross-platform executables using Poetry + PyInstaller
- Supports Linux, Windows, macOS

## Configuration
1. Nameservers
Define your nameservers in config.json:
```json
{
    "nameservers": [
        "ns1.example.com",
        "dns1.example.com"
    ]
}
```

2. Cluster Machines
Define machines in config.json.
Supports range expansion:
```json
{
"machines": [
    "web{1..100}.example.com",
    "vps.example.com"
]
}
```
The checker will expand web[1-100] into web1, web2, ..., web100.

Final file should look like:

```json
{
    "nameservers": [
        "ns1.example.com",
        "dns1.example.com"
    ],
    "machines": [
        "web{1..100}.example.com",
        "vps.example.com"
    ]
}
```

## Usage
Development

- Install dependencies:
```bash
poetry install
```

- Create a config file as described in [Configuration](#configuration)

- Run the tool:
```bash
cd src
poetry run main.py -d <domain>
```

- Build Standalone Executable
    * Use Poetry + PyInstaller:
```bash
poetry run pyinstaller --onefile --name witd dns_checker/__main__.py
```
Output: dist/witd (or .exe on Windows)