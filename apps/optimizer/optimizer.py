import statistics
from typing import List, Dict

class PipelineOptimizer:
    def __init__(self, runs: List[Dict]):
        """
        :param runs: List of CI/CD run results
                     Example: [{ "duration": 300, "status": "success", "job": "tests" }, ...]
        """
        self.runs = runs

    def suggest_parallelization(self) -> List[str]:
        """
        Suggest jobs that consistently take too long and could be split into parallel jobs.
        """
        job_durations = {}
        for run in self.runs:
            job = run.get("job", "unknown")
            job_durations.setdefault(job, []).append(run["duration"])

        suggestions = []
        for job, durations in job_durations.items():
            avg_duration = statistics.mean(durations)
            if avg_duration > 120:  # Arbitrary threshold: jobs > 2 min are considered "too long"
                suggestions.append(f"Job '{job}' averages {avg_duration:.1f}s — consider splitting into parallel jobs.")
        return suggestions

    def detect_caching_opportunities(self) -> List[str]:
        """
        Detect jobs that often repeat with similar durations (likely due to rebuilding deps).
        """
        suggestions = []
        for job in set(run["job"] for run in self.runs):
            durations = [r["duration"] for r in self.runs if r["job"] == job]
            if len(set(durations)) > 1 and max(durations) / min(durations) > 1.5:
                suggestions.append(f"Job '{job}' shows large runtime variance — caching dependencies may help.")
        return suggestions

    def estimate_savings(self) -> str:
        """
        Roughly estimate potential build time savings from optimizations.
        """
        total_time = sum(run["duration"] for run in self.runs)
        savings = total_time * 0.20  # Assume 20% savings as baseline
        return f"Estimated potential savings: {savings:.1f}s across all builds."

    def generate_report(self) -> Dict:
        """
        Generate a full optimization report.
        """
        return {
            "parallelization": self.suggest_parallelization(),
            "caching": self.detect_caching_opportunities(),
            "savings": self.estimate_savings()
        }


if __name__ == "__main__":
    sample_runs = [
        {"duration": 300, "status": "success", "job": "tests"},
        {"duration": 320, "status": "failed", "job": "tests"},
        {"duration": 100, "status": "success", "job": "lint"},
        {"duration": 250, "status": "success", "job": "build"},
        {"duration": 450, "status": "success", "job": "tests"},
    ]

    optimizer = PipelineOptimizer(sample_runs)
    report = optimizer.generate_report()
    print("\n--- CI/CD Optimization Report ---")
    for category, items in report.items():
        if isinstance(items, list):
            for i in items:
                print(f"[{category.upper()}] {i}")
        else:
            print(f"[{category.upper()}] {items}")
