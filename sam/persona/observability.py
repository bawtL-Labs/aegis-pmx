"""
Observability Manager for personality matrix monitoring.

This module handles tracing, monitoring, and observability features
for the personality matrix system.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    PersonalityConfig,
    StyleTrace,
)


logger = logging.getLogger(__name__)


class ObservabilityManager:
    """
    Manages observability, tracing, and monitoring for the personality matrix.
    
    This class handles style traces, drift detection, performance monitoring,
    and observability features for debugging and analysis.
    """
    
    def __init__(self, config: PersonalityConfig):
        """
        Initialize the observability manager.
        
        Args:
            config: Personality configuration
        """
        self.config = config
        
        # Storage for traces and metrics
        self._traces: List[StyleTrace] = []
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._drift_alerts: List[Dict[str, Any]] = []
        
        # Performance tracking
        self._performance_metrics = {
            "style_synthesis_time": [],
            "state_update_time": [],
            "boundary_adjustment_time": [],
            "memory_lensing_time": [],
        }
        
        logger.info("Observability Manager initialized")
    
    def record_trace(self, trace: StyleTrace) -> None:
        """
        Record a style trace for observability.
        
        Args:
            trace: Style trace to record
        """
        # Add trace to storage
        self._traces.append(trace)
        
        # Maintain trace retention policy
        self._cleanup_old_traces()
        
        # Check for drift
        if self.config.enable_drift_alerts:
            self._check_for_drift(trace)
        
        logger.debug("Recorded style trace: %s", trace.id)
    
    def get_recent_traces(self, limit: int = 10) -> List[StyleTrace]:
        """
        Get recent style traces.
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            List of recent style traces
        """
        # Sort by timestamp (newest first)
        sorted_traces = sorted(self._traces, key=lambda t: t.ts, reverse=True)
        
        return sorted_traces[:limit]
    
    def get_traces_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[StyleTrace]:
        """
        Get traces within a specific time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of traces in the time range
        """
        return [
            trace for trace in self._traces
            if start_time <= trace.ts <= end_time
        ]
    
    def get_traces_by_event_type(self, event_type: str) -> List[StyleTrace]:
        """
        Get traces for a specific event type.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of traces for the event type
        """
        return [
            trace for trace in self._traces
            if trace.inputs.get("event_type") == event_type
        ]
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
        """
        metric_entry = {
            "timestamp": datetime.utcnow(),
            "value": value,
            "tags": tags or {},
        }
        
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        self._metrics[metric_name].append(metric_entry)
        
        # Maintain metric retention
        self._cleanup_old_metrics()
        
        logger.debug("Recorded metric: %s = %.3f", metric_name, value)
    
    def record_performance_metric(
        self,
        operation: str,
        duration: float
    ) -> None:
        """
        Record a performance metric for an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
        """
        if operation in self._performance_metrics:
            self._performance_metrics[operation].append({
                "timestamp": datetime.utcnow(),
                "duration": duration,
            })
            
            # Keep only recent performance data
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self._performance_metrics[operation] = [
                entry for entry in self._performance_metrics[operation]
                if entry["timestamp"] > cutoff
            ]
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get a summary of performance metrics.
        
        Returns:
            Dictionary of performance summaries
        """
        summary = {}
        
        for operation, entries in self._performance_metrics.items():
            if entries:
                durations = [entry["duration"] for entry in entries]
                summary[operation] = {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
                }
            else:
                summary[operation] = {
                    "count": 0,
                    "avg_duration": 0.0,
                    "min_duration": 0.0,
                    "max_duration": 0.0,
                    "p95_duration": 0.0,
                }
        
        return summary
    
    def get_style_evolution_summary(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get a summary of style evolution over time.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Style evolution summary
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_traces = [
            trace for trace in self._traces
            if trace.ts > cutoff
        ]
        
        if not recent_traces:
            return {"message": "No recent traces available"}
        
        # Analyze style changes
        style_changes = []
        for trace in recent_traces:
            if trace.style_delta:
                style_changes.append(trace.style_delta)
        
        # Calculate statistics
        total_changes = len(style_changes)
        if total_changes == 0:
            return {"message": "No style changes detected"}
        
        # Analyze change patterns
        change_types = {}
        for change in style_changes:
            for dimension, delta in change.items():
                if dimension not in change_types:
                    change_types[dimension] = []
                change_types[dimension].append(delta)
        
        # Calculate summary statistics
        summary = {
            "total_traces": len(recent_traces),
            "total_style_changes": total_changes,
            "change_frequency": total_changes / len(recent_traces),
            "dimension_changes": {},
        }
        
        for dimension, deltas in change_types.items():
            # Parse delta strings to get numeric values
            numeric_deltas = []
            for delta in deltas:
                try:
                    if delta.startswith("+"):
                        numeric_deltas.append(float(delta[1:]))
                    elif delta.startswith("-"):
                        numeric_deltas.append(-float(delta[1:]))
                    else:
                        numeric_deltas.append(float(delta))
                except ValueError:
                    continue
            
            if numeric_deltas:
                summary["dimension_changes"][dimension] = {
                    "count": len(numeric_deltas),
                    "avg_change": sum(numeric_deltas) / len(numeric_deltas),
                    "max_increase": max(numeric_deltas) if numeric_deltas else 0.0,
                    "max_decrease": min(numeric_deltas) if numeric_deltas else 0.0,
                }
        
        return summary
    
    def get_drift_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent drift alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of drift alerts
        """
        return self._drift_alerts[-limit:]
    
    def export_traces(
        self,
        format: str = "json",
        time_range: Optional[tuple] = None
    ) -> str:
        """
        Export traces in the specified format.
        
        Args:
            format: Export format ("json" or "csv")
            time_range: Optional (start_time, end_time) tuple
            
        Returns:
            Exported traces as string
        """
        if time_range:
            start_time, end_time = time_range
            traces = self.get_traces_by_time_range(start_time, end_time)
        else:
            traces = self._traces
        
        if format.lower() == "json":
            return json.dumps(
                [trace.dict() for trace in traces],
                indent=2,
                default=str
            )
        elif format.lower() == "csv":
            # Simple CSV export
            if not traces:
                return ""
            
            # Get all possible fields
            fields = set()
            for trace in traces:
                fields.update(trace.dict().keys())
            
            fields = sorted(list(fields))
            
            # Create CSV
            lines = [",".join(fields)]
            for trace in traces:
                trace_dict = trace.dict()
                row = [str(trace_dict.get(field, "")) for field in fields]
                lines.append(",".join(row))
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_observability_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive observability summary.
        
        Returns:
            Observability summary
        """
        return {
            "traces": {
                "total_count": len(self._traces),
                "recent_count": len(self.get_recent_traces(24)),
                "retention_days": self.config.trace_retention_days,
            },
            "metrics": {
                "metric_count": len(self._metrics),
                "total_entries": sum(len(entries) for entries in self._metrics.values()),
            },
            "performance": self.get_performance_summary(),
            "drift_alerts": {
                "total_count": len(self._drift_alerts),
                "recent_count": len(self.get_drift_alerts(24)),
            },
            "style_evolution": self.get_style_evolution_summary(24),
        }
    
    def _cleanup_old_traces(self) -> None:
        """Remove traces older than the retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.config.trace_retention_days)
        self._traces = [
            trace for trace in self._traces
            if trace.ts > cutoff
        ]
    
    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than 7 days."""
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        for metric_name in list(self._metrics.keys()):
            self._metrics[metric_name] = [
                entry for entry in self._metrics[metric_name]
                if entry["timestamp"] > cutoff
            ]
            
            # Remove empty metric lists
            if not self._metrics[metric_name]:
                del self._metrics[metric_name]
    
    def _check_for_drift(self, trace: StyleTrace) -> None:
        """Check for personality drift in the trace."""
        if not trace.style_delta:
            return
        
        # Calculate total drift magnitude
        drift_magnitude = 0.0
        for delta_str in trace.style_delta.values():
            try:
                if delta_str.startswith("+"):
                    drift_magnitude += float(delta_str[1:])
                elif delta_str.startswith("-"):
                    drift_magnitude += abs(float(delta_str[1:]))
                else:
                    drift_magnitude += abs(float(delta_str))
            except ValueError:
                continue
        
        # Check if drift exceeds threshold
        if drift_magnitude > self.config.drift_threshold:
            alert = {
                "id": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "trace_id": str(trace.id),
                "drift_magnitude": drift_magnitude,
                "threshold": self.config.drift_threshold,
                "style_delta": trace.style_delta,
                "rationale": trace.rationale,
                "severity": "high" if drift_magnitude > self.config.drift_threshold * 2 else "medium",
            }
            
            self._drift_alerts.append(alert)
            
            logger.warning(
                "Personality drift detected: magnitude=%.3f, threshold=%.3f",
                drift_magnitude, self.config.drift_threshold
            )
    
    def clear_all_data(self) -> None:
        """Clear all stored data (for testing/debugging)."""
        self._traces.clear()
        self._metrics.clear()
        self._drift_alerts.clear()
        
        for operation in self._performance_metrics:
            self._performance_metrics[operation].clear()
        
        logger.info("All observability data cleared")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the observability system.
        
        Returns:
            Health status information
        """
        # Check trace storage
        trace_health = {
            "status": "healthy",
            "message": "Trace storage is functioning normally",
        }
        
        if len(self._traces) > 10000:  # Arbitrary limit
            trace_health["status"] = "warning"
            trace_health["message"] = "Large number of traces stored"
        
        # Check performance metrics
        performance_health = {
            "status": "healthy",
            "message": "Performance monitoring is functioning normally",
        }
        
        for operation, entries in self._performance_metrics.items():
            if entries:
                avg_duration = sum(entry["duration"] for entry in entries) / len(entries)
                if avg_duration > 1.0:  # More than 1 second average
                    performance_health["status"] = "warning"
                    performance_health["message"] = f"Slow performance detected in {operation}"
                    break
        
        # Check drift alerts
        drift_health = {
            "status": "healthy",
            "message": "No significant drift detected",
        }
        
        recent_alerts = self.get_drift_alerts(24)
        if len(recent_alerts) > 5:
            drift_health["status"] = "warning"
            drift_health["message"] = f"Multiple drift alerts in last 24 hours: {len(recent_alerts)}"
        
        high_severity_alerts = [alert for alert in recent_alerts if alert["severity"] == "high"]
        if high_severity_alerts:
            drift_health["status"] = "critical"
            drift_health["message"] = f"High severity drift alerts detected: {len(high_severity_alerts)}"
        
        return {
            "overall_status": "healthy" if all(
                h["status"] == "healthy" for h in [trace_health, performance_health, drift_health]
            ) else "warning",
            "components": {
                "trace_storage": trace_health,
                "performance_monitoring": performance_health,
                "drift_detection": drift_health,
            },
            "timestamp": datetime.utcnow(),
        }