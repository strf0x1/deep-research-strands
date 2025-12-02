"""CLI tool for NCI evaluation framework."""

import sys
import argparse
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from src.eval.dataset_collector import DatasetCollector
from src.eval.evaluator import NCIEvaluator
from src.eval.visualizer import EvaluationVisualizer
from src.eval.report_generator import ReportGenerator
from src.eval.config import EvalConfig

console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NCI Evaluation Framework - Evaluate NCI scoring system performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create sample dataset
  uv run src/eval/cli.py --create-samples --output sample_data.json
  
  # Run evaluation on dataset
  uv run src/eval/cli.py --evaluate --dataset sample_data.json
  
  # Generate report from results
  uv run src/eval/cli.py --report --results eval_output/evaluation_results.json
  
  # Compare multiple thresholds
  uv run src/eval/cli.py --compare-thresholds --dataset sample_data.json
        """,
    )

    parser.add_argument(
        "--create-samples",
        action="store_true",
        help="Create sample evaluation dataset",
    )

    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run NCI evaluation on a dataset",
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML and markdown reports",
    )

    parser.add_argument(
        "--compare-thresholds",
        action="store_true",
        help="Compare NCI performance across different thresholds",
    )

    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to input dataset JSON file",
    )

    parser.add_argument(
        "--results",
        type=str,
        help="Path to evaluation results JSON file",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file path",
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=EvalConfig.DEFAULT_THRESHOLD,
        help=f"NCI score threshold for binary classification (default: {EvalConfig.DEFAULT_THRESHOLD})",
    )

    parser.add_argument(
        "--visualizations",
        action="store_true",
        help="Generate visualizations",
    )

    parser.add_argument(
        "--thresholds",
        type=str,
        help="Comma-separated list of thresholds to compare (e.g., 3,5,6,8,10)",
    )

    args = parser.parse_args()

    # Display banner
    display_banner()

    # Ensure directories exist
    EvalConfig.ensure_directories()

    try:
        if args.create_samples:
            create_samples(args.output)
        elif args.evaluate:
            if not args.dataset:
                console.print("[bold red]Error:[/bold red] --dataset required for --evaluate")
                sys.exit(1)
            run_evaluation(args.dataset, args.threshold, args.visualizations)
        elif args.compare_thresholds:
            if not args.dataset:
                console.print("[bold red]Error:[/bold red] --dataset required for --compare-thresholds")
                sys.exit(1)
            compare_thresholds(args.dataset, args.thresholds)
        elif args.report:
            if not args.results:
                console.print("[bold red]Error:[/bold red] --results required for --report")
                sys.exit(1)
            generate_report(args.results)
        else:
            parser.print_help()

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def display_banner():
    """Display CLI banner."""
    banner_text = "[bold cyan]NCI EVALUATION FRAMEWORK[/bold cyan]\n"
    banner_text += "[dim]Evaluate NCI scoring system performance[/dim]"
    console.print(Panel(banner_text, expand=False, border_style="cyan"))


def create_samples(output_path: str = None):
    """Create sample evaluation dataset."""
    console.print("\n[bold]Creating sample dataset...[/bold]")

    collector = DatasetCollector()
    samples = collector.create_sample_dataset()

    output_file = output_path or "sample_test_set.json"
    output_path = collector.save_dataset(samples, output_file)

    console.print(f"[green]✓[/green] Sample dataset created: [cyan]{output_path}[/cyan]")
    console.print(f"  - {len(samples)} sample sources")
    console.print(f"  - Mix of manipulative and credible content")
    console.print(f"  - Ready for evaluation")


def run_evaluation(dataset_path: str, threshold: int = 6, generate_vis: bool = False):
    """Run NCI evaluation on dataset."""
    # Load dataset
    console.print(f"\n[bold]Loading dataset from {dataset_path}...[/bold]")
    
    try:
        with open(dataset_path, "r") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Dataset not found: {dataset_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON in dataset")
        sys.exit(1)

    console.print(f"[green]✓[/green] Loaded {len(dataset)} sources")

    # Validate dataset
    collector = DatasetCollector()
    validation = collector.validate_dataset(dataset)
    if not validation["valid"]:
        console.print("[bold red]Dataset validation failed:[/bold red]")
        for error in validation["errors"]:
            console.print(f"  - {error}")
        sys.exit(1)

    if validation["warnings"]:
        console.print("[yellow]Warnings:[/yellow]")
        for warning in validation["warnings"]:
            console.print(f"  - {warning}")

    # Run evaluation
    console.print(f"\n[bold]Running evaluation (threshold={threshold})...[/bold]")
    evaluator = NCIEvaluator()
    
    evaluation_results = evaluator.evaluate_dataset(
        dataset=dataset,
        threshold=threshold,
        save_results=True,
    )

    # Display results summary
    metrics = evaluation_results.get("classification_metrics", {})
    console.print("\n[bold]Evaluation Results:[/bold]")
    console.print(f"  Accuracy:  {metrics.get('accuracy', 0):.1%}")
    console.print(f"  Precision: {metrics.get('precision', 0):.1%}")
    console.print(f"  Recall:    {metrics.get('recall', 0):.1%}")
    console.print(f"  F1-Score:  {metrics.get('f1', 0):.2f}")

    calibration = evaluation_results.get("calibration_metrics", {})
    console.print(f"\n[bold]Calibration:[/bold]")
    console.print(f"  Brier Score: {calibration.get('brier_score', 0):.4f}")
    console.print(f"  ECE:         {calibration.get('expected_calibration_error', 0):.4f}")

    # Generate visualizations if requested
    if generate_vis:
        console.print("\n[bold]Generating visualizations...[/bold]")
        visualizer = EvaluationVisualizer()
        visualizations = visualizer.generate_all_visualizations(evaluation_results)
        console.print(f"[green]✓[/green] {len(visualizations)} visualizations generated")

        # Generate reports
        console.print("\n[bold]Generating reports...[/bold]")
        report_gen = ReportGenerator()
        html_path = report_gen.generate_html_report(evaluation_results, visualizations)
        md_path = report_gen.generate_markdown_report(evaluation_results)
        
        console.print(f"[green]✓[/green] HTML Report: [cyan]{html_path}[/cyan]")
        console.print(f"[green]✓[/green] Markdown Report: [cyan]{md_path}[/cyan]")

    console.print(f"\n[green]✓[/green] Evaluation complete!")


def compare_thresholds(dataset_path: str, thresholds_str: str = None):
    """Compare performance across thresholds."""
    # Load dataset
    console.print(f"\n[bold]Loading dataset from {dataset_path}...[/bold]")
    
    try:
        with open(dataset_path, "r") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Dataset not found: {dataset_path}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Loaded {len(dataset)} sources")

    # Parse thresholds
    if thresholds_str:
        thresholds = [int(t.strip()) for t in thresholds_str.split(",")]
    else:
        thresholds = list(range(3, 16))

    console.print(f"\n[bold]Comparing {len(thresholds)} thresholds: {thresholds}[/bold]")

    # Run evaluations
    evaluator = NCIEvaluator()
    results_by_threshold = {}

    with Progress() as progress:
        task = progress.add_task("[cyan]Evaluating...", total=len(thresholds))
        for threshold in thresholds:
            results = evaluator.evaluate_dataset(
                dataset=dataset,
                threshold=threshold,
                save_results=False,
            )
            metrics = results.get("classification_metrics", {})
            results_by_threshold[threshold] = metrics
            progress.update(task, advance=1)

    # Display comparison
    console.print("\n[bold]Threshold Comparison Results:[/bold]\n")
    
    table_data = []
    for threshold in thresholds:
        metrics = results_by_threshold[threshold]
        table_data.append([
            str(threshold),
            f"{metrics.get('accuracy', 0):.1%}",
            f"{metrics.get('precision', 0):.1%}",
            f"{metrics.get('recall', 0):.1%}",
            f"{metrics.get('f1', 0):.2f}",
        ])

    console.print("[dim]Threshold | Accuracy | Precision | Recall | F1-Score[/dim]")
    console.print("[dim]" + "-" * 60 + "[/dim]")
    for row in table_data:
        console.print(f"{row[0]:9} | {row[1]:8} | {row[2]:9} | {row[3]:6} | {row[4]}")

    # Find best thresholds
    best_f1_threshold = max(thresholds, key=lambda t: results_by_threshold[t].get("f1", 0))
    best_accuracy_threshold = max(thresholds, key=lambda t: results_by_threshold[t].get("accuracy", 0))

    console.print(f"\n[green]✓[/green] Best F1-Score at threshold {best_f1_threshold}")
    console.print(f"[green]✓[/green] Best Accuracy at threshold {best_accuracy_threshold}")

    # Save results
    output_path = EvalConfig.EVAL_OUTPUT_DIR / "threshold_comparison.json"
    with open(output_path, "w") as f:
        json.dump(results_by_threshold, f, indent=2, default=str)
    
    console.print(f"\n[green]✓[/green] Results saved to [cyan]{output_path}[/cyan]")


def generate_report(results_path: str):
    """Generate HTML and markdown reports from evaluation results."""
    console.print(f"\n[bold]Loading results from {results_path}...[/bold]")
    
    try:
        with open(results_path, "r") as f:
            evaluation_results = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Results file not found: {results_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON in results file")
        sys.exit(1)

    # Generate visualizations
    console.print("\n[bold]Generating visualizations...[/bold]")
    visualizer = EvaluationVisualizer()
    visualizations = visualizer.generate_all_visualizations(evaluation_results)

    # Generate reports
    console.print("\n[bold]Generating reports...[/bold]")
    report_gen = ReportGenerator()
    html_path = report_gen.generate_html_report(evaluation_results, visualizations)
    md_path = report_gen.generate_markdown_report(evaluation_results)

    console.print(f"\n[green]✓[/green] Report generation complete!")
    console.print(f"\n[bold]Output files:[/bold]")
    console.print(f"  HTML: [cyan]{html_path}[/cyan]")
    console.print(f"  Markdown: [cyan]{md_path}[/cyan]")

    for name, path in visualizations.items():
        console.print(f"  Chart ({name}): [cyan]{path}[/cyan]")


if __name__ == "__main__":
    main()

