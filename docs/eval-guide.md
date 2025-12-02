# NCI Evaluation Framework Guide

## Overview

The NCI Evaluation Framework provides tools for rigorously testing and validating the NCI (Narrative Credibility Index) scoring system. It allows you to:

- Collect diverse evaluation datasets
- Run NCI scoring on sources with known ground truth labels
- Calculate comprehensive performance metrics
- Generate detailed evaluation reports
- Compare performance across different thresholds
- Visualize results for transparent assessment

## Quick Start

### 1. Install Dependencies

The evaluation framework requires additional dependencies:

```bash
uv add matplotlib seaborn scikit-learn pandas
```

Or add them directly to your `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "pandas",
]
```

Then sync:

```bash
uv sync
```

### 2. Create Sample Dataset

Start with the included sample dataset to test the framework:

```bash
uv run src/eval/cli.py --create-samples --output sample_data.json
```

This creates a JSON file with diverse examples of manipulative and credible content.

### 3. Run Evaluation

Evaluate the sample dataset:

```bash
uv run src/eval/cli.py --evaluate --dataset sample_data.json --visualizations
```

This will:
- Score each source using NCI
- Calculate classification metrics (accuracy, precision, recall, F1)
- Calculate calibration metrics (Brier score, ECE)
- Generate visualizations (confusion matrix, score distributions, etc.)
- Create HTML and markdown reports

### 4. Review Results

Results are saved to the `eval_output/` directory:

```
eval_output/
├── evaluation_results.json      # Raw metrics and scoring data
├── evaluation_report.html       # Interactive HTML report
├── evaluation_report.md         # Markdown format report
├── confusion_matrix.png
├── score_distributions.png
├── calibration_curve.png
├── criterion_metrics.png
├── metrics_summary.png
└── risk_level_distribution.png
```

Open `evaluation_report.html` in a browser to view the comprehensive report.

## Usage Guide

### CLI Commands

#### Create Sample Dataset

```bash
uv run src/eval/cli.py --create-samples
```

Creates `sample_test_set.json` with diverse examples for testing.

#### Run Full Evaluation

```bash
uv run src/eval/cli.py --evaluate \
  --dataset <path_to_dataset.json> \
  --threshold 6 \
  --visualizations
```

**Options:**
- `--dataset`: Path to input dataset (required)
- `--threshold`: NCI score threshold for classification (default: 6)
- `--visualizations`: Generate charts and reports

#### Compare Multiple Thresholds

```bash
uv run src/eval/cli.py --compare-thresholds \
  --dataset <path_to_dataset.json> \
  --thresholds 3,5,6,8,10
```

Tests multiple threshold values to find optimal settings.

#### Generate Report from Results

```bash
uv run src/eval/cli.py --report \
  --results eval_output/evaluation_results.json
```

Generates HTML and markdown reports from existing results.

### Python API

Use the evaluation framework programmatically:

```python
from src.eval.dataset_collector import DatasetCollector
from src.eval.evaluator import NCIEvaluator
from src.eval.visualizer import EvaluationVisualizer
from src.eval.report_generator import ReportGenerator
import json

# Load or create dataset
collector = DatasetCollector()
with open("my_dataset.json") as f:
    dataset = json.load(f)

# Validate dataset
validation = collector.validate_dataset(dataset)
if not validation["valid"]:
    print("Dataset errors:", validation["errors"])
    exit(1)

# Run evaluation
evaluator = NCIEvaluator()
results = evaluator.evaluate_dataset(dataset, threshold=6)

# Generate visualizations
visualizer = EvaluationVisualizer()
visualizations = visualizer.generate_all_visualizations(results)

# Generate reports
report_gen = ReportGenerator()
html_path = report_gen.generate_html_report(results, visualizations)
md_path = report_gen.generate_markdown_report(results)

print(f"Report saved to {html_path}")
```

## Metrics Explained

### Classification Metrics

These measure how well NCI distinguishes manipulative from credible sources using a score threshold:

