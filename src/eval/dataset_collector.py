"""Dataset collector for NCI evaluation framework."""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import requests
from src.eval.config import EvalConfig


class DatasetCollector:
    """Collect evaluation datasets from fact-checking sources."""

    def __init__(self):
        """Initialize dataset collector."""
        EvalConfig.ensure_directories()
        self.datasets_dir = EvalConfig.EVAL_DATASETS_DIR
        self.manipulative_dir = self.datasets_dir / "manipulative"
        self.credible_dir = self.datasets_dir / "credible"

    def add_source(
        self,
        text: str,
        url: str,
        title: str,
        ground_truth_label: str,
        source_dataset: str,
        ground_truth_score: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a source to the evaluation dataset.

        Args:
            text: Full article/content text
            url: Source URL
            title: Article title
            ground_truth_label: 'manipulative' or 'credible'
            source_dataset: Origin of the data
            ground_truth_score: Expert-assigned score (0-20, optional)
            metadata: Additional context

        Returns:
            Dictionary with the source entry
        """
        if ground_truth_label not in ["manipulative", "credible"]:
            raise ValueError("ground_truth_label must be 'manipulative' or 'credible'")

        entry = {
            "text": text,
            "url": url,
            "title": title,
            "ground_truth_label": ground_truth_label,
            "ground_truth_score": ground_truth_score,
            "source_dataset": source_dataset,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
        }

        return entry

    def save_dataset(self, sources: List[Dict[str, Any]], filename: str = "test_set.json"):
        """
        Save dataset to JSON file.

        Args:
            sources: List of source entries
            filename: Output filename
        """
        output_path = self.datasets_dir / filename
        with open(output_path, "w") as f:
            json.dump(sources, f, indent=2)
        print(f"Saved {len(sources)} sources to {output_path}")
        return output_path

    def load_dataset(self, filename: str = "test_set.json") -> List[Dict[str, Any]]:
        """
        Load dataset from JSON file.

        Args:
            filename: Input filename

        Returns:
            List of source entries
        """
        filepath = self.datasets_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset not found: {filepath}")

        with open(filepath, "r") as f:
            return json.load(f)

    def create_sample_dataset(self) -> List[Dict[str, Any]]:
        """
        Create a sample dataset for testing and demonstration.

        Returns:
            List of sample sources
        """
        samples = [
            # Manipulative examples
            self.add_source(
                text="""
                SHOCKING: Scientists Have Discovered a DEVASTATING Truth About Water!
                
                In an unprecedented discovery that mainstream media is REFUSING to cover, 
                researchers have found that water contains particles that could change EVERYTHING 
                we know about health. This explains why THEY have been keeping this secret from us!
                
                The elite don't want you to know this. They profit from your ignorance. 
                SHARE THIS BEFORE IT'S DELETED!
                """,
                url="https://example.com/shocking-water-truth",
                title="SHOCKING Water Discovery Scientists Don't Want You To Know!",
                ground_truth_label="manipulative",
                source_dataset="synthetic_test",
                ground_truth_score=18,
                metadata={"topic": "pseudoscience", "type": "clickbait"},
            ),
            self.add_source(
                text="""
                BREAKING: New Report Shows Policy X is Either Completely Perfect OR Total Disaster.
                
                According to insiders, there are only two options for Policy X:
                1. It saves everyone and everything is perfect
                2. It destroys civilization as we know it
                
                There is literally no middle ground. You must choose a side NOW. 
                Everyone on social media is choosing side B - are you with them or against them?
                """,
                url="https://example.com/policy-false-choice",
                title="Policy X: The Most Divisive Issue Ever - Pick Your Side",
                ground_truth_label="manipulative",
                source_dataset="synthetic_test",
                ground_truth_score=16,
                metadata={"topic": "politics", "type": "false_dilemma"},
            ),
            self.add_source(
                text="""
                Emotional Appeal Alert: Won't Someone Think of the Children?!
                
                Videos show tears and destruction. We're looping the most emotional footage 
                on every channel. All voices agree this is unprecedented and avoidable.
                
                We're not discussing causes or systemic factors - only the dramatic consequences.
                An expert (who is not an expert in this field) is urging immediate donations 
                and policy changes without time for reflection.
                """,
                url="https://example.com/emotional-campaign",
                title="Heartbreaking: Children in Crisis - Act NOW",
                ground_truth_label="manipulative",
                source_dataset="synthetic_test",
                ground_truth_score=15,
                metadata={"topic": "crisis", "type": "emotional_manipulation"},
            ),
            # Credible examples
            self.add_source(
                text="""
                Water Quality Standards: A Technical Overview
                
                This paper examines current water quality standards established by the EPA.
                
                Methods:
                - Review of EPA regulations from 1970-2024
                - Analysis of 50 major water systems
                - Comparison with international standards
                
                Results:
                Water quality has improved significantly since 1970, with lead levels down 99%.
                However, challenges remain in rural areas.
                
                Conclusion:
                Current standards are based on scientific evidence. We identify specific areas
                needing improvement and recommend targeted regulatory updates based on recent
                epidemiological data.
                """,
                url="https://example.com/water-technical-analysis",
                title="Water Quality Standards: Technical Analysis and Policy Recommendations",
                ground_truth_label="credible",
                source_dataset="synthetic_test",
                ground_truth_score=2,
                metadata={"topic": "water_quality", "type": "technical"},
            ),
            self.add_source(
                text="""
                Policy Analysis: Understanding Complex Trade-offs
                
                Policy X involves genuine trade-offs between different values and outcomes.
                
                Arguments for adoption:
                - Potential environmental benefits (estimated $2B/year)
                - New job creation in specific sectors
                - Alignment with international commitments
                
                Arguments against adoption:
                - Implementation costs ($500M/year over 5 years)
                - Transitional impact on workers in specific regions
                - Uncertainty in long-term outcomes
                
                Discussion:
                Both perspectives have merit based on different priorities. 
                We present the evidence for each view and acknowledge legitimate disagreement.
                The optimal approach depends on value judgments that citizens must make.
                """,
                url="https://example.com/policy-balanced-analysis",
                title="Policy X: Balanced Analysis of Trade-offs and Evidence",
                ground_truth_label="credible",
                source_dataset="synthetic_test",
                ground_truth_score=3,
                metadata={"topic": "policy", "type": "balanced_analysis"},
            ),
            self.add_source(
                text="""
                Scientific Research Study: Novel Findings in Materials Science
                
                Published in Journal of Materials Chemistry
                
                Background:
                Previous research identified limitations in current material properties.
                
                Methods:
                - Controlled laboratory experiments (n=500 samples)
                - Peer review process (2 years)
                - Replication by independent lab
                
                Results:
                Material A showed 23% improvement in metric X (95% CI: 18-28%).
                Effect size was consistent across temperature ranges 5-35°C.
                
                Limitations:
                - Limited to laboratory conditions
                - Scaling to production environments requires further study
                - Long-term durability testing ongoing
                
                Conclusion:
                Preliminary findings are promising but require scaling validation.
                We plan follow-up studies in field conditions.
                """,
                url="https://example.com/journal-research",
                title="Novel Properties of Material A: Controlled Laboratory Study",
                ground_truth_label="credible",
                source_dataset="synthetic_test",
                ground_truth_score=2,
                metadata={"topic": "science", "type": "peer_reviewed"},
            ),
        ]

        return samples

    def save_sample_dataset(self):
        """Create and save sample dataset."""
        samples = self.create_sample_dataset()
        return self.save_dataset(samples, "sample_test_set.json")

    def validate_dataset(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate dataset structure and content.

        Args:
            sources: List of sources to validate

        Returns:
            Validation report
        """
        required_fields = ["text", "url", "title", "ground_truth_label", "source_dataset"]
        errors = []
        warnings = []

        for i, source in enumerate(sources):
            # Check required fields
            for field in required_fields:
                if field not in source:
                    errors.append(f"Source {i}: Missing required field '{field}'")

            # Validate ground_truth_label
            if source.get("ground_truth_label") not in ["manipulative", "credible"]:
                errors.append(f"Source {i}: Invalid ground_truth_label")

            # Check text length
            if len(source.get("text", "")) < 50:
                warnings.append(f"Source {i}: Text is very short")

            # Check ground_truth_score if present
            if "ground_truth_score" in source and source["ground_truth_score"] is not None:
                if not (0 <= source["ground_truth_score"] <= 20):
                    errors.append(f"Source {i}: ground_truth_score must be 0-20")

        return {
            "valid": len(errors) == 0,
            "total_sources": len(sources),
            "errors": errors,
            "warnings": warnings,
        }

