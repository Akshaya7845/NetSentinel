from datetime import datetime
from typing import Dict, Any
import random


class AzureNetworkWatcher:
    """
    Simulated Azure Network Watcher service for NetSentinel.

    This implementation provides connectivity and network-path
    monitoring without requiring live Azure credentials.
    """

    def __init__(self):
        self.paths = {
            "Login API": "http://localhost:8000/login",
            "Product API": "http://localhost:8000/products",
            "Payment API": "http://localhost:8000/payment",
        }

    def check_connectivity(self) -> Dict[str, Any]:
        """
        Check connectivity for the configured network paths.
        """

        results = {}

        for name, endpoint in self.paths.items():

            # Simulated network metrics
            latency_ms = round(random.uniform(10, 80), 2)
            packet_loss = 0.0

            results[name] = {
                "source": "NetSentinel",
                "destination": endpoint,
                "status": "Reachable",
                "latency_ms": latency_ms,
                "packet_loss_percent": packet_loss,
                "timestamp": datetime.now().isoformat(),
            }

        return results

    def get_network_summary(self) -> Dict[str, Any]:
        """
        Return an overall summary of network connectivity.
        """

        results = self.check_connectivity()

        total_paths = len(results)

        reachable_paths = sum(
            1
            for result in results.values()
            if result["status"] == "Reachable"
        )

        unreachable_paths = total_paths - reachable_paths

        latencies = [
            result["latency_ms"]
            for result in results.values()
        ]

        average_latency = (
            round(sum(latencies) / len(latencies), 2)
            if latencies
            else 0.0
        )

        return {
            "status": (
                "Healthy"
                if unreachable_paths == 0
                else "Degraded"
            ),
            "total_paths": total_paths,
            "reachable_paths": reachable_paths,
            "unreachable_paths": unreachable_paths,
            "average_latency_ms": average_latency,
            "paths": results,
            "timestamp": datetime.now().isoformat(),
        }

    def get_path_status(self) -> Dict[str, Any]:
        """
        Return the status of each monitored network path.
        """

        results = self.check_connectivity()

        return {
            "status": "success",
            "paths": results,
            "timestamp": datetime.now().isoformat(),
        }


azure_network_watcher = AzureNetworkWatcher()
