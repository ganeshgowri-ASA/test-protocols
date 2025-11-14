"""
Protocol Analytics Module - Performance metrics and trend analysis
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from models.protocol import Protocol, ProtocolStatus, QCResult, ProtocolType
from utils.helpers import calculate_percentage, filter_by_date_range


class ProtocolAnalytics:
    """Analyze protocol performance and trends"""

    def __init__(self, protocols: List[Protocol]):
        self.protocols = protocols

    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall protocol statistics"""
        total = len(self.protocols)
        if total == 0:
            return self._empty_stats()

        completed = sum(1 for p in self.protocols if p.status == ProtocolStatus.COMPLETED)
        in_progress = sum(1 for p in self.protocols if p.status == ProtocolStatus.IN_PROGRESS)
        pending = sum(1 for p in self.protocols if p.status == ProtocolStatus.PENDING)
        failed = sum(1 for p in self.protocols if p.status == ProtocolStatus.FAILED)

        passed = sum(1 for p in self.protocols if p.qc_result == QCResult.PASS)
        qc_failed = sum(1 for p in self.protocols if p.qc_result == QCResult.FAIL)

        durations = [p.duration_hours for p in self.protocols if p.duration_hours is not None]
        avg_duration = statistics.mean(durations) if durations else 0

        return {
            'total_protocols': total,
            'completed': completed,
            'in_progress': in_progress,
            'pending': pending,
            'failed': failed,
            'completion_rate': calculate_percentage(completed, total),
            'pass_rate': calculate_percentage(passed, completed) if completed > 0 else 0,
            'fail_rate': calculate_percentage(qc_failed, completed) if completed > 0 else 0,
            'average_duration_hours': round(avg_duration, 2),
            'total_test_hours': round(sum(durations), 2) if durations else 0
        }

    def get_protocol_type_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by protocol type"""
        type_stats = defaultdict(lambda: {
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'pending': 0,
            'failed': 0,
            'passed': 0,
            'qc_failed': 0,
            'durations': []
        })

        for protocol in self.protocols:
            ptype = protocol.protocol_type.value
            type_stats[ptype]['total'] += 1

            if protocol.status == ProtocolStatus.COMPLETED:
                type_stats[ptype]['completed'] += 1
            elif protocol.status == ProtocolStatus.IN_PROGRESS:
                type_stats[ptype]['in_progress'] += 1
            elif protocol.status == ProtocolStatus.PENDING:
                type_stats[ptype]['pending'] += 1
            elif protocol.status == ProtocolStatus.FAILED:
                type_stats[ptype]['failed'] += 1

            if protocol.qc_result == QCResult.PASS:
                type_stats[ptype]['passed'] += 1
            elif protocol.qc_result == QCResult.FAIL:
                type_stats[ptype]['qc_failed'] += 1

            if protocol.duration_hours:
                type_stats[ptype]['durations'].append(protocol.duration_hours)

        # Calculate derived metrics
        result = {}
        for ptype, stats in type_stats.items():
            completed = stats['completed']
            result[ptype] = {
                'total': stats['total'],
                'completed': completed,
                'in_progress': stats['in_progress'],
                'pending': stats['pending'],
                'failed': stats['failed'],
                'completion_rate': calculate_percentage(completed, stats['total']),
                'pass_rate': calculate_percentage(stats['passed'], completed) if completed > 0 else 0,
                'average_duration': round(statistics.mean(stats['durations']), 2) if stats['durations'] else 0
            }

        return dict(result)

    def get_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Filter protocols by date
        time_filtered = [
            p for p in self.protocols
            if p.start_time and start_date <= p.start_time <= end_date
        ]

        if not time_filtered:
            return {'error': 'No data available for the specified time period'}

        # Group by day
        daily_stats = defaultdict(lambda: {
            'completed': 0,
            'failed': 0,
            'passed': 0,
            'qc_failed': 0,
            'total': 0
        })

        for protocol in time_filtered:
            day = protocol.start_time.date()
            daily_stats[day]['total'] += 1

            if protocol.status == ProtocolStatus.COMPLETED:
                daily_stats[day]['completed'] += 1

            if protocol.qc_result == QCResult.PASS:
                daily_stats[day]['passed'] += 1
            elif protocol.qc_result == QCResult.FAIL:
                daily_stats[day]['qc_failed'] += 1

        # Calculate trends
        dates = sorted(daily_stats.keys())
        completion_rates = []
        pass_rates = []

        for date in dates:
            stats = daily_stats[date]
            if stats['total'] > 0:
                completion_rates.append(calculate_percentage(stats['completed'], stats['total']))
            if stats['completed'] > 0:
                pass_rates.append(calculate_percentage(stats['passed'], stats['completed']))

        return {
            'period_days': days,
            'total_protocols': len(time_filtered),
            'average_completion_rate': round(statistics.mean(completion_rates), 2) if completion_rates else 0,
            'average_pass_rate': round(statistics.mean(pass_rates), 2) if pass_rates else 0,
            'daily_data': {str(k): v for k, v in daily_stats.items()}
        }

    def get_failure_mode_analysis(self) -> Dict[str, Any]:
        """Analyze failure patterns"""
        failed_protocols = [p for p in self.protocols if p.qc_result == QCResult.FAIL]

        if not failed_protocols:
            return {'total_failures': 0, 'failure_rate': 0, 'by_type': {}}

        # Group failures by type
        failure_by_type = defaultdict(int)
        for protocol in failed_protocols:
            failure_by_type[protocol.protocol_type.value] += 1

        # Calculate failure rates by type
        type_failure_rates = {}
        for ptype in failure_by_type.keys():
            type_total = sum(1 for p in self.protocols if p.protocol_type.value == ptype)
            type_failure_rates[ptype] = {
                'failures': failure_by_type[ptype],
                'total': type_total,
                'failure_rate': calculate_percentage(failure_by_type[ptype], type_total)
            }

        total_completed = sum(1 for p in self.protocols if p.status == ProtocolStatus.COMPLETED)

        return {
            'total_failures': len(failed_protocols),
            'overall_failure_rate': calculate_percentage(len(failed_protocols), total_completed) if total_completed > 0 else 0,
            'by_type': type_failure_rates,
            'top_failure_types': sorted(
                type_failure_rates.items(),
                key=lambda x: x[1]['failure_rate'],
                reverse=True
            )[:5]
        }

    def get_performance_indicators(self) -> Dict[str, Any]:
        """Calculate statistical process control indicators"""
        durations = [p.duration_hours for p in self.protocols if p.duration_hours is not None]

        if not durations:
            return {'error': 'No duration data available'}

        mean_duration = statistics.mean(durations)
        stdev_duration = statistics.stdev(durations) if len(durations) > 1 else 0

        # Control limits (3-sigma)
        ucl = mean_duration + (3 * stdev_duration)
        lcl = max(0, mean_duration - (3 * stdev_duration))

        # Identify outliers
        outliers = [d for d in durations if d > ucl or d < lcl]

        # Calculate capability metrics
        durations_sorted = sorted(durations)
        p95 = durations_sorted[int(len(durations_sorted) * 0.95)] if durations_sorted else 0

        return {
            'mean_duration': round(mean_duration, 2),
            'std_deviation': round(stdev_duration, 2),
            'median_duration': round(statistics.median(durations), 2),
            'min_duration': round(min(durations), 2),
            'max_duration': round(max(durations), 2),
            'p95_duration': round(p95, 2),
            'upper_control_limit': round(ucl, 2),
            'lower_control_limit': round(lcl, 2),
            'outlier_count': len(outliers),
            'outlier_rate': calculate_percentage(len(outliers), len(durations))
        }

    def get_comparative_analysis(self) -> List[Dict[str, Any]]:
        """Compare protocols across multiple dimensions"""
        type_comparison = []

        for ptype in ProtocolType:
            type_protocols = [p for p in self.protocols if p.protocol_type == ptype]

            if not type_protocols:
                continue

            completed = sum(1 for p in type_protocols if p.status == ProtocolStatus.COMPLETED)
            passed = sum(1 for p in type_protocols if p.qc_result == QCResult.PASS)
            durations = [p.duration_hours for p in type_protocols if p.duration_hours is not None]

            type_comparison.append({
                'protocol_type': ptype.value,
                'total_count': len(type_protocols),
                'completed_count': completed,
                'completion_rate': calculate_percentage(completed, len(type_protocols)),
                'pass_rate': calculate_percentage(passed, completed) if completed > 0 else 0,
                'average_duration': round(statistics.mean(durations), 2) if durations else 0,
                'median_duration': round(statistics.median(durations), 2) if durations else 0
            })

        # Sort by completion rate
        type_comparison.sort(key=lambda x: x['completion_rate'], reverse=True)

        return type_comparison

    def get_predictive_maintenance_indicators(self) -> Dict[str, Any]:
        """Identify protocols that may need attention"""
        # Find protocols with increasing failure rates
        recent_protocols = [
            p for p in self.protocols
            if p.start_time and p.start_time > datetime.now() - timedelta(days=30)
        ]

        older_protocols = [
            p for p in self.protocols
            if p.start_time and p.start_time <= datetime.now() - timedelta(days=30)
        ]

        recent_fail_rate = calculate_percentage(
            sum(1 for p in recent_protocols if p.qc_result == QCResult.FAIL),
            len(recent_protocols)
        ) if recent_protocols else 0

        older_fail_rate = calculate_percentage(
            sum(1 for p in older_protocols if p.qc_result == QCResult.FAIL),
            len(older_protocols)
        ) if older_protocols else 0

        # Identify slow protocols
        slow_protocols = [
            p for p in self.protocols
            if p.duration_hours and p.duration_hours > 48
        ]

        # Identify overdue protocols
        overdue_protocols = [p for p in self.protocols if p.is_overdue]

        return {
            'recent_failure_rate': round(recent_fail_rate, 2),
            'historical_failure_rate': round(older_fail_rate, 2),
            'failure_rate_trend': 'increasing' if recent_fail_rate > older_fail_rate else 'decreasing',
            'slow_protocol_count': len(slow_protocols),
            'overdue_protocol_count': len(overdue_protocols),
            'attention_required': recent_fail_rate > older_fail_rate or len(overdue_protocols) > 0
        }

    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics"""
        return {
            'total_protocols': 0,
            'completed': 0,
            'in_progress': 0,
            'pending': 0,
            'failed': 0,
            'completion_rate': 0,
            'pass_rate': 0,
            'fail_rate': 0,
            'average_duration_hours': 0,
            'total_test_hours': 0
        }
