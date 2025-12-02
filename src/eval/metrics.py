"""Metrics calculator for NCI evaluation framework."""

from typing import Dict, List, Tuple, Any
import numpy as np
from dataclasses import dataclass, asdict
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    roc_curve,
    auc,
)


@dataclass
class ClassificationMetrics:
    """Container for classification metrics."""
    precision: float
    recall: float
    f1: float
    accuracy: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    threshold: float


@dataclass
class CalibrationMetrics:
    """Container for calibration metrics."""
    brier_score: float
    expected_calibration_error: float
    max_calibration_error: float


@dataclass
class CriterionMetrics:
    """Container for per-criterion metrics."""
    criterion: str
    precision: float
    recall: float
    f1: float
    support: int


class MetricsCalculator:
    """Calculate evaluation metrics for NCI scoring."""

    @staticmethod
    def binary_classification_metrics(
        predicted_scores: List[int],
        ground_truth_labels: List[str],
        threshold: int = 6,
    ) -> ClassificationMetrics:
        """
        Calculate binary classification metrics.

        Args:
            predicted_scores: NCI scores (0-20)
            ground_truth_labels: Ground truth labels ('manipulative' or 'credible')
            threshold: Score threshold for classification (score >= threshold -> manipulative)

        Returns:
            ClassificationMetrics object
        """
        # Convert labels to binary (1 = manipulative, 0 = credible)
        binary_labels = [1 if label == "manipulative" else 0 for label in ground_truth_labels]
        binary_predictions = [1 if score >= threshold else 0 for score in predicted_scores]

        # Calculate confusion matrix
        tn, fp, fn, tp = confusion_matrix(binary_labels, binary_predictions).ravel()

        # Calculate metrics
        precision = precision_score(binary_labels, binary_predictions, zero_division=0)
        recall = recall_score(binary_labels, binary_predictions, zero_division=0)
        f1 = f1_score(binary_labels, binary_predictions, zero_division=0)
        accuracy = accuracy_score(binary_labels, binary_predictions)

        return ClassificationMetrics(
            precision=float(precision),
            recall=float(recall),
            f1=float(f1),
            accuracy=float(accuracy),
            true_positives=int(tp),
            true_negatives=int(tn),
            false_positives=int(fp),
            false_negatives=int(fn),
            threshold=threshold,
        )

    @staticmethod
    def calibration_metrics(
        predicted_scores: List[int],
        ground_truth_labels: List[str],
        num_bins: int = 5,
    ) -> Tuple[CalibrationMetrics, Dict[str, Any]]:
        """
        Calculate calibration metrics.

        Args:
            predicted_scores: NCI scores (0-20), normalized to 0-1 for calibration
            ground_truth_labels: Ground truth labels ('manipulative' or 'credible')
            num_bins: Number of bins for calibration

        Returns:
            Tuple of (CalibrationMetrics, calibration_data dict)
        """
        # Convert to binary labels and normalize scores
        binary_labels = np.array([1 if label == "manipulative" else 0 for label in ground_truth_labels])
        normalized_scores = np.array([score / 20.0 for score in predicted_scores])

        # Brier score
        brier = float(np.mean((normalized_scores - binary_labels) ** 2))

        # Expected Calibration Error (ECE)
        ece, bin_data = MetricsCalculator._calculate_ece(normalized_scores, binary_labels, num_bins)

        # Max calibration error
        mce = float(np.max([abs(b["expected"] - b["actual"]) for b in bin_data]))

        return CalibrationMetrics(
            brier_score=brier,
            expected_calibration_error=ece,
            max_calibration_error=mce,
        ), {
            "bin_data": bin_data,
            "normalized_scores": normalized_scores.tolist(),
            "binary_labels": binary_labels.tolist(),
        }

    @staticmethod
    def _calculate_ece(
        predicted_probs: np.ndarray,
        true_labels: np.ndarray,
        num_bins: int = 5,
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate Expected Calibration Error.

        Args:
            predicted_probs: Predicted probabilities (0-1)
            true_labels: Ground truth labels (0 or 1)
            num_bins: Number of bins

        Returns:
            Tuple of (ECE value, bin data)
        """
        bin_boundaries = np.linspace(0, 1, num_bins + 1)
        bin_data = []
        total_samples = len(predicted_probs)
        ece = 0.0

        for i in range(num_bins):
            mask = (predicted_probs >= bin_boundaries[i]) & (predicted_probs < bin_boundaries[i + 1])
            if np.sum(mask) == 0:
                continue

            bin_size = np.sum(mask)
            bin_accuracy = np.mean(true_labels[mask])
            bin_confidence = np.mean(predicted_probs[mask])
            bin_weight = bin_size / total_samples

            ece += bin_weight * abs(bin_confidence - bin_accuracy)
            bin_data.append({
                "bin": f"{bin_boundaries[i]:.2f}-{bin_boundaries[i + 1]:.2f}",
                "confidence": float(bin_confidence),
                "actual": float(bin_accuracy),
                "expected": float(bin_confidence),
                "samples": int(bin_size),
            })

        return ece, bin_data

    @staticmethod
    def per_criterion_metrics(
        criteria_results: List[Dict[str, Any]],
        ground_truth_labels: List[str],
    ) -> List[CriterionMetrics]:
        """
        Calculate per-criterion metrics.

        Args:
            criteria_results: List of criterion scoring results
            ground_truth_labels: Ground truth labels

        Returns:
            List of CriterionMetrics
        """
        criterion_metrics = []
        binary_labels = np.array([1 if label == "manipulative" else 0 for label in ground_truth_labels])

        # Collect all criterion names
        all_criteria = set()
        for result in criteria_results:
            if isinstance(result, dict) and "criteria_scores" in result:
                all_criteria.update(result["criteria_scores"].keys())

        for criterion in sorted(all_criteria):
            # Extract binary predictions for this criterion
            predictions = []
            for result in criteria_results:
                if isinstance(result, dict) and "criteria_scores" in result:
                    criterion_data = result["criteria_scores"].get(criterion, {})
                    predictions.append(1 if criterion_data.get("matched", False) else 0)
                else:
                    predictions.append(0)

            predictions = np.array(predictions)

            # Calculate metrics
            if np.sum(predictions) == 0 or np.sum(binary_labels) == 0:
                support = np.sum(binary_labels)
                criterion_metrics.append(
                    CriterionMetrics(
                        criterion=criterion,
                        precision=0.0,
                        recall=0.0,
                        f1=0.0,
                        support=int(support),
                    )
                )
            else:
                precision = precision_score(binary_labels, predictions, zero_division=0)
                recall = recall_score(binary_labels, predictions, zero_division=0)
                f1 = f1_score(binary_labels, predictions, zero_division=0)
                support = np.sum(binary_labels)

                criterion_metrics.append(
                    CriterionMetrics(
                        criterion=criterion,
                        precision=float(precision),
                        recall=float(recall),
                        f1=float(f1),
                        support=int(support),
                    )
                )

        return criterion_metrics

    @staticmethod
    def score_distribution_analysis(
        predicted_scores: List[int],
        ground_truth_labels: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze score distributions.

        Args:
            predicted_scores: NCI scores
            ground_truth_labels: Ground truth labels

        Returns:
            Dictionary with distribution statistics
        """
        manipulative_scores = [
            s for s, label in zip(predicted_scores, ground_truth_labels)
            if label == "manipulative"
        ]
        credible_scores = [
            s for s, label in zip(predicted_scores, ground_truth_labels)
            if label == "credible"
        ]

        def stats(scores):
            if not scores:
                return {
                    "mean": None,
                    "median": None,
                    "std": None,
                    "min": None,
                    "max": None,
                    "count": 0,
                }
            arr = np.array(scores)
            return {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr)),
                "min": int(np.min(arr)),
                "max": int(np.max(arr)),
                "count": len(scores),
            }

        return {
            "manipulative": stats(manipulative_scores),
            "credible": stats(credible_scores),
            "overall": stats(predicted_scores),
        }

    @staticmethod
    def risk_level_analysis(
        predicted_scores: List[int],
        ground_truth_labels: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze risk level predictions vs ground truth.

        Args:
            predicted_scores: NCI scores
            ground_truth_labels: Ground truth labels

        Returns:
            Dictionary with risk level analysis
        """
        risk_levels = []
        for score in predicted_scores:
            if score <= 5:
                risk_levels.append("LOW")
            elif score <= 10:
                risk_levels.append("MODERATE")
            elif score <= 15:
                risk_levels.append("HIGH")
            else:
                risk_levels.append("CRITICAL")

        # Cross-tabulation
        cross_tab = {}
        for pred_level, truth_label in zip(risk_levels, ground_truth_labels):
            key = f"{pred_level}_vs_{truth_label}"
            cross_tab[key] = cross_tab.get(key, 0) + 1

        return {
            "risk_levels": risk_levels,
            "cross_tabulation": cross_tab,
        }

    @staticmethod
    def metrics_to_dict(metrics_obj: Any) -> Dict[str, Any]:
        """Convert metrics dataclass to dictionary."""
        if hasattr(metrics_obj, "__dataclass_fields__"):
            return asdict(metrics_obj)
        return vars(metrics_obj)

