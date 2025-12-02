# NCI Evaluation Datasets

This directory contains datasets for evaluating the NCI (Narrative Credibility Index) scoring system.

## Directory Structure

```
eval_datasets/
├── manipulative/          # Known manipulative sources
├── credible/              # Known credible sources
├── sample_test_set.json   # Example dataset for testing
└── test_set.json         # Combined test dataset with ground truth labels
```

## Dataset Format

Each dataset file should be a JSON array where each entry has the following structure:

```json
{
  "text": "Full article or content text",
  "url": "https://example.com/article",
  "title": "Article title",
  "ground_truth_label": "manipulative",
  "ground_truth_score": 15,
  "source_dataset": "synthetic_test",
  "metadata": {
    "topic": "politics",
    "type": "false_dilemma",
    "date": "2024-01-01"
  },
  "added_at": "2024-01-01T12:00:00"
}
```

### Field Descriptions

- **text** (required): Full content of the source to be analyzed (at least 50 characters)
- **url** (required): URL of the source
- **title** (required): Title or headline of the article
- **ground_truth_label** (required): Either `"manipulative"` or `"credible"`
- **ground_truth_score** (optional): Expert-assigned score from 0-20
  - 0-5: Credible content
  - 6-10: Moderately concerning
  - 11-15: Highly concerning
  - 16-20: Extremely concerning/clearly manipulative
- **source_dataset** (required): Where this source came from (e.g., "snopes", "politifact", "synthetic_test")
- **metadata** (optional): Additional context about the source
- **added_at** (optional): ISO timestamp when added

## Sources and Guidelines

### Manipulative Content Sources

Potential sources for manipulative/disinformation content:

- **Snopes**: https://www.snopes.com
  - Debunked claims and fact checks
  - Clearly marked as "false" or misleading

- **PolitiFact**: https://www.politifact.com
  - False or misleading political claims
  - Range from "Mostly False" to "Pants on Fire"

- **FactCheck.org**: https://www.factcheck.org
  - Debunked claims and false facts

- **NewsGuard**: https://www.newsguardtech.com
  - Low credibility ratings for news sources

### Credible Content Sources

Potential sources for credible content:

- **Academic Papers**
  - Published in peer-reviewed journals
  - Include full methodology and evidence

- **Government Sources**
  - .gov domain websites
  - Official reports and statistics

- **Established News Organizations**
  - News outlets with high credibility ratings
  - Major newspapers and broadcasters

- **Expert Analysis**
  - Academic institutions
  - Reputable research organizations

## Creating Your Own Evaluation Dataset

1. **Collect Sources**: Gather articles and content from known sources
2. **Add Ground Truth Labels**: Classify as "manipulative" or "credible"
3. **Optional Scoring**: Add expert scores from 0-20
4. **Validate**: Run the dataset validator to check format

```python
from src.eval.dataset_collector import DatasetCollector

collector = DatasetCollector()
with open("my_dataset.json") as f:
    dataset = json.load(f)

validation = collector.validate_dataset(dataset)
if validation["valid"]:
    print("Dataset is valid!")
else:
    print("Errors:", validation["errors"])
```

## Sample Dataset

A sample dataset (`sample_test_set.json`) is included with diverse examples of:
- Clearly manipulative content (emotional appeals, false dilemmas, etc.)
- Clearly credible content (balanced analysis, peer-reviewed research, etc.)

Use this for testing the evaluation framework:

```bash
uv run src/eval/cli.py --evaluate --dataset data/eval_datasets/sample_test_set.json
```

## Best Practices

1. **Diversity**: Include sources from various topics and domains
2. **Balance**: Try to include roughly equal numbers of manipulative and credible sources
3. **Transparency**: Document where each source came from
4. **Multiple Reviewers**: Have multiple people label sources for consistency
5. **Metadata**: Include relevant context (date, topic, source type)

## Dataset Size Recommendations

- **Minimum**: 50 sources (25 manipulative, 25 credible) for initial testing
- **Recommended**: 200+ sources for robust evaluation
- **Ideal**: 500+ diverse sources for comprehensive assessment

## Legal and Ethical Considerations

- Respect copyright and fair use when collecting content
- Preserve original URLs and attributions
- Document sources clearly
- Consider sensitivity around manipulative content
- Get permission when necessary

## Contributing Datasets

If you create evaluation datasets, consider sharing them with the community. Contact the project maintainers for guidelines on contributing datasets.

## Tips for Effective Evaluation

1. **Topic Diversity**: Include varied topics (politics, health, science, etc.)
2. **Temporal Range**: Include content from different time periods
3. **Domain Variety**: Mix news, social media, academic, and other sources
4. **Challenge Cases**: Include borderline cases that are hard to classify
5. **Known Outcomes**: Prioritize sources with clear ground truth

## Resources

- [NCI Scoring Criteria Documentation](../../docs/nci-scoring-system.md)
- [Evaluation Guide](../../docs/eval-guide.md)
- [Project README](../../README.md)

---

**Last Updated**: 2024

For questions or contributions, see the project's main README.md

