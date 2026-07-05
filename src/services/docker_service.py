import docker


def get_container_status():
    """
    Returns the status of all running NetSentinel containers.
    """

    client = docker.from_env()

    containers = client.containers.list()

    status = {
        "nginx": "stopped",
        "postgres": "stopped",
        "prometheus": "stopped"
    }

    running_count = 0

    for container in containers:

        running_count += 1

        if "netsentinel-web" in container.name:
            status["nginx"] = "running"

        elif "netsentinel-db" in container.name:
            status["postgres"] = "running"

        elif "netsentinel-prometheus" in container.name:
            status["prometheus"] = "running"

    return {
        "containers_running": running_count,
        "container_status": status
    }