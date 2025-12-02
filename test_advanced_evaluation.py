#!/usr/bin/env python3
"""
Advanced NCI Evaluation Test Script

This script demonstrates the new advanced evaluation capabilities:
1. Dataset expansion with adversarial examples
2. Criterion-level performance metrics
3. Threshold optimization analysis
4. Error analysis
5. Criterion correlation analysis

Usage:
    uv run test_advanced_evaluation.py
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.eval.dataset_expansion import DatasetExpander
from src.eval.evaluator import NCIEvaluator
from src.eval.advanced_metrics import AdvancedMetricsCalculator
from src.eval.config import EvalConfig

console = Console()


def main():
    """Run advanced NCI evaluation."""

    # Display header
    banner = """[bold cyan]ADVANCED NCI EVALUATION FRAMEWORK[/bold cyan]
[dim]Testing expanded capabilities and deeper analysis[/dim]"""
    console.print(Panel(banner, expand=False, border_style="cyan"))

    # Step 1: Load and expand dataset
    console.print("\n[bold]Step 1: Dataset Expansion[/bold]")
    dataset_path = Path("data/eval_datasets/nci_synthetic_demo.json")

    if not dataset_path.exists():
        console.print(f"[bold red]Error:[/bold red] Dataset not found at {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r") as f:
        base_dataset = json.load(f)

    console.print(f"  Loaded base dataset: {len(base_dataset)} examples")

    # Analyze coverage gaps
    expander = DatasetExpander()
    gaps = expander.analyze_coverage_gaps(base_dataset)

    console.print(f"\n  Coverage Analysis:")
    for gap in gaps[:5]:  # Top 5 gaps
        console.print(f"    [yellow]•[/yellow] {gap.category}: "
                     f"{gap.current_count}/{gap.target_count} "
                     f"(need {gap.examples_needed})")

    # Create expanded dataset
    expanded_path = Path("data/eval_datasets/nci_expanded_demo.json")
    expander.save_expanded_dataset(
        base_dataset=base_dataset,
        output_path=expanded_path,
        include_adversarial=True,
        include_borderline=True
    )

    # Load expanded dataset
    with open(expanded_path, "r") as f:
        expanded_dataset = json.load(f)

    console.print(f"\n  [green]✓[/green] Expanded dataset: {len(expanded_dataset)} examples")

    # Step 2: Run evaluation
    console.print("\n[bold]Step 2: Running NCI Evaluation[/bold]")
    evaluator = NCIEvaluator()
    evaluation_results = evaluator.evaluate_dataset(
        dataset=expanded_dataset,
        threshold=6,
        save_results=True,
        output_filename="nci_advanced_results.json",
    )

    metrics = evaluation_results["classification_metrics"]
    console.print(f"  [green]✓[/green] Evaluation complete")
    console.print(f"    Accuracy: {metrics['accuracy']:.1%}")
    console.print(f"    Precision: {metrics['precision']:.1%}")
    console.print(f"    Recall: {metrics['recall']:.1%}")
    console.print(f"    F1: {metrics['f1']:.2f}")

    # Step 3: Advanced Metrics
    console.print("\n[bold]Step 3: Advanced Metrics Analysis[/bold]")
    advanced_calc = AdvancedMetricsCalculator()

    # Criterion-level metrics
    console.print("\n  [cyan]Criterion-Level Performance:[/cyan]")
    criterion_metrics = advanced_calc.criterion_level_metrics(
        scoring_results=evaluation_results["scoring_results"],
        ground_truth_labels=[s["ground_truth_label"] for s in expanded_dataset]
    )

    # Display top and bottom performers
    perf_table = Table(title="Top 5 & Bottom 5 Criteria Performance", box=box.SIMPLE)
    perf_table.add_column("Criterion", style="cyan")
    perf_table.add_column("F1", style="green")
    perf_table.add_column("Precision", style="blue")
    perf_table.add_column("Recall", style="magenta")
    perf_table.add_column("Support", style="dim")

    for metric in criterion_metrics[:5]:
        perf_table.add_row(
            metric.criterion.replace("_", " ").title(),
            f"{metric.f1_score:.3f}",
            f"{metric.precision:.3f}",
            f"{metric.recall:.3f}",
            str(metric.support)
        )

    perf_table.add_row("...", "...", "...", "...", "...", style="dim")

    for metric in criterion_metrics[-5:]:
        perf_table.add_row(
            metric.criterion.replace("_", " ").title(),
            f"{metric.f1_score:.3f}",
            f"{metric.precision:.3f}",
            f"{metric.recall:.3f}",
            str(metric.support),
            style="yellow"
        )

    console.print(perf_table)

    # Threshold optimization
    console.print("\n  [cyan]Threshold Optimization:[/cyan]")
    threshold_analyses, roc_data = advanced_calc.threshold_optimization_analysis(
        predicted_scores=[r.get("predicted_score", 0) for r in evaluation_results["scoring_results"]],
        ground_truth_labels=[s["ground_truth_label"] for s in expanded_dataset]
    )

    # Find optimal thresholds for different objectives
    opt_f1_thresh, opt_f1 = advanced_calc.find_optimal_threshold(
        threshold_analyses, optimization_target="f1"
    )
    opt_youden_thresh, opt_youden = advanced_calc.find_optimal_threshold(
        threshold_analyses, optimization_target="youden"
    )

    # Cost-optimized (weight false negatives 3x higher)
    opt_cost_thresh, opt_cost = advanced_calc.find_optimal_threshold(
        threshold_analyses, optimization_target="cost", fn_cost=3.0, fp_cost=1.0
    )

    thresh_table = Table(title="Optimal Thresholds for Different Objectives", box=box.SIMPLE)
    thresh_table.add_column("Objective", style="cyan")
    thresh_table.add_column("Threshold", style="green")
    thresh_table.add_column("F1", style="blue")
    thresh_table.add_column("Precision", style="magenta")
    thresh_table.add_column("Recall", style="yellow")

    thresh_table.add_row(
        "F1 Maximization",
        str(opt_f1_thresh),
        f"{opt_f1.f1_score:.3f}",
        f"{opt_f1.precision:.3f}",
        f"{opt_f1.recall:.3f}"
    )
    thresh_table.add_row(
        "Youden's J (balanced)",
        str(opt_youden_thresh),
        f"{opt_youden.f1_score:.3f}",
        f"{opt_youden.precision:.3f}",
        f"{opt_youden.recall:.3f}"
    )
    thresh_table.add_row(
        "Cost-optimized (FN=3x FP)",
        str(opt_cost_thresh),
        f"{opt_cost.f1_score:.3f}",
        f"{opt_cost.precision:.3f}",
        f"{opt_cost.recall:.3f}"
    )
    thresh_table.add_row(
        "Current (threshold=6)",
        "6",
        f"{metrics['f1']:.3f}",
        f"{metrics['precision']:.3f}",
        f"{metrics['recall']:.3f}",
        style="bold"
    )

    console.print(thresh_table)

    if "auc" in roc_data:
        console.print(f"\n  ROC AUC Score: [green]{roc_data['auc']:.3f}[/green]")

    # Error analysis
    console.print("\n  [cyan]Error Analysis:[/cyan]")
    error_analysis = advanced_calc.error_analysis_report(
        scoring_results=evaluation_results["scoring_results"],
        ground_truth_labels=[s["ground_truth_label"] for s in expanded_dataset],
        threshold=6
    )

    console.print(f"    False Positives: {error_analysis['false_positives']['count']}")
    if error_analysis['false_positives']['count'] > 0:
        console.print(f"      Avg Score: {error_analysis['false_positives']['avg_score']:.1f}")
        console.print(f"      Common criteria:")
        for criterion, count in error_analysis['false_positives']['common_criteria'][:3]:
            console.print(f"        • {criterion.replace('_', ' ').title()}: {count}x")

    console.print(f"\n    False Negatives: {error_analysis['false_negatives']['count']}")
    if error_analysis['false_negatives']['count'] > 0:
        console.print(f"      Avg Score: {error_analysis['false_negatives']['avg_score']:.1f}")

    # Criterion correlation
    console.print("\n  [cyan]Criterion Correlation Analysis:[/cyan]")
    correlation = advanced_calc.criterion_correlation_analysis(
        scoring_results=evaluation_results["scoring_results"]
    )

    console.print(f"    Found {len(correlation['common_patterns'])} significant co-occurrence patterns")
    if correlation['common_patterns']:
        console.print(f"    Top patterns:")
        for pattern in correlation['common_patterns'][:5]:
            c1, c2 = pattern['criteria']
            console.print(f"      • {c1.replace('_', ' ').title()} + "
                         f"{c2.replace('_', ' ').title()}: "
                         f"{pattern['count']}x (lift: {pattern['lift']:.2f})")

    # Step 4: Export comprehensive results
    console.print("\n[bold]Step 4: Exporting Results[/bold]")
    advanced_output_path = EvalConfig.EVAL_OUTPUT_DIR / "nci_advanced_metrics.json"
    advanced_calc.export_metrics_to_json(
        criterion_metrics=criterion_metrics,
        threshold_analyses=threshold_analyses,
        correlation_analysis=correlation,
        error_analysis=error_analysis,
        output_path=str(advanced_output_path)
    )

    console.print(f"  [green]✓[/green] Saved to {advanced_output_path}")

    # Final summary
    console.print("\n[bold green]✓ Advanced Evaluation Complete![/bold green]")

    console.print(f"\n[bold]Key Insights:[/bold]")

    # Identify weakest criteria
    weakest = criterion_metrics[-3:]
    console.print(f"  [yellow]Criteria needing attention:[/yellow]")
    for m in weakest:
        console.print(f"    • {m.criterion.replace('_', ' ').title()}: F1={m.f1_score:.3f}")

    # Threshold recommendation
    if opt_f1_thresh != 6:
        console.print(f"\n  [yellow]Threshold recommendation:[/yellow]")
        console.print(f"    Consider threshold={opt_f1_thresh} for F1 maximization")
        console.print(f"    Would improve F1 from {metrics['f1']:.3f} to {opt_f1.f1_score:.3f}")

    # Dataset recommendations
    console.print(f"\n  [yellow]Dataset recommendations:[/yellow]")
    high_priority_gaps = [g for g in gaps if g.priority == "high"]
    if high_priority_gaps:
        for gap in high_priority_gaps[:3]:
            console.print(f"    • Add {gap.examples_needed} examples for: {gap.category}")

    console.print(f"\n[bold]Output Files:[/bold]")
    console.print(f"  Expanded Dataset: {expanded_path}")
    console.print(f"  Evaluation Results: {EvalConfig.EVAL_OUTPUT_DIR}/nci_advanced_results.json")
    console.print(f"  Advanced Metrics: {advanced_output_path}")


if __name__ == "__main__":
    main()
