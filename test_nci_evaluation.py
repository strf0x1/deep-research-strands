#!/usr/bin/env python3
"""
Quick test script for NCI evaluation framework using synthetic demo dataset.

Usage:
    uv run test_nci_evaluation.py

This script:
1. Loads the synthetic NCI demo dataset
2. Runs evaluation
3. Displays results
4. Generates visualizations and reports
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.eval.dataset_collector import DatasetCollector
from src.eval.evaluator import NCIEvaluator
from src.eval.visualizer import EvaluationVisualizer
from src.eval.report_generator import ReportGenerator
from src.eval.config import EvalConfig

console = Console()


def main():
    """Run NCI evaluation on synthetic demo dataset."""
    
    # Display header
    banner = "[bold cyan]NCI EVALUATION FRAMEWORK[/bold cyan]\n[dim]Testing with Synthetic Demo Dataset[/dim]"
    console.print(Panel(banner, expand=False, border_style="cyan"))
    
    # Load synthetic dataset
    dataset_path = Path("data/eval_datasets/nci_synthetic_demo.json")
    
    if not dataset_path.exists():
        console.print(f"[bold red]Error:[/bold red] Dataset not found at {dataset_path}")
        sys.exit(1)
    
    console.print(f"\n[bold]Loading dataset...[/bold]")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
    
    console.print(f"[green]✓[/green] Loaded {len(dataset)} examples")
    
    # Display dataset summary
    manipulative_count = sum(1 for s in dataset if s["ground_truth_label"] == "manipulative")
    credible_count = sum(1 for s in dataset if s["ground_truth_label"] == "credible")
    
    summary_table = Table(title="Dataset Summary")
    summary_table.add_column("Type", style="cyan")
    summary_table.add_column("Count", style="green")
    summary_table.add_row("Manipulative", str(manipulative_count))
    summary_table.add_row("Credible", str(credible_count))
    summary_table.add_row("Total", str(len(dataset)))
    console.print(summary_table)
    
    # Validate dataset
    console.print(f"\n[bold]Validating dataset...[/bold]")
    collector = DatasetCollector()
    validation = collector.validate_dataset(dataset)
    
    if not validation["valid"]:
        console.print("[bold red]Dataset validation failed:[/bold red]")
        for error in validation["errors"]:
            console.print(f"  [red]✗[/red] {error}")
        sys.exit(1)
    
    console.print(f"[green]✓[/green] Dataset validation passed")
    
    # Show example sources
    console.print(f"\n[bold]Sample Sources:[/bold]")
    for i, source in enumerate(dataset[:3]):
        label = "[red]MANIPULATIVE[/red]" if source["ground_truth_label"] == "manipulative" else "[green]CREDIBLE[/green]"
        score = f"({source.get('ground_truth_score', '?')}/20)"
        console.print(f"\n{i+1}. {label} {score}")
        console.print(f"   Title: {source['title'][:70]}")
        if "metadata" in source and "primary_criteria" in source["metadata"]:
            criteria = source["metadata"]["primary_criteria"]
            if criteria:
                console.print(f"   Criteria: {', '.join(criteria[:3])}")
    
    # Run evaluation
    console.print(f"\n[bold]Running NCI Evaluation...[/bold]")
    console.print("(This will score each source using the NCI system)")
    
    evaluator = NCIEvaluator()
    evaluation_results = evaluator.evaluate_dataset(
        dataset=dataset,
        threshold=6,
        save_results=True,
        output_filename="nci_demo_results.json",
    )
    
    # Display results
    print_evaluation_results(evaluation_results)
    
    # Generate visualizations
    console.print(f"\n[bold]Generating visualizations...[/bold]")
    visualizer = EvaluationVisualizer()
    visualizations = visualizer.generate_all_visualizations(evaluation_results)
    
    console.print(f"[green]✓[/green] Generated {len(visualizations)} visualizations:")
    for name, path in visualizations.items():
        console.print(f"  - {name}")
    
    # Generate reports
    console.print(f"\n[bold]Generating reports...[/bold]")
    report_gen = ReportGenerator()
    html_path = report_gen.generate_html_report(evaluation_results, visualizations)
    md_path = report_gen.generate_markdown_report(evaluation_results)
    
    # Display final results
    console.print(f"\n[bold green]✓ Evaluation Complete![/bold green]")
    console.print(f"\n[bold]Output Files:[/bold]")
    console.print(f"  [cyan]HTML Report:[/cyan] {html_path}")
    console.print(f"  [cyan]Markdown Report:[/cyan] {md_path}")
    console.print(f"  [cyan]Metrics JSON:[/cyan] {EvalConfig.EVAL_OUTPUT_DIR}/nci_demo_results.json")
    
    console.print(f"\n[bold yellow]Next Steps:[/bold yellow]")
    console.print(f"1. Open the HTML report in your browser:")
    console.print(f"   open {html_path}")
    console.print(f"2. Review the visualizations and metrics")
    console.print(f"3. Check individual source analysis in the metrics JSON")
    console.print(f"4. Try different thresholds:")
    console.print(f"   uv run src/eval/cli.py --compare-thresholds \\")
    console.print(f"     --dataset data/eval_datasets/nci_synthetic_demo.json")


def print_evaluation_results(evaluation_results):
    """Display evaluation results in a nice format."""
    
    metrics = evaluation_results.get("classification_metrics", {})
    calibration = evaluation_results.get("calibration_metrics", {})
    score_dist = evaluation_results.get("score_distribution", {})
    
    # Classification metrics table
    console.print(f"\n[bold cyan]Classification Metrics:[/bold cyan]")
    metrics_table = Table()
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_column("Meaning", style="dim")
    
    metrics_table.add_row(
        "Accuracy",
        f"{metrics.get('accuracy', 0):.1%}",
        "Overall correctness"
    )
    metrics_table.add_row(
        "Precision",
        f"{metrics.get('precision', 0):.1%}",
        "When flagged manipulative, % correct"
    )
    metrics_table.add_row(
        "Recall",
        f"{metrics.get('recall', 0):.1%}",
        "% of manipulative sources detected"
    )
    metrics_table.add_row(
        "F1-Score",
        f"{metrics.get('f1', 0):.2f}",
        "Balance of precision & recall"
    )
    
    console.print(metrics_table)
    
    # Confusion matrix
    console.print(f"\n[bold cyan]Confusion Matrix:[/bold cyan]")
    cm_table = Table()
    cm_table.add_column("", style="dim")
    cm_table.add_column("Predicted Credible", style="blue")
    cm_table.add_column("Predicted Manipulative", style="red")
    
    cm_table.add_row(
        "[blue]Actually Credible[/blue]",
        str(metrics.get("true_negatives", 0)),
        f"[red]{metrics.get('false_positives', 0)}[/red]"
    )
    cm_table.add_row(
        "[red]Actually Manipulative[/red]",
        str(metrics.get("false_negatives", 0)),
        f"[green]{metrics.get('true_positives', 0)}[/green]"
    )
    
    console.print(cm_table)
    
    # Calibration metrics
    console.print(f"\n[bold cyan]Calibration Metrics:[/bold cyan]")
    calib_table = Table()
    calib_table.add_column("Metric", style="cyan")
    calib_table.add_column("Value", style="green")
    calib_table.add_column("Meaning", style="dim")
    
    calib_table.add_row(
        "Brier Score",
        f"{calibration.get('brier_score', 0):.4f}",
        "Prediction error (0=perfect, 1=worst)"
    )
    calib_table.add_row(
        "ECE (Expected Calibration Error)",
        f"{calibration.get('expected_calibration_error', 0):.4f}",
        "Avg calibration discrepancy"
    )
    calib_table.add_row(
        "MCE (Max Calibration Error)",
        f"{calibration.get('max_calibration_error', 0):.4f}",
        "Worst-case calibration error"
    )
    
    console.print(calib_table)
    
    # Score distribution
    console.print(f"\n[bold cyan]Score Distribution:[/bold cyan]")
    dist_table = Table()
    dist_table.add_column("Category", style="cyan")
    dist_table.add_column("Mean", style="green")
    dist_table.add_column("Median", style="green")
    dist_table.add_column("Range", style="dim")
    dist_table.add_column("Count", style="green")
    
    manip = score_dist.get("manipulative", {})
    dist_table.add_row(
        "[red]Manipulative[/red]",
        f"{manip.get('mean', 0):.1f}",
        f"{manip.get('median', 0):.1f}",
        f"{manip.get('min', 0)}-{manip.get('max', 0)}",
        str(manip.get("count", 0))
    )
    
    cred = score_dist.get("credible", {})
    dist_table.add_row(
        "[green]Credible[/green]",
        f"{cred.get('mean', 0):.1f}",
        f"{cred.get('median', 0):.1f}",
        f"{cred.get('min', 0)}-{cred.get('max', 0)}",
        str(cred.get("count", 0))
    )
    
    console.print(dist_table)
    
    # Interpretation
    console.print(f"\n[bold cyan]Interpretation:[/bold cyan]")
    accuracy = metrics.get("accuracy", 0)
    if accuracy >= 0.8:
        console.print("[green]✓ High accuracy:[/green] System performs well at distinguishing sources")
    elif accuracy >= 0.6:
        console.print("[yellow]⚠ Moderate accuracy:[/yellow] System works but has room for improvement")
    else:
        console.print("[red]✗ Low accuracy:[/red] System needs tuning")
    
    mean_sep = abs(manip.get('mean', 0) - cred.get('mean', 0))
    console.print(f"\n[dim]Score separation:[/dim] Manipulative sources scored {mean_sep:.1f} points higher on average")
    console.print(f"[dim](Range: 0-20, Threshold: 6)[/dim]")


if __name__ == "__main__":
    main()

