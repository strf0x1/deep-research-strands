"""Visualization generator for NCI evaluation results."""

from typing import Dict, List, Any
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Rectangle
import seaborn as sns
from src.eval.config import EvalConfig

# Set style
matplotlib.use("Agg")
sns.set_style("whitegrid")


class EvaluationVisualizer:
    """Generate visualizations for evaluation results."""

    def __init__(self):
        """Initialize visualizer."""
        EvalConfig.ensure_directories()
        self.output_dir = EvalConfig.EVAL_OUTPUT_DIR

    def plot_confusion_matrix(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "confusion_matrix.png",
    ) -> Path:
        """
        Plot confusion matrix.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        metrics = evaluation_results.get("classification_metrics", {})
        tp = metrics.get("true_positives", 0)
        tn = metrics.get("true_negatives", 0)
        fp = metrics.get("false_positives", 0)
        fn = metrics.get("false_negatives", 0)

        cm = np.array([[tn, fp], [fn, tp]])

        fig, ax = plt.subplots(figsize=(8, 6), dpi=EvalConfig.PLOT_DPI)
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")

        plt.colorbar(im, ax=ax)
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")
        ax.set_title("Confusion Matrix (NCI Evaluation)")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Credible", "Manipulative"])
        ax.set_yticklabels(["Credible", "Manipulative"])

        # Add text annotations
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def plot_score_distributions(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "score_distributions.png",
    ) -> Path:
        """
        Plot score distributions for manipulative vs credible sources.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        scoring_results = evaluation_results.get("scoring_results", [])

        manipulative_scores = []
        credible_scores = []

        for result in scoring_results:
            if "error" not in result:
                score = result.get("predicted_score", 0)
                label = result.get("ground_truth_label", "")
                if label == "manipulative":
                    manipulative_scores.append(score)
                else:
                    credible_scores.append(score)

        fig, ax = plt.subplots(figsize=(10, 6), dpi=EvalConfig.PLOT_DPI)

        ax.hist([credible_scores, manipulative_scores], label=["Credible", "Manipulative"], bins=10, alpha=0.7)
        ax.set_xlabel("NCI Score")
        ax.set_ylabel("Frequency")
        ax.set_title("Score Distribution: Credible vs Manipulative Sources")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def plot_calibration_curve(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "calibration_curve.png",
    ) -> Path:
        """
        Plot calibration curve.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        calibration_data = evaluation_results.get("calibration_data", {})
        bin_data = calibration_data.get("bin_data", [])

        if not bin_data:
            # Return a placeholder
            fig, ax = plt.subplots(figsize=(8, 6), dpi=EvalConfig.PLOT_DPI)
            ax.text(0.5, 0.5, "No calibration data available", ha="center", va="center")
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
            plt.close()
            return output_path

        confidences = [b["confidence"] for b in bin_data]
        actuals = [b["actual"] for b in bin_data]

        fig, ax = plt.subplots(figsize=(8, 6), dpi=EvalConfig.PLOT_DPI)

        # Perfect calibration line
        ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=2)

        # Actual calibration
        ax.scatter(confidences, actuals, s=100, label="Actual", alpha=0.6)

        # Add bin size labels
        for conf, actual, bin_info in zip(confidences, actuals, bin_data):
            ax.annotate(f"n={bin_info['samples']}", (conf, actual), fontsize=8, alpha=0.7)

        ax.set_xlabel("Predicted Score (normalized)")
        ax.set_ylabel("Actual Manipulation Rate")
        ax.set_title("Calibration Curve")
        ax.legend()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def plot_criterion_metrics(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "criterion_metrics.png",
    ) -> Path:
        """
        Plot per-criterion performance.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        criterion_metrics = evaluation_results.get("criterion_metrics", [])

        if not criterion_metrics:
            fig, ax = plt.subplots(figsize=(10, 8), dpi=EvalConfig.PLOT_DPI)
            ax.text(0.5, 0.5, "No criterion metrics available", ha="center", va="center")
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
            plt.close()
            return output_path

        criteria = [m["criterion"] for m in criterion_metrics]
        precisions = [m["precision"] for m in criterion_metrics]
        recalls = [m["recall"] for m in criterion_metrics]
        f1_scores = [m["f1"] for m in criterion_metrics]

        fig, ax = plt.subplots(figsize=(12, 6), dpi=EvalConfig.PLOT_DPI)

        x = np.arange(len(criteria))
        width = 0.25

        ax.bar(x - width, precisions, width, label="Precision", alpha=0.8)
        ax.bar(x, recalls, width, label="Recall", alpha=0.8)
        ax.bar(x + width, f1_scores, width, label="F1-Score", alpha=0.8)

        ax.set_xlabel("NCI Criterion")
        ax.set_ylabel("Score")
        ax.set_title("Per-Criterion Performance Metrics")
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("_", "\n") for c in criteria], fontsize=8)
        ax.legend()
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def plot_metrics_summary(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "metrics_summary.png",
    ) -> Path:
        """
        Plot summary of key metrics.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        metrics = evaluation_results.get("classification_metrics", {})
        calibration = evaluation_results.get("calibration_metrics", {})

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8), dpi=EvalConfig.PLOT_DPI)

        # Precision/Recall/F1
        ax1.bar(
            ["Precision", "Recall", "F1-Score"],
            [metrics.get("precision", 0), metrics.get("recall", 0), metrics.get("f1", 0)],
            color=["#1f77b4", "#ff7f0e", "#2ca02c"],
        )
        ax1.set_ylim(0, 1)
        ax1.set_title("Classification Metrics")
        ax1.set_ylabel("Score")
        ax1.grid(True, alpha=0.3, axis="y")

        # Accuracy
        ax2.bar(["Accuracy"], [metrics.get("accuracy", 0)], color="#d62728")
        ax2.set_ylim(0, 1)
        ax2.set_title("Overall Accuracy")
        ax2.set_ylabel("Score")
        ax2.grid(True, alpha=0.3, axis="y")

        # Calibration metrics
        ax3.bar(
            ["Brier Score", "ECE", "MCE"],
            [
                calibration.get("brier_score", 0),
                calibration.get("expected_calibration_error", 0),
                calibration.get("max_calibration_error", 0),
            ],
            color=["#9467bd", "#8c564b", "#e377c2"],
        )
        ax3.set_title("Calibration Metrics")
        ax3.set_ylabel("Score")
        ax3.grid(True, alpha=0.3, axis="y")

        # Confusion matrix as text
        cm = np.array([
            [metrics.get("true_negatives", 0), metrics.get("false_positives", 0)],
            [metrics.get("false_negatives", 0), metrics.get("true_positives", 0)],
        ])
        ax4.axis("off")
        confusion_text = f"""