- **Accuracy**: Percentage of sources correctly classified
  - Formula: `(TP + TN) / Total`
  - Interpretation: Overall correctness
  - Target: Higher is better

- **Precision**: When flagged as manipulative, how often correct
  - Formula: `TP / (TP + FP)`
  - Interpretation: False alarm rate
  - Target: Higher reduces false alarms

- **Recall**: Of truly manipulative sources, how many detected
  - Formula: `TP / (TP + FN)`
  - Interpretation: Detection rate
  - Target: Higher catches more manipulation

- **F1-Score**: Harmonic mean of precision and recall
  - Formula: `2 * (Precision * Recall) / (Precision + Recall)`
  - Interpretation: Balance between precision and recall
  - Target: Higher is generally better

### Confusion Matrix

Shows classification results:

```
                 Predicted
               Credible | Manipulative
True: Credible    TN      |      FP
      Manipulative FN      |      TP
```

- **TP (True Positives)**: Correctly flagged as manipulative
- **TN (True Negatives)**: Correctly identified as credible
- **FP (False Positives)**: Credible mislabeled as manipulative
- **FN (False Negatives)**: Manipulative sources missed

### Calibration Metrics

These measure whether predicted NCI scores align with actual manipulation rates:

- **Brier Score**: Mean squared error of predictions
  - Formula: `Mean((predicted - actual)²)`
  - Range: 0 to 1
  - Target: Lower is better (0 = perfect)

- **Expected Calibration Error (ECE)**: Average difference between confidence and accuracy
  - Measures if score of 0.7 means 70% of sources are actually manipulative
  - Range: 0 to 1
  - Target: Lower is better (0 = perfect calibration)

- **Max Calibration Error (MCE)**: Worst-case calibration error
  - Identifies largest discrepancy
  - Target: Lower is better

### Per-Criterion Metrics

Shows performance of individual NCI criteria:

- Which criteria most effectively identify manipulation
- Which criteria have high false positive rates
- Helps identify strengths and weaknesses in the system

## Dataset Management

### Creating Custom Datasets

1. Collect sources from known fact-checking sites:
   - Snopes, PolitiFact, FactCheck.org for manipulative content
   - Academic papers, government sources for credible content

2. Create JSON file with ground truth labels:

```json
[
  {
    "text": "Full article text...",
    "url": "https://example.com/article",
    "title": "Article Title",
    "ground_truth_label": "manipulative",
    "ground_truth_score": 15,
    "source_dataset": "snopes",
    "metadata": {"topic": "politics"}
  },
  ...
]
```

3. Validate with the collector:

```python
from src.eval.dataset_collector import DatasetCollector

collector = DatasetCollector()
validation = collector.validate_dataset(dataset)
```

### Dataset Guidelines

- **Size**: Start with 50+ sources, aim for 200-500 for robust results
- **Balance**: Include roughly equal manipulative and credible sources
- **Diversity**: Cover multiple topics and time periods
- **Quality**: Use sources with clear ground truth labels
- **Documentation**: Record where each source came from

See [eval_datasets/README.md](../data/eval_datasets/README.md) for more details.

## Interpreting Results

### Good Performance Indicators

- **High Accuracy (>80%)**: System correctly classifies most sources
- **High Precision & Recall (>75%)**: System is both sensitive and specific
- **Good Calibration (ECE <0.1)**: Scores align with actual outcomes
- **Clear Score Separation**: Manipulative and credible sources have different mean scores
- **Criterion Variety**: Multiple criteria effectively predict manipulation

### Warning Signs

- **Low Accuracy (<60%)**: System needs tuning or better features
- **High False Positive Rate**: Conservative, may miss legitimate content concerns
- **High False Negative Rate**: System misses actual manipulation
- **Poor Calibration (ECE >0.2)**: Scores don't reflect actual risk
- **Unbalanced Metrics**: Large gap between precision and recall
- **Few Relevant Criteria**: Only a few criteria drive predictions

