from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
from backend.models import DeviceInventory


def device_connection(ip_addr: str, credentials: dict) -> ConnectHandler:
    remote_device = {
        "device_type": "autodetect",
        "host": ip_addr,
        "username": credentials.get("username"),
        "password": credentials.get("password"),
    }

    try:
        guesser = SSHDetect(**remote_device)
        best_match = guesser.autodetect()
        remote_device["device_type"] = best_match
        connection = ConnectHandler(**remote_device)
    except (
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
    ) as e:
        print(f"Could not connect to device due to the following error: {e}")
        connection = None

    return connection


def discover_device(device_conn: ConnectHandler) -> DeviceInventory:
    if (
        device_conn.device_type == "cisco_ios"
    ):  # May replace with regex exp to match on 'cisco'
        try:
            sh_ver = device_conn.send_command("show version", use_genie=True)
            discovered_device = DeviceInventory(
                hostname=sh_ver["version"]["hostname"],
                mgmt_ip=device_conn.host,
                vendor="Cisco",
                model=sh_ver["version"]["chassis"],
                os_version=sh_ver["version"]["version"],
                serial_number=sh_ver["version"]["chassis_sn"],
            )
        except (
            NetmikoTimeoutException,
            NetmikoAuthenticationException,
        ) as e:
            print(f"Could not connect to device due to the following error: {e}")
            discovered_device = None
    else:
        # Defaulting to None for now
        discovered_device = None

    return discovered_device
