SERVICE_MAPPING = {
    "tanzanite.gems.teknologiumum.com": [
        "traefik",
        "bot",
        "captcha",
        "gitgram",
        "gold",
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

if __name__ == "__main__":
    for server, containers in SERVICE_MAPPING.items():
        # SSH to server
        # Copy directory with rsync

    