### Threshold Selection

The default threshold is 6. Choose based on your use case:

- **Lower threshold (3-5)**: More sensitive, catches more manipulation but more false alarms
- **Default (6)**: Balanced approach
- **Higher threshold (8-10)**: More conservative, fewer false alarms but may miss manipulation

Use `--compare-thresholds` to find optimal value for your dataset.

## Advanced Usage

### Comparing Multiple Datasets

```python
evaluator = NCIEvaluator()

for dataset_name in ["dataset1.json", "dataset2.json"]:
    with open(f"data/{dataset_name}") as f:
        dataset = json.load(f)
    
    results = evaluator.evaluate_dataset(dataset)
    print(f"{dataset_name}: Accuracy = {results['classification_metrics']['accuracy']:.1%}")
```

### Finding Misclassifications

```python
# Find false positives (credible mislabeled as manipulative)
false_positives = evaluator.find_misclassifications(
    results, 
    label_type="false_positive", 
    limit=10
)

for fp in false_positives:
    print(f"URL: {fp['url']}")
    print(f"Predicted Score: {fp['predicted_score']}")
    print(f"Ground Truth: {fp['ground_truth_label']}")
    print()
```

### Custom Metrics

The framework is extensible. Add custom metrics in `src/eval/metrics.py`:

```python
@staticmethod
def custom_metric(results):
    """Your custom metric calculation."""
    # Your logic here
    return metric_value
```

## Troubleshooting

### Issue: "NCI scoring error"

**Cause**: API call failed or invalid API key

**Solution**:
1. Check `OPENROUTER_API_KEY` is set in `.env`
2. Verify API key has credits
3. Check network connectivity
4. See `evaluation_results.json` for detailed error messages

### Issue: "Text too short to score"

**Cause**: Source text is less than 50 characters

**Solution**:
- Ensure dataset sources have sufficient content
- NCI requires enough text to analyze manipulation tactics

### Issue: Low performance metrics

**Cause**: Could be dataset quality, threshold issues, or system limitations

**Solution**:
1. Verify ground truth labels are correct
2. Try different thresholds with `--compare-thresholds`
3. Check if dataset is representative
4. Review misclassifications with `find_misclassifications()`
5. Analyze per-criterion metrics to identify weak areas

### Issue: Visualizations not generating

**Cause**: Missing dependencies or file permissions

**Solution**:
```bash
# Ensure matplotlib/seaborn installed
uv sync

# Check write permissions to eval_output/
ls -la eval_output/
```

## Best Practices

1. **Start Small**: Test with sample dataset before large evaluations
2. **Validate First**: Always validate dataset before evaluation
3. **Document Everything**: Record dataset sources and labeling process
4. **Test Multiple Thresholds**: Don't assume default threshold is optimal
5. **Review Misclassifications**: Understand where system fails
6. **Iterate**: Use feedback to improve dataset or system
7. **Be Transparent**: Document all assumptions and limitations
8. **Save Results**: Keep historical results for comparison

## Integration with Research Reports

Use NCI evaluation results to improve research report transparency:

```python
from src.eval.evaluator import NCIEvaluator

# Generate credibility report for your research
evaluator = NCIEvaluator()

# Evaluate sources used in research
research_sources = [
    {"text": source_text, "url": url, ...}
]

results = evaluator.evaluate_dataset(research_sources)

# Include NCI analysis in report
print(f"Source Credibility Assessment:")
print(f"  Average NCI Score: {results['score_distribution']['overall']['mean']:.1f}/20")
print(f"  Risk Level Distribution: ...")
```

## References

- [NCI Scoring Criteria](nci-scoring-system.md)
- [Main README](../README.md)
- [Dataset Documentation](../data/eval_datasets/README.md)

## Questions & Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the example code in this guide
3. See the sample dataset for format examples
4. Check evaluation_results.json for detailed error messages
5. Open an issue on the project repository

---

**Last Updated**: 2024

For the latest information, refer to the project repository and documentation.

