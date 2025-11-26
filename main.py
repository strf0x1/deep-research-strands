#!/usr/bin/env python3
"""
Deep Research Agent CLI (Strands Version)

A command-line interface for conducting deep research using:
- Minimax M2 (via Strands Agents)
- Exa API (neural web search)
- OpenRouter (subagent LLMs)
"""

import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from src.agents.supervisor import SupervisorAgent
from src.utils.config import Config

# Initialize rich console
console = Console()


def print_banner():
    """Print welcome banner with colors."""
    banner_text = Text()
    banner_text.append("DEEP RESEARCH AGENT (STRANDS)", style="bold cyan")
    banner_text.append("\nPowered by ", style="white")
    banner_text.append("OpenRouter (Minimax M2)", style="bold magenta")
    banner_text.append(" & ", style="white")
    banner_text.append("AWS Strands", style="bold green")

    console.print(Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    ))


def run_research(query: str, output_file: str = None, structure_file: str = None):
    """
    Run research for a given query.

    Args:
        query: Research question or topic
        output_file: Optional path to save the report
        structure_file: Optional path to a file containing custom report structure
    """
    try:
        # Load custom structure if provided
        report_structure = None
        if structure_file:
            try:
                with open(structure_file, 'r') as f:
                    report_structure = f.read()
                console.print(f"[dim]Loaded custom report structure from {structure_file}[/dim]")
            except Exception as e:
                console.print(f"[bold red]Error reading structure file:[/bold red] {e}")
                sys.exit(1)

        # Initialize supervisor
        console.print("\n[dim]Initializing Strands Supervisor Agent...[/dim]")
        supervisor = SupervisorAgent(report_structure=report_structure)

        # Conduct research
        result = supervisor.research(query)

        # Display results
        console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
        console.print("[bold yellow] RESEARCH REPORT[/bold yellow]")
        console.print(f"[bold cyan]{'=' * 80}[/bold cyan]")

        # Display markdown-formatted result with colors
        console.print(Markdown(result))
        console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")

        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(result)
                console.print(f"\n[bold green]✓ Report saved to:[/bold green] {output_file}")
            except Exception as e:
                console.print(f"[bold red]Error saving report:[/bold red] {e}")

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Research Agent - Conduct thorough research using Strands Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Research query'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path for the report (e.g., report.md)'
    )

    parser.add_argument(
        '-s', '--structure',
        type=str,
        help='Path to a text file defining custom report structure'
    )

    args = parser.parse_args()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[bold red]✗ Configuration Error:[/bold red] {e}")
        sys.exit(1)

    print_banner()

    if args.query:
        run_research(args.query, args.output, args.structure)
    else:
        # Interactive mode
        while True:
            try:
                query = input("\n🔍 Research Query (or 'exit'): ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                if query:
                    run_research(query)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
