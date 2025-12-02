"""Main evaluator for NCI scoring system."""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from src.tools.nci_scoring_tool import NCIScoringTool
from src.eval.dataset_collector import DatasetCollector
from src.eval.metrics import MetricsCalculator, ClassificationMetrics, CalibrationMetrics
from src.eval.config import EvalConfig


class NCIEvaluator:
    """Main evaluator for NCI scoring system."""

    def __init__(self, nci_scorer: Optional[NCIScoringTool] = None):
        """
        Initialize evaluator.

        Args:
            nci_scorer: NCIScoringTool instance (created if not provided)
        """
        self.nci_scorer = nci_scorer or NCIScoringTool()
        self.dataset_collector = DatasetCollector()
        self.metrics_calculator = MetricsCalculator()
        EvalConfig.ensure_directories()

    def evaluate_dataset(
        self,
        dataset: List[Dict[str, Any]],
        threshold: int = EvalConfig.DEFAULT_THRESHOLD,
        save_results: bool = True,
        output_filename: str = "evaluation_results.json",
    ) -> Dict[str, Any]:
        """
        Evaluate a dataset of sources.

        Args:
            dataset: List of source entries with ground truth labels
            threshold: NCI score threshold for binary classification
            save_results: Whether to save results to file
            output_filename: Filename for results

        Returns:
            Comprehensive evaluation results
        """
        # Validate dataset
        validation = self.dataset_collector.validate_dataset(dataset)
        if not validation["valid"]:
            raise ValueError(f"Invalid dataset: {validation['errors']}")

        print(f"Evaluating {len(dataset)} sources...")

        # Score each source
        scoring_results = []
        predicted_scores = []
        ground_truth_labels = []

        for i, source in enumerate(dataset):
            try:
                # Score the source
                score = self.nci_scorer.score_text(
                    text=source.get("text", ""),
                    url=source.get("url", ""),
                    title=source.get("title", ""),
                )

                # Extract score
                agg_score = score.get("aggregate_score", 0)
                predicted_scores.append(agg_score)
                ground_truth_labels.append(source.get("ground_truth_label", ""))

                # Add to results
                result = {
                    "index": i,
                    "url": source.get("url", ""),
                    "title": source.get("title", ""),
                    "ground_truth_label": source.get("ground_truth_label", ""),
                    "ground_truth_score": source.get("ground_truth_score"),
                    "predicted_score": agg_score,
                    "nci_result": score,
                }
                scoring_results.append(result)

                if (i + 1) % 5 == 0:
                    print(f"  Scored {i + 1}/{len(dataset)} sources...")

            except Exception as e:
                print(f"Error scoring source {i}: {str(e)}")
                scoring_results.append({
                    "index": i,
                    "url": source.get("url", ""),
                    "title": source.get("title", ""),
                    "error": str(e),
                })

        print(f"Completed scoring. Calculating metrics...")

        # Calculate classification metrics
        classification_metrics = self.metrics_calculator.binary_classification_metrics(
            predicted_scores=predicted_scores,
            ground_truth_labels=ground_truth_labels,
            threshold=threshold,
        )

        # Calculate calibration metrics
        calibration_metrics, calibration_data = self.metrics_calculator.calibration_metrics(
            predicted_scores=predicted_scores,
            ground_truth_labels=ground_truth_labels,
        )

        # Calculate per-criterion metrics
        criterion_metrics = self.metrics_calculator.per_criterion_metrics(
            criteria_results=scoring_results,
            ground_truth_labels=ground_truth_labels,
        )

        # Calculate score distributions
        score_distribution = self.metrics_calculator.score_distribution_analysis(
            predicted_scores=predicted_scores,
            ground_truth_labels=ground_truth_labels,
        )

        # Calculate risk level analysis
        risk_analysis = self.metrics_calculator.risk_level_analysis(
            predicted_scores=predicted_scores,
            ground_truth_labels=ground_truth_labels,
        )

        # Compile results
        evaluation_results = {
            "metadata": {
                "timestamp": time.time(),
                "total_sources": len(dataset),
                "threshold": threshold,
                "successfully_scored": len(scoring_results),
            },
            "classification_metrics": self.metrics_calculator.metrics_to_dict(classification_metrics),
            "calibration_metrics": self.metrics_calculator.metrics_to_dict(calibration_metrics),
            "calibration_data": calibration_data,
            "criterion_metrics": [
                self.metrics_calculator.metrics_to_dict(cm) for cm in criterion_metrics
            ],
            "score_distribution": score_distribution,
            "risk_analysis": risk_analysis,
            "scoring_results": scoring_results,
        }

        # Save if requested
        if save_results:
            output_path = EvalConfig.EVAL_OUTPUT_DIR / output_filename
            with open(output_path, "w") as f:
                json.dump(evaluation_results, f, indent=2, default=str)
            print(f"Saved evaluation results to {output_path}")

        return evaluation_results

    def compare_thresholds(
        self,
        dataset: List[Dict[str, Any]],
        thresholds: Optional[List[int]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """
        Compare performance across different thresholds.

        Args:
            dataset: List of source entries
            thresholds: List of thresholds to test (default: 3-15)

        Returns:
            Dictionary mapping threshold to metrics
        """
        if thresholds is None:
            thresholds = list(range(3, 16))

        print(f"Comparing {len(thresholds)} thresholds...")

        results = {}
        for threshold in thresholds:
            print(f"  Testing threshold={threshold}...")
            eval_result = self.evaluate_dataset(
                dataset=dataset,
                threshold=threshold,
                save_results=False,
            )
            results[threshold] = eval_result

        return results

    def generate_confusion_data(
        self,
        evaluation_results: Dict[str, Any],
    ) -> Dict[str, int]:
        """
        Generate confusion matrix data from evaluation results.

        Args:
            evaluation_results: Results from evaluate_dataset

        Returns:
            Confusion matrix data
        """
        metrics = evaluation_results.get("classification_metrics", {})
        return {
            "TP": metrics.get("true_positives", 0),
            "TN": metrics.get("true_negatives", 0),
            "FP": metrics.get("false_positives", 0),
            "FN": metrics.get("false_negatives", 0),
        }

    def find_misclassifications(
        self,
        evaluation_results: Dict[str, Any],
        label_type: str = "all",  # 'false_positive', 'false_negative', 'correct', 'all'
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find misclassified sources.

        Args:
            evaluation_results: Results from evaluate_dataset
            label_type: Type of misclassification to find
            limit: Maximum number to return

        Returns:
            List of misclassified sources
        """
        threshold = evaluation_results["metadata"]["threshold"]
        scoring_results = evaluation_results.get("scoring_results", [])

        misclassifications = []
        for result in scoring_results:
            if "error" in result:
                continue

            predicted_score = result.get("predicted_score", 0)
            ground_truth = result.get("ground_truth_label", "")
            predicted = "manipulative" if predicted_score >= threshold else "credible"

            is_correct = predicted == ground_truth
            is_fp = (predicted == "manipulative" and ground_truth == "credible")
            is_fn = (predicted == "credible" and ground_truth == "manipulative")

            if label_type == "all" or \
               (label_type == "false_positive" and is_fp) or \
               (label_type == "false_negative" and is_fn) or \
               (label_type == "correct" and is_correct):
                misclassifications.append({
                    **result,
                    "predicted_label": predicted,
                    "error_type": "FP" if is_fp else "FN" if is_fn else "Correct",
                })

        return misclassifications[:limit]

