import docker


def get_container_status():
    """
    Returns the status of all NetSentinel containers.

    If Docker is unavailable (for example in GitHub Actions),
    return a default status instead of raising an exception.
    """

    status = {
        "nginx": "stopped",
        "postgres": "stopped",
        "prometheus": "stopped"
    }

    try:
        client = docker.from_env()
        containers = client.containers.list()

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

    except Exception:
        # Docker is unavailable (e.g., GitHub Actions)
        return {
            "containers_running": 0,
            "container_status": status
        }