Confusion Matrix:
  Predicted Credible: {cm[0, 0] + cm[1, 0]}
  Predicted Manip.: {cm[0, 1] + cm[1, 1]}

  True Negatives:  {cm[0, 0]}
  False Positives: {cm[0, 1]}
  False Negatives: {cm[1, 0]}
  True Positives:  {cm[1, 1]}
"""
        ax4.text(0.1, 0.5, confusion_text, fontsize=10, family="monospace", verticalalignment="center")
        ax4.set_title("Confusion Matrix Summary")

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def plot_risk_level_distribution(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "risk_level_distribution.png",
    ) -> Path:
        """
        Plot risk level distribution.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved figure
        """
        risk_analysis = evaluation_results.get("risk_analysis", {})
        cross_tab = risk_analysis.get("cross_tabulation", {})

        if not cross_tab:
            fig, ax = plt.subplots(figsize=(10, 6), dpi=EvalConfig.PLOT_DPI)
            ax.text(0.5, 0.5, "No risk level data available", ha="center", va="center")
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
            plt.close()
            return output_path

        # Organize data
        risk_levels = ["LOW", "MODERATE", "HIGH", "CRITICAL"]
        true_labels = ["manipulative", "credible"]

        data = {}
        for risk in risk_levels:
            data[risk] = {"manipulative": 0, "credible": 0}
            for true_label in true_labels:
                key = f"{risk}_vs_{true_label}"
                data[risk][true_label] = cross_tab.get(key, 0)

        fig, ax = plt.subplots(figsize=(10, 6), dpi=EvalConfig.PLOT_DPI)

        x = np.arange(len(risk_levels))
        width = 0.35

        manipulative_counts = [data[risk]["manipulative"] for risk in risk_levels]
        credible_counts = [data[risk]["credible"] for risk in risk_levels]

        ax.bar(x - width / 2, manipulative_counts, width, label="Actually Manipulative", alpha=0.8)
        ax.bar(x + width / 2, credible_counts, width, label="Actually Credible", alpha=0.8)

        ax.set_xlabel("Predicted Risk Level")
        ax.set_ylabel("Count")
        ax.set_title("Risk Level Distribution")
        ax.set_xticks(x)
        ax.set_xticklabels(risk_levels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=EvalConfig.PLOT_DPI, bbox_inches="tight")
        plt.close()

        return output_path

    def generate_all_visualizations(
        self,
        evaluation_results: Dict[str, Any],
    ) -> Dict[str, Path]:
        """
        Generate all evaluation visualizations.

        Args:
            evaluation_results: Results from evaluator

        Returns:
            Dictionary mapping visualization names to file paths
        """
        print("Generating visualizations...")

        visualizations = {
            "confusion_matrix": self.plot_confusion_matrix(evaluation_results),
            "score_distributions": self.plot_score_distributions(evaluation_results),
            "calibration_curve": self.plot_calibration_curve(evaluation_results),
            "criterion_metrics": self.plot_criterion_metrics(evaluation_results),
            "metrics_summary": self.plot_metrics_summary(evaluation_results),
            "risk_level_distribution": self.plot_risk_level_distribution(evaluation_results),
        }

        print("Visualizations generated successfully!")
        for name, path in visualizations.items():
            print(f"  - {name}: {path}")

        return visualizations

