"""Advanced metrics for deeper NCI evaluation analysis."""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
from sklearn.metrics import roc_curve, auc, roc_auc_score
import json


@dataclass
class CriterionPerformance:
    """Performance metrics for a single NCI criterion."""
    criterion: str
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    support: int  # Total manipulative examples
    prevalence: float  # How often this criterion appears


@dataclass
class ThresholdAnalysis:
    """Analysis results for a specific threshold."""
    threshold: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    fpr: float  # False positive rate
    tpr: float  # True positive rate (recall)


@dataclass
class TemporalStabilityResult:
    """Results from temporal stability testing."""
    source_id: str
    mean_score: float
    std_dev: float
    coefficient_of_variation: float
    min_score: int
    max_score: int
    num_runs: int
    is_stable: bool  # True if CV < threshold


class AdvancedMetricsCalculator:
    """Calculate advanced metrics for deeper NCI evaluation."""

    def __init__(self):
        self.nci_criteria = [
            "timing", "emotional_manipulation", "uniform_messaging",
            "missing_information", "simplistic_narratives", "tribal_division",
            "authority_overload", "call_for_urgent_action", "overuse_of_novelty",
            "financial_political_gain", "suppression_of_dissent", "false_dilemmas",
            "bandwagon_effect", "emotional_repetition", "cherry_picked_data",
            "logical_fallacies", "manufactured_outrage", "framing_techniques",
            "rapid_behavior_shifts", "historical_parallels"
        ]

    def criterion_level_metrics(
        self,
        scoring_results: List[Dict[str, Any]],
        ground_truth_labels: List[str]
    ) -> List[CriterionPerformance]:
        """
        Calculate precision, recall, F1 for each individual criterion.

        Args:
            scoring_results: NCI scoring results for each source
            ground_truth_labels: Ground truth labels (manipulative/credible)

        Returns:
            List of criterion performance metrics
        """
        criterion_metrics = []

        for criterion in self.nci_criteria:
            tp = fp = fn = tn = 0

            for i, result in enumerate(scoring_results):
                if "error" in result or "nci_result" not in result:
                    continue

                ground_truth = ground_truth_labels[i]
                criteria_scores = result["nci_result"].get("criteria_scores", {})

                # Check if this criterion matched
                criterion_matched = criteria_scores.get(criterion, {}).get("matched", False)

                # Ground truth: manipulative sources SHOULD match criteria
                if ground_truth == "manipulative":
                    if criterion_matched:
                        tp += 1  # Correctly identified manipulation indicator
                    else:
                        fn += 1  # Missed manipulation indicator
                else:  # credible
                    if criterion_matched:
                        fp += 1  # Incorrectly flagged credible source
                    else:
                        tn += 1  # Correctly did not flag

            # Calculate metrics
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            support = tp + fn  # Total manipulative examples
            total = tp + fp + fn + tn
            prevalence = (tp + fp) / total if total > 0 else 0.0

            criterion_metrics.append(CriterionPerformance(
                criterion=criterion,
                precision=precision,
                recall=recall,
                f1_score=f1,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                true_negatives=tn,
                support=support,
                prevalence=prevalence
            ))

        # Sort by F1 score descending
        return sorted(criterion_metrics, key=lambda x: x.f1_score, reverse=True)

    def threshold_optimization_analysis(
        self,
        predicted_scores: List[int],
        ground_truth_labels: List[str],
        threshold_range: Optional[Tuple[int, int]] = None
    ) -> Tuple[List[ThresholdAnalysis], Dict[str, Any]]:
        """
        Comprehensive threshold analysis with ROC curve.

        Args:
            predicted_scores: NCI aggregate scores
            ground_truth_labels: Ground truth labels
            threshold_range: (min, max) thresholds to test, default (0, 20)

        Returns:
            Tuple of (threshold_analyses, roc_data)
        """
        if threshold_range is None:
            threshold_range = (0, 21)

        # Convert labels to binary
        y_true = np.array([1 if label == "manipulative" else 0 for label in ground_truth_labels])
        y_scores = np.array(predicted_scores)

        threshold_analyses = []

        for threshold in range(threshold_range[0], threshold_range[1]):
            # Make predictions at this threshold
            y_pred = (y_scores >= threshold).astype(int)

            # Calculate confusion matrix
            tp = np.sum((y_pred == 1) & (y_true == 1))
            fp = np.sum((y_pred == 1) & (y_true == 0))
            fn = np.sum((y_pred == 0) & (y_true == 1))
            tn = np.sum((y_pred == 0) & (y_true == 0))

            # Calculate metrics
            accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # TPR
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            threshold_analyses.append(ThresholdAnalysis(
                threshold=threshold,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                true_positives=int(tp),
                false_positives=int(fp),
                false_negatives=int(fn),
                true_negatives=int(tn),
                fpr=fpr,
                tpr=recall
            ))

        # ROC curve analysis
        try:
            # For ROC, we want continuous scores, not thresholded
            fpr_curve, tpr_curve, thresholds_curve = roc_curve(y_true, y_scores)
            roc_auc = auc(fpr_curve, tpr_curve)

            roc_data = {
                "fpr": fpr_curve.tolist(),
                "tpr": tpr_curve.tolist(),
                "thresholds": thresholds_curve.tolist(),
                "auc": float(roc_auc)
            }
        except Exception as e:
            roc_data = {"error": str(e)}

        return threshold_analyses, roc_data

    def find_optimal_threshold(
        self,
        threshold_analyses: List[ThresholdAnalysis],
        optimization_target: str = "f1",
        fn_cost: float = 1.0,
        fp_cost: float = 1.0
    ) -> Tuple[int, ThresholdAnalysis]:
        """
        Find optimal threshold based on specified criteria.

        Args:
            threshold_analyses: List of threshold analyses
            optimization_target: "f1", "accuracy", "youden", or "cost"
            fn_cost: Cost of false negative (missing manipulation)
            fp_cost: Cost of false positive (flagging credible source)

        Returns:
            Tuple of (optimal_threshold, analysis)
        """
        if optimization_target == "f1":
            # Maximize F1 score
            best = max(threshold_analyses, key=lambda x: x.f1_score)

        elif optimization_target == "accuracy":
            # Maximize accuracy
            best = max(threshold_analyses, key=lambda x: x.accuracy)

        elif optimization_target == "youden":
            # Maximize Youden's J statistic (TPR - FPR)
            best = max(threshold_analyses, key=lambda x: x.tpr - x.fpr)

        elif optimization_target == "cost":
            # Minimize cost-weighted errors
            def cost_function(analysis):
                return (analysis.false_negatives * fn_cost +
                       analysis.false_positives * fp_cost)

            best = min(threshold_analyses, key=cost_function)

        else:
            raise ValueError(f"Unknown optimization target: {optimization_target}")

        return best.threshold, best

    def criterion_correlation_analysis(
        self,
        scoring_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze which criteria tend to co-occur.

        Args:
            scoring_results: NCI scoring results

        Returns:
            Correlation matrix and common patterns
        """
        # Build co-occurrence matrix
        cooccurrence = defaultdict(lambda: defaultdict(int))
        criterion_counts = defaultdict(int)

        for result in scoring_results:
            if "error" in result or "nci_result" not in result:
                continue

            criteria_scores = result["nci_result"].get("criteria_scores", {})
            matched_criteria = [c for c, data in criteria_scores.items()
                              if data.get("matched", False)]

            # Count individual criteria
            for criterion in matched_criteria:
                criterion_counts[criterion] += 1

            # Count co-occurrences
            for i, c1 in enumerate(matched_criteria):
                for c2 in matched_criteria[i+1:]:
                    cooccurrence[c1][c2] += 1
                    cooccurrence[c2][c1] += 1

        # Find common patterns
        patterns = []
        for c1, c2_counts in cooccurrence.items():
            for c2, count in c2_counts.items():
                if count >= 3:  # Minimum support
                    # Calculate lift (how much more than random)
                    total_sources = len(scoring_results)
                    expected = (criterion_counts[c1] * criterion_counts[c2]) / total_sources
                    lift = count / expected if expected > 0 else 0

                    if lift > 1.5:  # Significant association
                        patterns.append({
                            "criteria": [c1, c2],
                            "count": count,
                            "lift": lift
                        })

        # Sort by lift
        patterns = sorted(patterns, key=lambda x: x["lift"], reverse=True)

        return {
            "criterion_counts": dict(criterion_counts),
            "cooccurrence_matrix": {k: dict(v) for k, v in cooccurrence.items()},
            "common_patterns": patterns[:20]  # Top 20
        }

    def temporal_stability_test(
        self,
        score_runs: List[List[Dict[str, Any]]],
        stability_threshold: float = 0.15
    ) -> List[TemporalStabilityResult]:
        """
        Test scoring stability across multiple runs.

        Args:
            score_runs: List of scoring results from multiple runs
            stability_threshold: CV threshold for considering result stable

        Returns:
            Stability metrics for each source
        """
        if len(score_runs) < 2:
            raise ValueError("Need at least 2 runs for stability testing")

        num_sources = len(score_runs[0])
        stability_results = []

        for source_idx in range(num_sources):
            scores = []
            source_id = None

            for run in score_runs:
                if source_idx < len(run):
                    result = run[source_idx]
                    if "error" not in result:
                        scores.append(result.get("predicted_score", 0))
                        if source_id is None:
                            source_id = result.get("url", f"source_{source_idx}")

            if len(scores) >= 2:
                mean_score = np.mean(scores)
                std_dev = np.std(scores)
                cv = std_dev / mean_score if mean_score > 0 else float('inf')

                stability_results.append(TemporalStabilityResult(
                    source_id=source_id or f"source_{source_idx}",
                    mean_score=float(mean_score),
                    std_dev=float(std_dev),
                    coefficient_of_variation=float(cv),
                    min_score=int(min(scores)),
                    max_score=int(max(scores)),
                    num_runs=len(scores),
                    is_stable=cv < stability_threshold
                ))

        return stability_results

    def error_analysis_report(
        self,
        scoring_results: List[Dict[str, Any]],
        ground_truth_labels: List[str],
        threshold: int = 6
    ) -> Dict[str, Any]:
        """
        Comprehensive error analysis for misclassifications.

        Args:
            scoring_results: NCI scoring results
            ground_truth_labels: Ground truth labels
            threshold: Classification threshold

        Returns:
            Detailed error analysis
        """
        false_positives = []
        false_negatives = []

        for i, result in enumerate(scoring_results):
            if "error" in result or "nci_result" not in result:
                continue

            predicted_score = result.get("predicted_score", 0)
            ground_truth = ground_truth_labels[i]
            predicted = "manipulative" if predicted_score >= threshold else "credible"

            if predicted != ground_truth:
                criteria_scores = result["nci_result"].get("criteria_scores", {})
                matched_criteria = [c for c, data in criteria_scores.items()
                                  if data.get("matched", False)]

                error_info = {
                    "index": i,
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "predicted_score": predicted_score,
                    "ground_truth_score": result.get("ground_truth_score"),
                    "matched_criteria": matched_criteria,
                    "num_criteria": len(matched_criteria),
                    "risk_level": result["nci_result"].get("risk_level", "")
                }

                if predicted == "manipulative" and ground_truth == "credible":
                    false_positives.append(error_info)
                elif predicted == "credible" and ground_truth == "manipulative":
                    false_negatives.append(error_info)

        # Analyze FP patterns
        fp_criteria = Counter()
        for fp in false_positives:
            fp_criteria.update(fp["matched_criteria"])

        # Analyze FN patterns
        fn_criteria = Counter()
        for fn in false_negatives:
            fn_criteria.update(fn["matched_criteria"])

        return {
            "false_positives": {
                "count": len(false_positives),
                "examples": false_positives,
                "common_criteria": fp_criteria.most_common(10),
                "avg_score": np.mean([fp["predicted_score"] for fp in false_positives])
                            if false_positives else 0
            },
            "false_negatives": {
                "count": len(false_negatives),
                "examples": false_negatives,
                "common_criteria": fn_criteria.most_common(10),
                "avg_score": np.mean([fn["predicted_score"] for fn in false_negatives])
                            if false_negatives else 0
            },
            "summary": {
                "total_errors": len(false_positives) + len(false_negatives),
                "fp_rate": len(false_positives) / len(scoring_results),
                "fn_rate": len(false_negatives) / len(scoring_results)
            }
        }

    def export_metrics_to_json(
        self,
        criterion_metrics: List[CriterionPerformance],
        threshold_analyses: List[ThresholdAnalysis],
        correlation_analysis: Dict[str, Any],
        error_analysis: Dict[str, Any],
        output_path: str
    ):
        """Export all advanced metrics to JSON file."""
        data = {
            "criterion_level_performance": [
                {
                    "criterion": m.criterion,
                    "precision": m.precision,
                    "recall": m.recall,
                    "f1_score": m.f1_score,
                    "support": m.support,
                    "prevalence": m.prevalence
                }
                for m in criterion_metrics
            ],
            "threshold_analysis": [
                {
                    "threshold": t.threshold,
                    "accuracy": t.accuracy,
                    "precision": t.precision,
                    "recall": t.recall,
                    "f1_score": t.f1_score,
                    "fpr": t.fpr,
                    "tpr": t.tpr
                }
                for t in threshold_analyses
            ],
            "correlation_analysis": correlation_analysis,
            "error_analysis": error_analysis
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
