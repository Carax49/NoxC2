from rich.table import Table
from rich.console import Console


clients = [
    {
        "id": "a1b2c3d4-e111-2222-3333-abcdef123456",
        "hostname": "WIN-DEV01",
        "ip": "192.168.1.10",
        "port": 50021,
        "last_beacon": 41,
        "os": "Windows 10 25H2",
        "status": "OFFLINE"
    },
    {
        "id": "b2c3d4e5-f222-3333-4444-bcdefa234567",
        "hostname": "LAPTOP-XYZ",
        "ip": "192.168.1.15",
        "port": 52311,
        "os": "Ubuntu 14.04",
        "last_beacon": 30,
        "status": "OFFLINE"
    },
    {
        "id": "c3d4e5f6-a333-4444-5555-cdefab345678",
        "hostname": "OFFICE-PC",
        "ip": "192.168.1.20",
        "port": 49876,
        "os": "MacOS",
        "last_beacon": 26,
        "status": "ONLINE"
    }
]


if __name__ == "__main__":
    table = Table()

    table.add_column(header="FIELD", style="cyan", justify="center")
    table.add_column(header="DETAIL", style="magenta", justify="center")

    for key, values in clients[0].items():
        table.add_row(key.upper(), str(values))

    console = Console(width=200)
    console.print(table)
