
from rich.console import Console
from rich.table import Table
from rich import print




# def checkin():
#     payload = {
#         "uuid": str(uuid.uuid4()),  # ID định danh agent
#         "hostname": socket.gethostname(),  # tên máy
#         "username": getpass.getuser(),  # user đang chạy
#         "os": platform.system(),  # Windows/Linux/Darwin
#         "os_version": platform.version(),  # version cụ thể
#         "arch": platform.machine(),  # x86/x64/ARM
#     }
#     for x in payload:
#         print(payload[x])
#
# if __name__ == "__main__":
#     checkin()


# Test sample
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

result = Table(title="TEST")


result.add_column(header="SESSION ID", justify="center", no_wrap=True)
result.add_column(header="HOSTNAME", justify="center", no_wrap=True)
result.add_column(header="IP", justify="center", no_wrap=True)
result.add_column(header="PORT", justify="center", no_wrap=True)
result.add_column(header="OS", justify="center", no_wrap=True)
result.add_column(header="LAST BEACON", justify="center", no_wrap=True)
result.add_column(header="STATUS", justify="center", no_wrap=True)


for x in clients:
    result.add_row(str(x['id']),
                  str(x['hostname']),
                  str(x['ip']),
                  str(x['port']),
                  str(x['os']),
                  str(x['last_beacon']) + ' (s)',
                  f"[green]{x['status']}[/green]" if x['status'] == "ONLINE" else str(x['status'])
                  )

console = Console(width=300)
console.print(result)

print(f"[blue]Total: {len(clients)} client(s)[/blue]")