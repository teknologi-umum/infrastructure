import platform
import subprocess
import time
import sys
import os
from pathlib import Path
from paramiko.client import SSHClient
from paramiko.config import SSHConfig
import sentry_sdk


SERVICE_MAPPING: dict[str, list[str]] = {
    "tanzanite.gems.teknologiumum.com": [
        "traefik",
        "bot",
        "captcha",
        "gitgram",
        # "gold", We'll skip gold for now as it's private repository
        "graphene",
        "libreddit",
        "monitoring",
        "pesto",
        "polarite",
        "pph21",
        "projects",
        "tgif",
        "watchtower",
    ],
    "painite.gems.teknologiumum.com": [
        "traefik",
        "git",
        "umami",
        "uptime-kuma",
        "watchtower",
    ],
    "hibonite.gems.teknologiumum.com": [
        "traefik",
        "bagetter",
        "goproxy",
        "verdaccio",
        "watchtower",
    ],
}

SUDO_PASSWORD: dict[str, str] = {
    "tanzanite.gems.teknologiumum.com": os.getenv("TANZANITE_SUDO_PASSWORD", ""),
    "painite.gems.teknologiumum.com": os.getenv("PAINITE_SUDO_PASSWORD", ""),
    "hibonite.gems.teknologiumum.com": os.getenv("HIBONITE_SUDO_PASSWORD", ""),
}


def ping(host: str) -> bool:
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


if __name__ == "__main__":
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

    for server, containers in SERVICE_MAPPING.items():
        # Check if server is available
        for i in range(10):
            server_up = ping(server)
            if server_up:
                break
            else:
                if i + 1 == 10:
                    # We've waited too long
                    print(f"Waited too long while trying to reach for {server}")
                    exit(4200)

                # Wait for 10 seconds before the next ping
                print("Retrying in 10 seconds")
                time.sleep(10)
                continue

        for container in containers:
            # Copy directory to destination
            subprocess.call(
                f"rsync -avz --progress {container} {server}:{container}".split(" "),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        ssh_config = SSHConfig.from_path(f"{Path.home()}/.ssh/config")
        server_config = ssh_config.lookup(server)

        with SSHClient() as client:
            client.load_system_host_keys(f"{Path.home()}/.ssh/known_hosts")
            client.connect(
                hostname=server_config.get("hostname"),
                port=server_config.as_int("port"),
                username=server_config.get("user"),
                key_filename=server_config.get("identityfile"),
            )

            for container in containers:
                print(f"Running commands for {container} on {server}")
                _, o1, e1 = client.exec_command(
                    f"echo '{SUDO_PASSWORD[server]}' | sudo -S bash -c 'cd {container}; if [ -f \"setup.sh\" ]; then\n  chmod +x setup.sh && sudo ./setup.sh\nfi'"
                )
                for c in iter(lambda: o1.read(1), b""):
                    sys.stdout.buffer.write(c)
                for c in iter(lambda: e1.read(1), b""):
                    sys.stderr.buffer.write(c)

                _, o2, e2 = client.exec_command(
                    f"echo '{SUDO_PASSWORD[server]}' | sudo -S bash -c 'cd {container}; docker compose up -d'"
                )
                for c in iter(lambda: o2.read(1), b""):
                    sys.stdout.buffer.write(c)
                for c in iter(lambda: e2.read(1), b""):
                    sys.stderr.buffer.write(c)
