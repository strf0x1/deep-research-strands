"""Report generator for NCI evaluation results."""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from src.eval.config import EvalConfig


class ReportGenerator:
    """Generate comprehensive evaluation reports."""

    def __init__(self):
        """Initialize report generator."""
        EvalConfig.ensure_directories()
        self.output_dir = EvalConfig.EVAL_OUTPUT_DIR

    def generate_html_report(
        self,
        evaluation_results: Dict[str, Any],
        visualizations: Dict[str, Path],
        filename: str = "evaluation_report.html",
    ) -> Path:
        """
        Generate comprehensive HTML evaluation report.

        Args:
            evaluation_results: Results from evaluator
            visualizations: Dictionary of visualization paths
            filename: Output filename

        Returns:
            Path to saved report
        """
        metrics = evaluation_results.get("classification_metrics", {})
        calibration = evaluation_results.get("calibration_metrics", {})
        criterion_metrics = evaluation_results.get("criterion_metrics", [])
        score_dist = evaluation_results.get("score_distribution", {})
        metadata = evaluation_results.get("metadata", {})

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{EvalConfig.REPORT_TITLE}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .metric {{
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2980b9;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        table th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        table tr:hover {{
            background-color: #f5f5f5;
        }}
        .positive {{
            color: #27ae60;
            font-weight: bold;
        }}
        .negative {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .success {{
            background-color: #d4edda;
            border: 1px solid #28a745;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .info {{
            background-color: #d1ecf1;
            border: 1px solid #17a2b8;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 {EvalConfig.REPORT_TITLE}</h1>

        <div class="info">
            <strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Dataset Size:</strong> {metadata.get('total_sources', 0)} sources<br>
            <strong>Successfully Scored:</strong> {metadata.get('successfully_scored', 0)} sources<br>
            <strong>Classification Threshold:</strong> {metadata.get('threshold', 6)}
        </div>

        <!-- Executive Summary -->
        <h2>Executive Summary</h2>
        <p>
            This report presents the evaluation results of the NCI (Narrative Credibility Index) 
            scoring system. The NCI is designed to detect narrative manipulation and psyop 
            campaigns using 20 criteria that identify common manipulation tactics.
        </p>
        <p>
            The evaluation compares NCI scores to ground truth labels for {metadata.get('total_sources', 0)} 
            source materials. Results show how well the NCI system can distinguish between 
            credible and manipulative sources.
        </p>

        <!-- Key Metrics -->
        <h2>Key Performance Metrics</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">Accuracy</div>
                <div class="metric-value {self._get_metric_class(metrics.get('accuracy', 0))}">
                    {metrics.get('accuracy', 0):.1%}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Precision</div>
                <div class="metric-value {self._get_metric_class(metrics.get('precision', 0))}">
                    {metrics.get('precision', 0):.1%}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Recall</div>
                <div class="metric-value {self._get_metric_class(metrics.get('recall', 0))}">
                    {metrics.get('recall', 0):.1%}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">F1-Score</div>
                <div class="metric-value {self._get_metric_class(metrics.get('f1', 0))}">
                    {metrics.get('f1', 0):.2f}
                </div>
            </div>
        </div>

        <!-- Classification Metrics Details -->
        <h2>Classification Performance</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Interpretation</th>
            </tr>
            <tr>
                <td>True Positives (TP)</td>
                <td><span class="positive">{metrics.get('true_positives', 0)}</span></td>
                <td>Correctly identified as manipulative</td>
            </tr>
            <tr>
                <td>True Negatives (TN)</td>
                <td><span class="positive">{metrics.get('true_negatives', 0)}</span></td>
                <td>Correctly identified as credible</td>
            </tr>
            <tr>
                <td>False Positives (FP)</td>
                <td><span class="negative">{metrics.get('false_positives', 0)}</span></td>
                <td>Credible sources incorrectly flagged as manipulative</td>
            </tr>
            <tr>
                <td>False Negatives (FN)</td>
                <td><span class="negative">{metrics.get('false_negatives', 0)}</span></td>
                <td>Manipulative sources missed</td>
            </tr>
            <tr>
                <td>Accuracy</td>
                <td colspan="2">{metrics.get('accuracy', 0):.1%} - Overall correctness</td>
            </tr>
            <tr>
                <td>Precision</td>
                <td colspan="2">{metrics.get('precision', 0):.1%} - When flagged as manipulative, how often correct</td>
            </tr>
            <tr>
                <td>Recall</td>
                <td colspan="2">{metrics.get('recall', 0):.1%} - Of truly manipulative sources, how many detected</td>
            </tr>
        </table>

        <!-- Calibration Metrics -->
        <h2>Calibration Analysis</h2>
        <p>
            Calibration metrics measure how well the predicted NCI scores align with actual 
            manipulation rates. Good calibration means the system's confidence levels are 
            well-matched to actual performance.
        </p>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">Brier Score</div>
                <div class="metric-value">{calibration.get('brier_score', 0):.4f}</div>
                <p style="font-size: 0.8em; color: #7f8c8d;">Lower is better (0 = perfect)</p>
            </div>
            <div class="metric">
                <div class="metric-label">ECE (Expected Calibration Error)</div>
                <div class="metric-value">{calibration.get('expected_calibration_error', 0):.4f}</div>
                <p style="font-size: 0.8em; color: #7f8c8d;">Lower is better (0 = perfect)</p>
            </div>
            <div class="metric">
                <div class="metric-label">MCE (Max Calibration Error)</div>
                <div class="metric-value">{calibration.get('max_calibration_error', 0):.4f}</div>
                <p style="font-size: 0.8em; color: #7f8c8d;">Lower is better (0 = perfect)</p>
            </div>
        </div>

        <!-- Score Distribution -->
        <h2>Score Distribution Analysis</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Mean</th>
                <th>Median</th>
                <th>Std Dev</th>
                <th>Min</th>
                <th>Max</th>
                <th>Count</th>
            </tr>
            <tr>
                <td><strong>Manipulative Sources</strong></td>
                <td>{score_dist.get('manipulative', {}).get('mean', 0):.2f}</td>
                <td>{score_dist.get('manipulative', {}).get('median', 0):.2f}</td>
                <td>{score_dist.get('manipulative', {}).get('std', 0):.2f}</td>
                <td>{score_dist.get('manipulative', {}).get('min', 0)}</td>
                <td>{score_dist.get('manipulative', {}).get('max', 0)}</td>
                <td>{score_dist.get('manipulative', {}).get('count', 0)}</td>
            </tr>
            <tr>
                <td><strong>Credible Sources</strong></td>
                <td>{score_dist.get('credible', {}).get('mean', 0):.2f}</td>
                <td>{score_dist.get('credible', {}).get('median', 0):.2f}</td>
                <td>{score_dist.get('credible', {}).get('std', 0):.2f}</td>
                <td>{score_dist.get('credible', {}).get('min', 0)}</td>
                <td>{score_dist.get('credible', {}).get('max', 0)}</td>
                <td>{score_dist.get('credible', {}).get('count', 0)}</td>
            </tr>
        </table>

        <!-- Criterion Performance -->
        <h2>Per-Criterion Performance</h2>
        <p>This section shows which individual NCI criteria are most predictive.</p>
        <table>
            <tr>
                <th>Criterion</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>Support</th>
            </tr>
            {self._generate_criterion_rows(criterion_metrics)}
        </table>

        <!-- Visualizations -->
        <h2>Visualizations</h2>
        
        {self._generate_chart_html(visualizations, 'metrics_summary', 'Metrics Summary')}
        {self._generate_chart_html(visualizations, 'confusion_matrix', 'Confusion Matrix')}
        {self._generate_chart_html(visualizations, 'score_distributions', 'Score Distribution')}
        {self._generate_chart_html(visualizations, 'calibration_curve', 'Calibration Curve')}
        {self._generate_chart_html(visualizations, 'criterion_metrics', 'Per-Criterion Performance')}
        {self._generate_chart_html(visualizations, 'risk_level_distribution', 'Risk Level Distribution')}

        <!-- Interpretation and Recommendations -->
        <h2>Interpretation & Recommendations</h2>
        
        {self._generate_interpretation(metrics, calibration, metadata)}

        <!-- Methodology -->
        <h2>Methodology</h2>
        <h3>NCI Scoring System</h3>
        <p>
            The NCI (Narrative Credibility Index) uses 20 criteria to detect manipulation tactics:
        </p>
        <ol>
            <li>Timing - Serendipitous or coincidental timing</li>
            <li>Emotional Manipulation - Provokes emotion without evidence</li>
            <li>Uniform Messaging - Repeated phrases across media</li>
            <li>Missing Information - Alternative views excluded</li>
            <li>Simplistic Narratives - "Good vs. evil" framing</li>
            <li>Tribal Division - "Us vs. them" dynamic</li>
            <li>Authority Overload - Questionable experts</li>
            <li>Call for Urgent Action - Pressure for immediate decisions</li>
            <li>Overuse of Novelty - Event framed as shocking</li>
            <li>Financial/Political Gain - Powerful groups benefit</li>
            <li>Suppression of Dissent - Critics silenced</li>
            <li>False Dilemmas - Only two extreme options</li>
            <li>Bandwagon Effect - Pressure to conform</li>
            <li>Emotional Repetition - Same triggers repeated</li>
            <li>Cherry-Picked Data - Statistics out of context</li>
            <li>Logical Fallacies - Flawed arguments</li>
            <li>Manufactured Outrage - Outrage seems sudden</li>
            <li>Framing Techniques - Story shaped for perception</li>
            <li>Rapid Behavior Shifts - Groups adopt symbols</li>
            <li>Historical Parallels - Mirrors past manipulation</li>
        </ol>

        <h3>Evaluation Approach</h3>
        <p>
            This evaluation compares NCI scores against ground truth labels for a diverse 
            dataset of sources. Binary classification is performed using a score threshold 
            of {metadata.get('threshold', 6)} (scores ≥ threshold are classified as manipulative).
        </p>
        <p>
            Key metrics calculated:
        </p>
        <ul>
            <li><strong>Classification Metrics:</strong> Precision, Recall, F1-Score, Accuracy</li>
            <li><strong>Calibration Metrics:</strong> Brier Score, Expected Calibration Error</li>
            <li><strong>Per-Criterion Analysis:</strong> Which NCI criteria are most predictive</li>
            <li><strong>Score Distribution:</strong> How scores separate manipulative vs credible</li>
        </ul>

        <!-- Limitations and Caveats -->
        <h2>Limitations & Caveats</h2>
        <div class="warning">
            <strong>⚠️ Important Limitations:</strong>
            <ul>
                <li>NCI scores should be used as <em>one input</em> among many, not as sole determinant</li>
                <li>Ground truth labels are subject to annotator bias and may not be perfect</li>
                <li>Small sample size in initial evaluation - results may not generalize</li>
                <li>NCI criteria may have varying applicability across different topics</li>
                <li>The system may be calibrated to the specific dataset used</li>
                <li>Real-world manipulation tactics evolve; new patterns may not be detected</li>
            </ul>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>NCI Evaluation Framework - For transparency and objective evaluation of narrative credibility analysis</p>
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
    </div>
</body>
</html>
"""

        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            f.write(html_content)

        print(f"HTML report saved to {output_path}")
        return output_path

    def generate_markdown_report(
        self,
        evaluation_results: Dict[str, Any],
        filename: str = "evaluation_report.md",
    ) -> Path:
        """
        Generate markdown format evaluation report.

        Args:
            evaluation_results: Results from evaluator
            filename: Output filename

        Returns:
            Path to saved report
        """
        metrics = evaluation_results.get("classification_metrics", {})
        calibration = evaluation_results.get("calibration_metrics", {})
        criterion_metrics = evaluation_results.get("criterion_metrics", [])
        score_dist = evaluation_results.get("score_distribution", {})
        metadata = evaluation_results.get("metadata", {})

        md_content = f"""# NCI Scoring System Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report presents evaluation results for the NCI (Narrative Credibility Index) scoring system, 
which detects narrative manipulation and psyop campaigns using 20 criteria.

- **Total Sources Evaluated:** {metadata.get('total_sources', 0)}
- **Successfully Scored:** {metadata.get('successfully_scored', 0)}
- **Classification Threshold:** {metadata.get('threshold', 6)}

## Key Performance Metrics

### Classification Performance

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| **Accuracy** | {metrics.get('accuracy', 0):.1%} | Overall correctness |
| **Precision** | {metrics.get('precision', 0):.1%} | When flagged as manipulative, how often correct |
| **Recall** | {metrics.get('recall', 0):.1%} | Of truly manipulative sources, how many detected |
| **F1-Score** | {metrics.get('f1', 0):.2f} | Harmonic mean of precision and recall |

### Confusion Matrix

```
                  Predicted
                 Credible | Manipulative
True:  Credible     {metrics.get('true_negatives', 0):3d}    |    {metrics.get('false_positives', 0):3d}
       Manipulative  {metrics.get('false_negatives', 0):3d}    |    {metrics.get('true_positives', 0):3d}
```

### Calibration Metrics

| Metric | Value |
|--------|-------|
| Brier Score | {calibration.get('brier_score', 0):.4f} (lower is better) |
| Expected Calibration Error (ECE) | {calibration.get('expected_calibration_error', 0):.4f} |
| Max Calibration Error (MCE) | {calibration.get('max_calibration_error', 0):.4f} |

## Score Distribution Analysis

### Manipulative Sources
- **Mean Score:** {score_dist.get('manipulative', {}).get('mean', 0):.2f}
- **Median:** {score_dist.get('manipulative', {}).get('median', 0):.2f}
- **Std Dev:** {score_dist.get('manipulative', {}).get('std', 0):.2f}
- **Range:** {score_dist.get('manipulative', {}).get('min', 0)} - {score_dist.get('manipulative', {}).get('max', 0)}
- **Count:** {score_dist.get('manipulative', {}).get('count', 0)}

### Credible Sources
- **Mean Score:** {score_dist.get('credible', {}).get('mean', 0):.2f}
- **Median:** {score_dist.get('credible', {}).get('median', 0):.2f}
- **Std Dev:** {score_dist.get('credible', {}).get('std', 0):.2f}
- **Range:** {score_dist.get('credible', {}).get('min', 0)} - {score_dist.get('credible', {}).get('max', 0)}
- **Count:** {score_dist.get('credible', {}).get('count', 0)}

## Per-Criterion Performance

| Criterion | Precision | Recall | F1-Score | Support |
|-----------|-----------|--------|----------|---------|
{self._generate_criterion_markdown(criterion_metrics)}

## Interpretation & Recommendations

{self._generate_interpretation_markdown(metrics, calibration, metadata)}

## Methodology

### NCI Scoring Criteria (20 Total)

1. **Timing** - Serendipitous or coincidental with other events
2. **Emotional Manipulation** - Provokes fear, outrage, or guilt without solid evidence
3. **Uniform Messaging** - Key phrases or ideas repeated across media
4. **Missing Information** - Alternative views or critical details excluded
5. **Simplistic Narratives** - Story reduced to "good vs. evil" frameworks
6. **Tribal Division** - Creates an "us vs. them" dynamic
7. **Authority Overload** - Questionable "experts" driving the narrative
8. **Call for Urgent Action** - Demands immediate decisions without reflection
9. **Overuse of Novelty** - Event framed as shocking or unprecedented
10. **Financial/Political Gain** - Do powerful groups benefit disproportionately?
11. **Suppression of Dissent** - Critics silenced or labeled negatively
12. **False Dilemmas** - Only two extreme options presented
13. **Bandwagon Effect** - Pressure to conform because "everyone is doing it"
14. **Emotional Repetition** - Same emotional triggers repeated excessively
15. **Cherry-Picked Data** - Statistics presented selectively or out of context
16. **Logical Fallacies** - Flawed arguments used to dismiss critics
17. **Manufactured Outrage** - Outrage seems sudden or disconnected from facts
18. **Framing Techniques** - Story shaped to control perception
19. **Rapid Behavior Shifts** - Groups adopting symbols or actions unexpectedly
20. **Historical Parallels** - Story mirrors manipulative past events

### Evaluation Approach

Binary classification compares NCI scores against ground truth labels using a threshold of 
{metadata.get('threshold', 6)} (scores ≥ threshold classified as manipulative).

## Limitations & Caveats

⚠️ **Important:**

- NCI scores should be used as **one input among many**, not as sole determinant
- Ground truth labels are subject to annotator bias and may not be perfect
- Small sample size in initial evaluation - results may not fully generalize
- NCI criteria may have varying applicability across different topics
- The system may be calibrated specifically to this dataset
- Real-world manipulation tactics evolve; new patterns may not be detected yet

## Recommendations

1. **Use as Complementary Tool:** Combine NCI scores with other credibility indicators
2. **Consider Context:** Evaluate content within broader context of the research topic
3. **Monitor Threshold:** Consider different thresholds based on use case
4. **Regular Re-evaluation:** Periodically test system on new datasets
5. **Multi-expert Consensus:** Use expert review for borderline cases
6. **Transparency:** Always disclose use of NCI scoring in reports

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d at %H:%M:%S UTC')}

For more information, see the evaluation framework documentation.
"""

        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            f.write(md_content)

        print(f"Markdown report saved to {output_path}")
        return output_path

    def _get_metric_class(self, value: float) -> str:
        """Get CSS class for metric value."""
        if value >= 0.8:
            return "positive"
        elif value >= 0.6:
            return "warning"
        else:
            return "negative"

    def _generate_criterion_rows(self, criterion_metrics: List[Dict]) -> str:
        """Generate HTML table rows for criterion metrics."""
        rows = []
        for metric in criterion_metrics:
            rows.append(f"""
            <tr>
                <td>{metric.get('criterion', '').replace('_', ' ').title()}</td>
                <td>{metric.get('precision', 0):.2f}</td>
                <td>{metric.get('recall', 0):.2f}</td>
                <td>{metric.get('f1', 0):.2f}</td>
                <td>{metric.get('support', 0)}</td>
            </tr>
            """)
        return "\n".join(rows)

    def _generate_criterion_markdown(self, criterion_metrics: List[Dict]) -> str:
        """Generate markdown table rows for criterion metrics."""
        rows = []
        for metric in criterion_metrics:
            rows.append(
                f"| {metric.get('criterion', '').replace('_', ' ').title()} | "
                f"{metric.get('precision', 0):.2f} | "
                f"{metric.get('recall', 0):.2f} | "
                f"{metric.get('f1', 0):.2f} | "
                f"{metric.get('support', 0)} |"
            )
        return "\n".join(rows)

    def _generate_chart_html(self, visualizations: Dict[str, Path], key: str, title: str) -> str:
        """Generate HTML for a chart."""
        if key not in visualizations:
            return ""
        
        chart_path = visualizations[key]
        # Convert to relative path if in output dir
        try:
            rel_path = chart_path.relative_to(self.output_dir)
        except ValueError:
            rel_path = chart_path

        return f"""
        <h3>{title}</h3>
        <div class="chart-container">
            <img src="{rel_path}" alt="{title}">
        </div>
        """

    def _generate_interpretation(
        self,
        metrics: Dict[str, Any],
        calibration: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate interpretation section."""
        accuracy = metrics.get("accuracy", 0)
        precision = metrics.get("precision", 0)
        recall = metrics.get("recall", 0)

        interpretation = "<ul>"

        if accuracy >= 0.8:
            interpretation += "<li class='positive'>✓ High accuracy indicates the system generally performs well</li>"
        elif accuracy >= 0.6:
            interpretation += "<li>⚠ Moderate accuracy suggests room for improvement</li>"
        else:
            interpretation += "<li class='negative'>✗ Low accuracy indicates the system needs tuning</li>"

        if precision >= recall:
            interpretation += f"<li>The system has higher precision ({precision:.1%}) than recall ({recall:.1%}), " \
                            "meaning it's conservative in flagging manipulative content (fewer false alarms)</li>"
        else:
            interpretation += f"<li>The system has higher recall ({recall:.1%}) than precision ({precision:.1%}), " \
                            "meaning it detects more manipulative content but with more false positives</li>"

        ece = calibration.get("expected_calibration_error", 1.0)
        if ece < 0.1:
            interpretation += "<li class='positive'>✓ Excellent calibration: NCI scores are well-aligned with actual outcomes</li>"
        elif ece < 0.2:
            interpretation += "<li>⚠ Good calibration with minor discrepancies</li>"
        else:
            interpretation += "<li class='negative'>✗ Calibration issues: Scores may not reflect actual manipulation risk accurately</li>"

        interpretation += "</ul>"

        return interpretation

    def _generate_interpretation_markdown(
        self,
        metrics: Dict[str, Any],
        calibration: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate markdown interpretation section."""
        accuracy = metrics.get("accuracy", 0)
        precision = metrics.get("precision", 0)
        recall = metrics.get("recall", 0)
        ece = calibration.get("expected_calibration_error", 1.0)

        lines = []

        if accuracy >= 0.8:
            lines.append("- **✓ High accuracy:** The system performs well overall")
        elif accuracy >= 0.6:
            lines.append("- **⚠ Moderate accuracy:** Performance is reasonable but could be improved")
        else:
            lines.append("- **✗ Low accuracy:** The system needs tuning or adjustment")

        if precision >= recall:
            lines.append(f"- **Conservative classifier:** Precision ({precision:.1%}) > Recall ({recall:.1%}) means fewer false alarms but may miss some manipulation")
        else:
            lines.append(f"- **Sensitive classifier:** Recall ({recall:.1%}) > Precision ({precision:.1%}) means better at detecting manipulation but more false positives")

        if ece < 0.1:
            lines.append("- **✓ Excellent calibration:** NCI scores align well with actual manipulation rates")
        elif ece < 0.2:
            lines.append("- **⚠ Good calibration:** Minor discrepancies between predicted confidence and actual outcomes")
        else:
            lines.append("- **✗ Calibration issues:** Scores may not reliably reflect actual manipulation risk")

        return "\n".join(lines)

