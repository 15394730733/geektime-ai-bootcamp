"""
Performance monitoring for database operations.

This module provides performance tracking and metrics collection for
database queries and connection pool usage.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import logging

from app.core.connection_pool import connection_pool_manager

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""

    query: str
    database: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    row_count: int = 0
    success: bool = True
    error_message: Optional[str] = None
    query_type: str = "UNKNOWN"  # SELECT, INSERT, UPDATE, DELETE, etc.

    def complete(self, success: bool, row_count: int, error_message: Optional[str] = None):
        """Mark the query as complete."""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.success = success
        self.row_count = row_count
        self.error_message = error_message


@dataclass
class PerformanceStats:
    """Performance statistics for a time window."""

    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_duration_ms: float = 0
    avg_duration_ms: float = 0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0
    queries_by_type: Dict[str, int] = field(default_factory=dict)
    slow_queries: List[Dict[str, Any]] = field(default_factory=list)

    def add_query(self, metrics: QueryMetrics):
        """Add query metrics to statistics."""
        self.total_queries += 1

        if metrics.success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1

        if metrics.duration_ms is not None:
            self.total_duration_ms += metrics.duration_ms
            self.avg_duration_ms = self.total_duration_ms / self.total_queries
            self.min_duration_ms = min(self.min_duration_ms, metrics.duration_ms)
            self.max_duration_ms = max(self.max_duration_ms, metrics.duration_ms)

            # Track slow queries (> 1 second)
            if metrics.duration_ms > 1000:
                self.slow_queries.append({
                    "query": metrics.query[:200],  # Truncate long queries
                    "database": metrics.database,
                    "duration_ms": metrics.duration_ms,
                    "timestamp": metrics.start_time.isoformat()
                })
                # Keep only the last 100 slow queries
                if len(self.slow_queries) > 100:
                    self.slow_queries.pop(0)

        # Track queries by type
        self.queries_by_type[metrics.query_type] = \
            self.queries_by_type.get(metrics.query_type, 0) + 1


class PerformanceMonitor:
    """Monitor and track database performance metrics."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.

        Args:
            max_history: Maximum number of query metrics to keep in history
        """
        self.max_history = max_history
        self.query_history: deque = deque(maxlen=max_history)
        self.active_queries: Dict[str, QueryMetrics] = {}
        self.stats = PerformanceStats()
        self.start_time = datetime.now()

    def start_query(self, query_id: str, query: str, database: str) -> QueryMetrics:
        """
        Start tracking a query execution.

        Args:
            query_id: Unique identifier for the query
            query: SQL query string
            database: Database name

        Returns:
            QueryMetrics object for tracking
        """
        # Determine query type
        query_type = self._get_query_type(query)

        metrics = QueryMetrics(
            query=query,
            database=database,
            start_time=datetime.now(),
            query_type=query_type
        )

        self.active_queries[query_id] = metrics
        return metrics

    def end_query(
        self,
        query_id: str,
        success: bool,
        row_count: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[QueryMetrics]:
        """
        End tracking a query execution.

        Args:
            query_id: Unique identifier for the query
            success: Whether the query succeeded
            row_count: Number of rows affected/returned
            error_message: Error message if query failed

        Returns:
            Completed QueryMetrics object, or None if query_id not found
        """
        if query_id not in self.active_queries:
            return None

        metrics = self.active_queries.pop(query_id)
        metrics.complete(success, row_count, error_message)

        self.query_history.append(metrics)
        self.stats.add_query(metrics)

        # Log slow queries
        if metrics.duration_ms and metrics.duration_ms > 1000:
            logger.warning(
                f"Slow query detected: {metrics.query[:100]}... "
                f"took {metrics.duration_ms:.2f}ms on database {metrics.database}"
            )

        return metrics

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "uptime_seconds": uptime,
            "total_queries": self.stats.total_queries,
            "successful_queries": self.stats.successful_queries,
            "failed_queries": self.stats.failed_queries,
            "success_rate": (
                self.stats.successful_queries / self.stats.total_queries
                if self.stats.total_queries > 0 else 0
            ),
            "avg_duration_ms": round(self.stats.avg_duration_ms, 2),
            "min_duration_ms": (
                round(self.stats.min_duration_ms, 2)
                if self.stats.min_duration_ms != float('inf') else 0
            ),
            "max_duration_ms": round(self.stats.max_duration_ms, 2),
            "queries_per_second": round(self.stats.total_queries / uptime, 2) if uptime > 0 else 0,
            "queries_by_type": self.stats.queries_by_type,
            "slow_queries_count": len(self.stats.slow_queries),
            "active_queries": len(self.active_queries)
        }

    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries.

        Args:
            limit: Maximum number of slow queries to return

        Returns:
            List of slow query details
        """
        return self.stats.slow_queries[-limit:]

    async def get_connection_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status.

        Returns:
            Dictionary with pool status information
        """
        return await connection_pool_manager.get_pool_status()

    def _get_query_type(self, query: str) -> str:
        """
        Determine the type of SQL query.

        Args:
            query: SQL query string

        Returns:
            Query type (SELECT, INSERT, UPDATE, DELETE, etc.)
        """
        query_upper = query.strip().upper()

        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif query_upper.startswith('CREATE'):
            return 'CREATE'
        elif query_upper.startswith('DROP'):
            return 'DROP'
        elif query_upper.startswith('ALTER'):
            return 'ALTER'
        elif query_upper.startswith('WITH'):
            return 'WITH'  # CTE
        else:
            return 'UNKNOWN'

    def reset_stats(self):
        """Reset performance statistics."""
        self.stats = PerformanceStats()
        self.query_history.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_query_id() -> str:
    """
    Generate a unique query ID.

    Returns:
        Unique query identifier
    """
    return f"query_{int(time.time() * 1000000)}"
