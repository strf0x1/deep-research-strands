"""NCI (Narrative Credibility Index) Scoring Tool for detecting psyop campaigns."""

import json
from typing import Dict, Any, List, Optional
from strands import Agent
from strands.models.openai import OpenAIModel
from pydantic import BaseModel, Field
from src.utils.config import Config


class NCIScoreData(BaseModel):
    """Pydantic model for NCI scoring output."""
    criteria_scores: Dict[str, Dict[str, Any]] = Field(description="Scores for each NCI criterion")
    aggregate_score: int = Field(description="Total score from 0-20")
    risk_level: str = Field(description="Risk level: LOW, MODERATE, HIGH, or CRITICAL")
    summary: str = Field(description="Brief summary of key manipulation tactics")


class NCIScoringTool:
    """
    Tool that scores source materials and synthesized findings against
    the NCI (Narrative Credibility Index) criteria to detect potential
    psyop campaigns and coordinated narrative manipulation.
    Uses Strands Agents for inference instead of raw HTTP calls.
    """

    def __init__(self):
        """Initialize NCI Scoring Tool with Strands Agent."""
        # Initialize model using Strands OpenAI provider
        self.model = OpenAIModel(
            client_args={
                "api_key": Config.OPENROUTER_API_KEY,
                "base_url": Config.OPENROUTER_BASE_URL,
            },
            model_id=Config.OPENROUTER_MODEL,
            params={
                "temperature": 0.3,  # Lower temp for more consistent scoring
                "max_tokens": 2000,
            }
        )

        self.system_prompt = """You are an expert analyst specializing in detecting narrative manipulation and psyop campaigns using the Narrative Credibility Index (NCI) methodology.

## NCI Scoring Criteria (20 total indicators)

Score a text for each criterion where it applies. A match indicates the presence of that manipulation tactic.

|| # | Criterion | Description |
||---|-----------|-------------|
|| 1 | Timing | Does the timing feel serendipitous or coincidental with other events? |
|| 2 | Emotional Manipulation | Does it provoke fear, outrage, or guilt without solid evidence? |
|| 3 | Uniform Messaging | Are key phrases or ideas repeated across media? |
|| 4 | Missing Information | Are alternative views or critical details excluded? |
|| 5 | Simplistic Narratives | Is the story reduced to "good vs. evil" frameworks? |
|| 6 | Tribal Division | Does it create an "us vs. them" dynamic? |
|| 7 | Authority Overload | Are questionable "experts" driving the narrative? |
|| 8 | Call for Urgent Action | Does it demand immediate decisions without reflection? |
|| 9 | Overuse of Novelty | Is the event framed as shocking or unprecedented? |
|| 10 | Financial/Political Gain | Do powerful groups benefit disproportionately? |
|| 11 | Suppression of Dissent | Are critics silenced or labeled negatively? |
|| 12 | False Dilemmas | Are only two extreme options presented? |
|| 13 | Bandwagon Effect | Is there pressure to conform because "everyone is doing it"? |
|| 14 | Emotional Repetition | Are the same emotional triggers repeated excessively? |
|| 15 | Cherry-Picked Data | Are statistics presented selectively or out of context? |
|| 16 | Logical Fallacies | Are flawed arguments used to dismiss critics? |
|| 17 | Manufactured Outrage | Does outrage seem sudden or disconnected from facts? |
|| 18 | Framing Techniques | Is the story shaped to control how you perceive it? |
|| 19 | Rapid Behavior Shifts | Are groups adopting symbols or actions without clear reasoning? |
|| 20 | Historical Parallels | Does the story mirror manipulative past events? |

## Task

Analyze the provided text and evaluate it against each NCI criterion.

**Output Format**: Return ONLY valid JSON:
{
  "criteria_scores": {
    "timing": {"matched": true/false, "reason": "brief explanation if matched"},
    "emotional_manipulation": {"matched": true/false, "reason": ""},
    ...all 20 criteria...
  },
  "aggregate_score": 0-20,
  "risk_level": "LOW|MODERATE|HIGH|CRITICAL",
  "summary": "brief 1-2 sentence summary of the key manipulation tactics"
}

**Scoring Rules**:
- LOW: 0-5 matches
- MODERATE: 6-10 matches
- HIGH: 11-15 matches
- CRITICAL: 16-20 matches

Be thorough but fair. Look for concrete evidence in the text for each criterion."""

        # Create Strands Agent for scoring
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
        )

    def score_text(
        self,
        text: str,
        url: str = "",
        title: str = ""
    ) -> Dict[str, Any]:
        """
        Score a single text against NCI criteria using Strands Agent.

        Args:
            text: The text content to score
            url: Optional URL of the source
            title: Optional title of the source

        Returns:
            Dictionary with scoring results
        """
        if not text or len(text.strip()) < 50:
            return {
                "url": url,
                "title": title,
                "error": "Text too short to score",
                "aggregate_score": 0,
                "risk_level": "UNKNOWN",
                "criteria_scores": {},
            }

        # Create scoring prompt
        prompt = f"""Score this source for NCI manipulation indicators:

Title: {title if title else "(no title)"}
URL: {url if url else "(no URL)"}

Content to analyze:
{text[:3000]}

Return ONLY valid JSON with no markdown formatting."""

        try:
            # Use Strands Agent with structured output for NCI scoring
            response = self.agent.structured_output(
                NCIScoreData,
                prompt,
            )
            
            # Convert Pydantic model to dict and add metadata
            score_data = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
            score_data["url"] = url
            score_data["title"] = title
            return score_data

        except Exception as e:
            if Config.DEBUG:
                print(f"[DEBUG] NCI scoring error for {url}: {str(e)}")
            
            # Fallback: try to call agent and parse JSON manually
            try:
                response = self.agent(prompt)
                result_text = str(response)
                
                # Extract JSON if wrapped in markdown
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                score_data = json.loads(result_text)
                score_data["url"] = url
                score_data["title"] = title
                return score_data
            except Exception as fallback_error:
                if Config.DEBUG:
                    print(f"[DEBUG] NCI scoring fallback error for {url}: {str(fallback_error)}")
                return {
                    "url": url,
                    "title": title,
                    "error": str(e),
                    "aggregate_score": 0,
                    "risk_level": "ERROR",
                    "criteria_scores": {},
                }

    def batch_score(self, sources: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Score multiple sources efficiently.

        Args:
            sources: List of dicts with 'text', 'url', and 'title' keys

        Returns:
            List of scoring results
        """
        results = []
        for source in sources:
            score = self.score_text(
                text=source.get("text", ""),
                url=source.get("url", ""),
                title=source.get("title", ""),
            )
            results.append(score)
        return results

    def score_synthesis(self, synthesis_text: str) -> Dict[str, Any]:
        """
        Score synthesized findings for meta-narrative patterns.

        Args:
            synthesis_text: The synthesized research findings

        Returns:
            Dictionary with synthesis-level scoring
        """
        return self.score_text(
            text=synthesis_text,
            url="SYNTHESIS",
            title="Research Synthesis - Meta Analysis",
        )

    def format_scores_for_display(
        self,
        scores: List[Dict[str, Any]],
        threshold: int = 6
    ) -> Dict[str, Any]:
        """
        Format scores for display in research reports.

        Args:
            scores: List of score results
            threshold: Minimum score to flag as concerning

        Returns:
            Formatted display data with flagged sources and summary
        """
        flagged_sources = []
        score_distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
        total_scored = 0

        for score in scores:
            if "error" in score or "aggregate_score" not in score:
                continue

            total_scored += 1
            agg_score = score.get("aggregate_score", 0)
            risk_level = score.get("risk_level", "UNKNOWN")

            if risk_level in score_distribution:
                score_distribution[risk_level] += 1

            if agg_score >= threshold:
                # Extract top criteria matches
                top_criteria = []
                criteria_scores = score.get("criteria_scores", {})
                for criterion, data in list(criteria_scores.items())[:5]:
                    if data.get("matched"):
                        top_criteria.append(criterion.replace("_", " ").title())

                flagged_sources.append({
                    "title": score.get("title", "Unknown"),
                    "url": score.get("url", ""),
                    "score": agg_score,
                    "risk_level": risk_level,
                    "key_indicators": top_criteria,
                })

        return {
            "total_scored": total_scored,
            "flagged_sources": flagged_sources,
            "distribution": score_distribution,
            "flagged_count": len(flagged_sources),
        }
