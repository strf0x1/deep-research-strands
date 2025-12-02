"""Tools for expanding and enriching evaluation datasets."""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ManipulationLevel(Enum):
    """Categories for manipulation sophistication."""
    OBVIOUS = "obvious"  # 16-20 score
    SOPHISTICATED = "sophisticated"  # 11-15 score
    SUBTLE = "subtle"  # 6-10 score
    MINIMAL = "minimal"  # 0-5 score


class SourceType(Enum):
    """Types of sources for dataset diversity."""
    SYNTHETIC = "synthetic"
    REAL_NEWS = "real_news"
    FACT_CHECK = "fact_check"
    ACADEMIC = "academic"
    SOCIAL_MEDIA = "social_media"
    PROPAGANDA = "propaganda"


@dataclass
class DatasetGap:
    """Represents a gap in dataset coverage."""
    category: str
    current_count: int
    target_count: int
    priority: str  # "high", "medium", "low"
    examples_needed: int


class DatasetExpander:
    """Expands evaluation datasets with diverse sources."""

    def __init__(self):
        self.target_distribution = {
            ManipulationLevel.OBVIOUS: 50,
            ManipulationLevel.SOPHISTICATED: 75,  # Increase this - currently weak
            ManipulationLevel.SUBTLE: 50,
            ManipulationLevel.MINIMAL: 75,  # More credible sources for calibration
        }

    def analyze_coverage_gaps(self, dataset: List[Dict[str, Any]]) -> List[DatasetGap]:
        """
        Analyze current dataset to identify coverage gaps.

        Args:
            dataset: Current evaluation dataset

        Returns:
            List of identified gaps with priorities
        """
        gaps = []

        # Analyze by NCI score range
        score_distribution = {
            "obvious": 0,  # 16-20
            "sophisticated": 0,  # 11-15
            "subtle": 0,  # 6-10
            "minimal": 0,  # 0-5
        }

        for source in dataset:
            score = source.get("ground_truth_score", 0)
            if score >= 16:
                score_distribution["obvious"] += 1
            elif score >= 11:
                score_distribution["sophisticated"] += 1
            elif score >= 6:
                score_distribution["subtle"] += 1
            else:
                score_distribution["minimal"] += 1

        # Identify gaps
        if score_distribution["sophisticated"] < 20:
            gaps.append(DatasetGap(
                category="sophisticated_manipulation",
                current_count=score_distribution["sophisticated"],
                target_count=75,
                priority="high",
                examples_needed=75 - score_distribution["sophisticated"]
            ))

        if score_distribution["subtle"] < 15:
            gaps.append(DatasetGap(
                category="subtle_borderline",
                current_count=score_distribution["subtle"],
                target_count=50,
                priority="high",
                examples_needed=50 - score_distribution["subtle"]
            ))

        # Analyze topic diversity
        topics = {}
        for source in dataset:
            topic = source.get("metadata", {}).get("topic", "unknown")
            topics[topic] = topics.get(topic, 0) + 1

        # Check for missing topics
        target_topics = [
            "health", "climate", "politics", "economics", "technology",
            "military", "immigration", "elections", "corporate", "science"
        ]

        for topic in target_topics:
            if topics.get(topic, 0) < 10:
                gaps.append(DatasetGap(
                    category=f"topic_{topic}",
                    current_count=topics.get(topic, 0),
                    target_count=10,
                    priority="medium",
                    examples_needed=10 - topics.get(topic, 0)
                ))

        # Check for real-world sources
        real_world_count = sum(1 for s in dataset
                              if s.get("source_dataset", "").startswith("real_"))
        if real_world_count < 100:
            gaps.append(DatasetGap(
                category="real_world_sources",
                current_count=real_world_count,
                target_count=100,
                priority="high",
                examples_needed=100 - real_world_count
            ))

        return sorted(gaps, key=lambda g: (
            {"high": 0, "medium": 1, "low": 2}[g.priority],
            -g.examples_needed
        ))

    def generate_adversarial_examples(self) -> List[Dict[str, Any]]:
        """
        Generate edge cases and adversarial examples for stress testing.

        Returns:
            List of adversarial test cases
        """
        adversarial_examples = []

        # Case 1: Credible source with emotional language (disaster reporting)
        adversarial_examples.append({
            "text": """Earthquake Strikes Coastal Region: Thousands Affected

A devastating 7.2 magnitude earthquake struck the coastal region early Tuesday morning,
resulting in widespread destruction and loss of life. Emergency services report at least
247 confirmed fatalities and over 1,500 injuries.

The earthquake, which occurred at 5:43 AM local time, was centered 15km offshore at a
depth of 12km according to the National Seismological Center. The shaking lasted
approximately 45 seconds and was felt across a 200km radius.

Infrastructure Damage:
- 3,200 buildings collapsed or severely damaged
- Major highway bridge failure blocking rescue access
- Power outages affecting 450,000 residents
- Water treatment facilities compromised in 3 districts

Response Efforts:
International search and rescue teams from 12 countries have arrived to assist local
emergency services. The government has declared a state of emergency and allocated
$500M in immediate disaster relief.

Scientific Context:
Dr. Maria Santos, Chief Seismologist at the Regional Monitoring Center, explained that
this earthquake occurred along the Pacific subduction zone, where tectonic plates
converge. "This region experiences seismic activity regularly, but events of this
magnitude occur approximately once every 30-50 years based on our historical records."

Ongoing Concerns:
Aftershocks continue, with 47 recorded above magnitude 4.0. Residents are advised to
remain in safe locations. Tsunami warnings have been issued for coastal areas, though
initial wave heights are lower than initially feared.

The full extent of casualties and damage is still being assessed as rescue teams access
remote areas. Hospitals are operating at capacity treating the injured.

This report will be updated as new information becomes available.
            """,
            "url": "https://example-news.org/earthquake-disaster-2024",
            "title": "Devastating Earthquake Strikes Coastal Region: Hundreds Dead",
            "ground_truth_label": "credible",
            "ground_truth_score": 3,
            "source_dataset": "adversarial_emotional_credible",
            "metadata": {
                "type": "adversarial_test",
                "challenge": "emotional_language_in_credible_source",
                "characteristics": ["factual", "emotional_appropriate", "evidence_based"],
                "topic": "disaster"
            }
        })

        # Case 2: Technical manipulation - real data, misleading presentation
        adversarial_examples.append({
            "text": """Study Reveals Concerning Rise in Youth Mental Health Issues

A comprehensive analysis of mental health data shows a dramatic 40% increase in
diagnosed anxiety and depression among adolescents over the past five years.

The research, drawing from insurance claims data covering 2.1 million adolescents
aged 13-17, found that diagnosis rates increased from 8.5% in 2018 to 11.9% in 2023.

These findings raise serious questions about the well-being of our youth in an
increasingly digital world.

Key Statistics:
- Anxiety diagnoses: +42% (2018-2023)
- Depression diagnoses: +38% (2018-2023)
- Crisis intervention utilization: +31%

Experts suggest multiple factors may be contributing to this trend, including social
media usage, academic pressure, and reduced in-person social interaction during the
pandemic years.

Dr. Jennifer Wong, a clinical psychologist not involved in the study, notes: "We're
seeing unprecedented levels of mental health challenges in young people. The correlation
with increased screen time and social media use is particularly concerning."

The data suggests an urgent need for expanded mental health resources in schools and
communities to address this growing crisis.
            """,
            "url": "https://example-health-news.com/youth-mental-health-crisis",
            "title": "Youth Mental Health Crisis: 40% Increase in Diagnoses",
            "ground_truth_label": "manipulative",
            "ground_truth_score": 9,
            "source_dataset": "adversarial_technical_manipulation",
            "metadata": {
                "type": "adversarial_test",
                "challenge": "cherry_picked_data_plausible_framing",
                "primary_criteria": ["cherry_picked_data", "missing_information", "framing_techniques"],
                "what_is_hidden": [
                    "Diagnosis increase may reflect increased screening/awareness not actual prevalence",
                    "Telehealth expansion increased access to diagnosis",
                    "Comparison baseline (2018) may be artificially low",
                    "No adjustment for population growth",
                    "Conflation of correlation with causation (social media)"
                ],
                "topic": "mental_health"
            }
        })

        # Case 3: Debunking article that might trigger false positive
        adversarial_examples.append({
            "text": """Fact Check: No, 5G Towers Do Not Cause COVID-19

Claim: 5G cellular towers cause or spread COVID-19
Rating: FALSE

This conspiracy theory has circulated widely on social media, with some posts
accumulating millions of shares. The claim is completely false and scientifically
impossible.

Why This Claim Is Wrong:

1. Different Mechanisms:
   - 5G uses radio waves (electromagnetic radiation)
   - COVID-19 is caused by SARS-CoV-2 virus (biological pathogen)
   - Radio waves cannot create or transmit viruses

2. Geographic Evidence:
   - COVID-19 spread in areas without 5G coverage
   - Countries without 5G infrastructure experienced outbreaks
   - Virus spread follows human contact patterns, not tower locations

3. Scientific Consensus:
   - WHO, FDA, FCC, and international health agencies confirm no connection
   - Peer-reviewed research finds no biological mechanism for such an effect
   - Radio frequency limits are set well below levels that cause any biological harm

Origin of the Myth:
This false claim appears to have originated from misinterpretation of a non-peer-reviewed
paper combined with pre-existing concerns about 5G technology.

Real COVID-19 Transmission:
COVID-19 spreads through respiratory droplets when infected people cough, sneeze, or talk.
The virus has been extensively studied, and its transmission mechanisms are well understood.

If you see this claim, please don't share it. Spreading health misinformation can lead to
real-world harm, including attacks on telecommunications workers and infrastructure.

For accurate COVID-19 information, consult CDC, WHO, or your local health department.
            """,
            "url": "https://example-factcheck.org/5g-covid-false",
            "title": "Debunked: The 5G-COVID-19 Conspiracy Theory",
            "ground_truth_label": "credible",
            "ground_truth_score": 2,
            "source_dataset": "adversarial_debunking_article",
            "metadata": {
                "type": "adversarial_test",
                "challenge": "debunking_article_mentioning_conspiracy",
                "characteristics": ["debunking", "evidence_based", "educational"],
                "topic": "misinformation"
            }
        })

        # Case 4: Satire/Parody
        adversarial_examples.append({
            "text": """BREAKING: Scientists Discover Earth Actually Flat, Just Really Well Lit

In a shocking reversal that will rewrite textbooks worldwide, a team of researchers from
the Institute of Obviously Satirical Studies announced today that Earth is indeed flat,
but sophisticated lighting techniques have fooled humanity for centuries.

"We were as surprised as anyone," said Dr. April Furst, lead researcher. "It turns out
the curvature we've been seeing is just really good CGI from Big Globe."

The team's findings, published in the Journal of Things That Aren't Real, suggest that:
- Gravity is actually just millions of tiny magnets beneath the Earth's flat surface
- The sun is approximately 47 feet across and runs on AAA batteries
- Australia is upside down for aesthetic reasons only
- Pilots are all in on the conspiracy and receive bonus frequent flyer miles for silence

When reached for comment, NASA officials were reportedly "laughing too hard to respond."

The research has been endorsed by the Flat Earth Society, the International Council of
People Who Didn't Read Past The Headline, and several individuals who believe birds
aren't real.

Critics note that this study was released on April 1st and published in a journal that
doesn't exist, but researchers maintain these are just coincidences.
            """,
            "url": "https://example-satire.com/earth-flat-discovery",
            "title": "Scientists Discover Earth Actually Flat, Just Really Well Lit",
            "ground_truth_label": "credible",
            "ground_truth_score": 1,
            "source_dataset": "adversarial_satire",
            "metadata": {
                "type": "adversarial_test",
                "challenge": "obvious_satire_not_manipulation",
                "characteristics": ["satire", "humor", "clearly_absurd"],
                "topic": "satire"
            }
        })

        return adversarial_examples

    def create_borderline_examples(self) -> List[Dict[str, Any]]:
        """
        Create examples in the critical 5-8 score range for threshold tuning.

        Returns:
            List of borderline examples
        """
        borderline_examples = []

        # Borderline case: Advocacy journalism (score ~7)
        borderline_examples.append({
            "text": """Why We Must Act on Climate Change Now

The evidence is clear and overwhelming: climate change represents an existential threat
that demands immediate action.

The Science:
Multiple peer-reviewed studies from IPCC, NOAA, and independent research institutions
confirm global temperatures have risen 1.2°C since pre-industrial times. This warming is
primarily driven by human greenhouse gas emissions.

The Consequences:
We're already seeing devastating impacts: unprecedented wildfires, stronger hurricanes,
coral reef die-offs, and accelerating ice sheet melt. Without action, these impacts will
intensify dramatically.

The Solution:
We must rapidly transition to renewable energy, implement carbon pricing, and invest in
green infrastructure. The technology exists - what's lacking is political will.

The Cost of Inaction:
Economic analyses show climate inaction could cost $500+ trillion in cumulative damages
by 2100. In contrast, aggressive climate action would cost 1-2% of global GDP annually -
a bargain for planetary survival.

The Moral Imperative:
This is fundamentally a moral issue. Future generations will judge us harshly if we fail
to act when we had the knowledge and means to prevent catastrophe.

Some argue economic concerns justify delay. This is short-sighted. The costs of action
pale compared to the costs of inaction, and green technology is creating millions of jobs.

We cannot afford to wait. Every year of delay makes the problem worse and solutions more
expensive. The time for half-measures has passed.

Contact your representatives. Support climate legislation. Make your voice heard. Our
children's future depends on what we do today.
            """,
            "url": "https://example-climate-advocacy.org/act-now",
            "title": "Why We Must Act on Climate Change Now",
            "ground_truth_label": "credible",
            "ground_truth_score": 7,
            "source_dataset": "borderline_advocacy_journalism",
            "metadata": {
                "type": "borderline",
                "characteristics": ["advocacy", "evidence_based", "urgent_framing", "moral_appeal"],
                "topic": "climate",
                "note": "Tests boundary between passionate advocacy and manipulation"
            }
        })

        return borderline_examples

    def save_expanded_dataset(
        self,
        base_dataset: List[Dict[str, Any]],
        output_path: Path,
        include_adversarial: bool = True,
        include_borderline: bool = True
    ):
        """
        Save expanded dataset with additional examples.

        Args:
            base_dataset: Original dataset
            output_path: Where to save expanded dataset
            include_adversarial: Include adversarial examples
            include_borderline: Include borderline examples
        """
        expanded = base_dataset.copy()

        if include_adversarial:
            expanded.extend(self.generate_adversarial_examples())

        if include_borderline:
            expanded.extend(self.create_borderline_examples())

        with open(output_path, 'w') as f:
            json.dump(expanded, f, indent=2)

        print(f"Saved expanded dataset with {len(expanded)} examples to {output_path}")
        print(f"  Original: {len(base_dataset)}")
        print(f"  Adversarial: {len(self.generate_adversarial_examples()) if include_adversarial else 0}")
        print(f"  Borderline: {len(self.create_borderline_examples()) if include_borderline else 0}")


if __name__ == "__main__":
    # Example usage
    expander = DatasetExpander()

    # Load existing dataset
    import json
    from pathlib import Path

    dataset_path = Path("data/eval_datasets/nci_synthetic_demo.json")
    with open(dataset_path) as f:
        dataset = json.load(f)

    # Analyze gaps
    print("Analyzing dataset gaps...")
    gaps = expander.analyze_coverage_gaps(dataset)

    print(f"\nFound {len(gaps)} coverage gaps:")
    for gap in gaps:
        print(f"  - {gap.category}: {gap.current_count}/{gap.target_count} "
              f"(need {gap.examples_needed}, priority: {gap.priority})")

    # Save expanded dataset
    output_path = Path("data/eval_datasets/nci_expanded_demo.json")
    expander.save_expanded_dataset(
        base_dataset=dataset,
        output_path=output_path,
        include_adversarial=True,
        include_borderline=True
    )
