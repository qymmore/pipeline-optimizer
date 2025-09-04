import pandas as pd
import numpy as np

class Analyzer:
    def __init__(self, threshold_factor: float = 1.5):
        """
        Analyzer detects "bad" CI/CD runs based on duration anomalies.
        Args:
            threshold_factor: factor to determine anomaly cutoff (default 1.5 IQR).
        """
        self.threshold_factor = threshold_factor
        self.lower_bound = None
        self.upper_bound = None

    def fit(self, durations: list[float]):
        """
        Fit thresholds using Interquartile Range (IQR) method.
        """
        q1 = np.percentile(durations, 25)
        q3 = np.percentile(durations, 75)
        iqr = q3 - q1

        self.lower_bound = q1 - self.threshold_factor * iqr
        self.upper_bound = q3 + self.threshold_factor * iqr

    def classify(self, duration: float) -> str:
        """
        Classify a run as 'good' or 'bad' based on fitted thresholds.
        """
        if self.lower_bound is None or self.upper_bound is None:
            raise ValueError("Analyzer not fitted. Call `fit()` first.")

        if duration < self.lower_bound or duration > self.upper_bound:
            return "bad"
        return "good"


if __name__ == "__main__":
    # Demo: Fake CI/CD run durations
    sample_durations = [320, 300, 310, 305, 900, 290, 315, 305, 1500, 310]

    analyzer = Analyzer()
    analyzer.fit(sample_durations)

    print("Fitted thresholds:", analyzer.lower_bound, analyzer.upper_bound)

    for d in sample_durations:
        print(f"Run {d} sec -> {analyzer.classify(d)}")
