"""
System monitoring and anomaly detection.
"""

import logging
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    Monitor system resources: CPU, memory, disk, network.

    Provides real-time system metrics collection and process monitoring.
    """

    def __init__(self) -> None:
        """Initialize system monitor."""
        if psutil is None:
            logger.warning("psutil not installed. Some features will be unavailable.")
        self.last_net_io = None
        if psutil:
            self.last_net_io = psutil.net_io_counters()

    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage percentage (0-100)
        """
        if not psutil:
            return 0.0
        return psutil.cpu_percent(interval=0.1)

    def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage.

        Returns:
            Memory usage percentage (0-100)
        """
        if not psutil:
            return 0.0
        return psutil.virtual_memory().percent

    def get_disk_usage(self) -> float:
        """
        Get disk usage percentage for root partition.

        Returns:
            Disk usage percentage (0-100)
        """
        if not psutil:
            return 0.0
        return psutil.disk_usage('/').percent

    def get_network_stats(self) -> Dict[str, int]:
        """
        Get network I/O statistics.

        Returns:
            Dictionary with keys: bytes_sent, bytes_recv, packets_sent, packets_recv
        """
        if not psutil:
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
            }

        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect all system metrics.

        Returns:
            Dictionary with all system metrics and timestamp
        """
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "disk_usage": self.get_disk_usage(),
            "network": self.get_network_stats(),
        }
        logger.debug(f"Collected system metrics: {metrics}")
        return metrics

    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """
        Get resource usage for specific process.

        Args:
            pid: Process ID

        Returns:
            Dictionary with process name, CPU percent, memory info
        """
        if not psutil:
            return {}

        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    "pid": pid,
                    "name": proc.name(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                    "status": proc.status(),
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error accessing process {pid}: {e}")
            return {}


class AnomalyDetector:
    """
    Detect anomalies in metrics using statistical Z-score method.

    Anomaly = (value - mean) / std_dev > threshold
    """

    def __init__(self, threshold: float = 2.0) -> None:
        """
        Initialize anomaly detector.

        Args:
            threshold: Z-score threshold for anomaly detection (default 2.0)
        """
        self.threshold = threshold
        self.metrics_history: Dict[str, List[float]] = defaultdict(list)
        logger.info(f"Initialized AnomalyDetector with threshold={threshold}")

    def add_observation(self, metric_name: str, value: float) -> None:
        """
        Add observation for a metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.metrics_history[metric_name].append(value)
        logger.debug(f"Added observation for {metric_name}: {value}")

    def get_statistics(self, metric_name: str) -> Dict[str, float]:
        """
        Get statistical summary for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary with mean, std_dev, min, max, count
        """
        values = self.metrics_history.get(metric_name, [])

        if not values:
            return {
                "mean": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0,
            }

        return {
            "mean": statistics.mean(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
            "count": len(values),
        }

    def is_anomaly(self, metric_name: str, value: float) -> bool:
        """
        Check if a single value is an anomaly.

        Args:
            metric_name: Name of the metric
            value: Value to check

        Returns:
            True if value is anomalous
        """
        stats = self.get_statistics(metric_name)

        if stats["std_dev"] == 0:
            return False

        z_score = abs((value - stats["mean"]) / stats["std_dev"])
        is_anom = z_score > self.threshold

        if is_anom:
            logger.warning(
                f"Anomaly detected in {metric_name}: "
                f"value={value}, z_score={z_score:.2f}"
            )

        return is_anom

    def detect_anomalies(self, metric_name: str) -> List[Dict[str, Any]]:
        """
        Detect all anomalies in metric history.

        Args:
            metric_name: Name of the metric

        Returns:
            List of anomalies with index, value, z_score
        """
        values = self.metrics_history.get(metric_name, [])
        stats = self.get_statistics(metric_name)
        anomalies = []

        if stats["std_dev"] == 0:
            return []

        for i, value in enumerate(values):
            z_score = abs((value - stats["mean"]) / stats["std_dev"])
            if z_score > self.threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": z_score,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        logger.info(
            f"Detected {len(anomalies)} anomalies in {metric_name}"
        )
        return anomalies
