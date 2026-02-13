# Deep Research Agent MCP - Skill Guide

A comprehensive guide to using the Deep Research Agent MCP server in Claude Code for producing academic-quality research reports.

## 🎯 What This MCP Does

The Deep Research Agent transforms Claude into a research powerhouse by adding:

- **Neural Web Search**: Exa API integration for semantic, high-quality source discovery
- **Multi-Agent Orchestration**: Automated query decomposition → search → synthesis pipeline
- **Academic-Quality Reports**: 15-30 page equivalent comprehensive research documents
- **Source Credibility Analysis**: Optional NCI scoring to detect manipulation in sources
- **Custom Report Structures**: Flexible templates for different research needs

## 📊 Report Format & Structure

### Default Report Output

When you use `run_research`, you get a markdown document with this structure:

```markdown
# [Research Topic Title]

## Executive Summary
3-5 paragraphs covering:
- Research scope and objectives
- Key findings summary
- Main conclusions and implications

## Introduction
- Context and background
- Research objectives
- Methodology overview

## Key Findings
Multiple detailed sections organized by theme:
- Section 1: [Theme A]
  - Subsection with data, statistics, expert quotes
  - Inline citations: [Source Name](URL)
- Section 2: [Theme B]
  - Technical details and examples
  - Comparative analysis

## Detailed Analysis
Deep dive into each area:
- Technical mechanisms and implementations
- Historical context and evolution
- Current state of the art
- Strengths and limitations

## Industry/Application Analysis
- Real-world applications and use cases
- Market trends, adoption rates, growth data
- Key players, institutions, companies
- Success stories and challenges

## Future Implications and Trends
- Emerging developments
- Expert predictions and projections
- Upcoming challenges
- Opportunities and potential

## Critical Analysis
- Debates and controversies in the field
- Limitations and open challenges
- Alternative perspectives
- Unanswered research questions

## Conclusion
- Summary of main points
- Broader implications for the field
- Recommendations (if applicable)

## Source Credibility Analysis (if NCI enabled)
- NCI methodology overview
- Risk distribution of assessed sources
- Table of flagged sources with manipulation indicators
- Recommendations for source corroboration

## Sources and Citations
- Comprehensive list organized by category
- URLs for all referenced materials
```

### Citation Style

**All reports use inline markdown citations:**

```markdown
The quantum computing market is projected to reach $47 billion by 2030
[according to Grand View Research](https://example.com/report).

Studies show a 44% annual growth rate [Statista Analysis](https://example.com/stats).

As [Dr. Sarah Chen noted in her 2024 paper](https://arxiv.org/example),
"quantum supremacy has moved from theory to practice."
```

**Why this matters:**
- Citations are immediately visible where claims are made
- Easy to verify sources while reading
- Professional, academic-standard formatting
- Can be directly converted to other formats (HTML, PDF, LaTeX)

### Report Characteristics

**Length**: 15-30 page equivalent when printed
- ~5,000-15,000 words typical
- 50-100+ inline citations
- 30-60 unique sources

**Depth**: Academic-quality analysis
- Technical details explained clearly
- Multiple perspectives considered
- Data-driven conclusions
- Expert opinions integrated

**Structure**: Hierarchical and scannable
- Clear section headers
- Logical flow from context → findings → analysis → implications
- Subsections for complex topics
- Tables and comparisons where relevant

## 🚀 How to Use in Claude Code

### Basic Research Query

**Simplest usage:**
```
Use the deep research agent to investigate quantum computing breakthroughs in 2024
```

Claude will:
1. Automatically invoke `run_research`
2. Generate 8-12 optimized subqueries
3. Execute searches across authoritative sources
4. Synthesize a comprehensive report
5. Return formatted markdown with inline citations

**Expected time**: 2-5 minutes for full report

### Custom Report Structure

**Use templates for specific needs:**
```
Load the library template from template://library and research FastAPI best practices
```

**Or provide custom structure:**
```
Research the state of LLM fine-tuning using this structure:

# LLM Fine-Tuning Landscape

## Quick Start Guide
## Method Comparison Table
## Cost Analysis
## Best Practices
## Tool Recommendations
```

### Targeted Research Workflows

**Breaking it down yourself:**
```
1. First, use plan_research_subqueries to break down "protein folding AI"
2. Then use execute_web_search with those subqueries
3. Let me synthesize the final report
```

**Direct search (no full report):**
```
Use exa_neural_search to find:
- 10 recent papers on CRISPR from arxiv.org
- Published in the last year
- Focus on agricultural applications
```

### Source Credibility Analysis

**With NCI scoring enabled:**
```
Research [controversial topic] and include credibility analysis of all sources
```

The report will include:
- NCI scores (0-20) for top sources
- Risk levels: LOW, MODERATE, HIGH, CRITICAL
- Manipulation indicators detected
- Recommendations for cross-verification

## 💡 What These Reports Are Good For

### 1. **Technology Evaluation & Selection**
```
Research open-source LLM frameworks for production deployment
Include: maturity, community support, enterprise adoption, limitations
```

**Output useful for:**
- Technical decision-making documents
- Stakeholder presentations
- RFP responses
- Architecture design docs

### 2. **Market Research & Competitive Analysis**
```
Analyze the AI agent framework market landscape in 2025-2026
Focus on: market leaders, emerging players, differentiation, trends
```

**Output useful for:**
- Business strategy documents
- Investor presentations
- Product positioning
- Market entry planning

### 3. **Academic Literature Review**
```
Comprehensive review of transformer architecture improvements since 2023
Include: arxiv.org papers, key researchers, performance benchmarks
```

**Output useful for:**
- Research proposals
- Grant applications
- PhD literature reviews
- Conference paper backgrounds

### 4. **Technical Deep Dives**
```
How does Retrieval-Augmented Generation (RAG) work?
Include: architecture, implementations, trade-offs, benchmarks
```

**Output useful for:**
- Technical blog posts
- Internal training materials
- Documentation
- Engineering onboarding

### 5. **Trend Analysis & Forecasting**
```
What are the emerging trends in edge computing for 2025-2026?
Focus on: adoption drivers, key technologies, barriers, predictions
```

**Output useful for:**
- Strategic planning
- Innovation roadmaps
- Thought leadership content
- Industry reports

### 6. **Policy & Regulatory Research**
```
Current state of AI regulation in the EU and US
Include: legislation, compliance requirements, enforcement, timeline
```

**Output useful for:**
- Compliance documentation
- Legal briefings
- Risk assessments
- Policy position papers

### 7. **Educational Content Creation**
```
Explain quantum computing from basics to current state
Include: fundamental concepts, key milestones, applications, resources
```

**Output useful for:**
- Course materials
- Tutorial content
- Onboarding guides
- Public talks/presentations

## 🎨 Report Customization Examples

### Comparison Matrix Format
```markdown
Use this structure for research on "vector databases":

# Vector Database Landscape 2025

## Executive Summary

## Comparison Matrix
| Database | Use Case | Performance | Maturity | Cost |
|----------|----------|-------------|----------|------|

## Detailed Profiles
### [Database Name]
- Technical architecture
- Best for: [use cases]
- Limitations

## Recommendations by Use Case
```

### Quick Reference Format
```markdown
Research Python async frameworks using:

# Python Async Frameworks - Quick Reference

## TL;DR
One paragraph - top recommendation

## When to Use Each
- Framework A: [scenario]
- Framework B: [scenario]

## Feature Comparison
## Code Examples
## Performance Benchmarks
## Migration Guide
```

### Timeline/Evolution Format
```markdown
Research the evolution of language models:

# Large Language Models: Evolution Timeline

## Pre-2017: Foundations
## 2017-2020: Transformer Era
## 2020-2023: Scale & Capabilities
## 2023-Present: Efficiency & Deployment
## Future Directions
```

## 🔧 Advanced Usage Tips

### 1. **Domain-Specific Research**
```
Use exa_neural_search with include_domains:
- arxiv.org for academic papers
- github.com for code/projects
- news sites for recent developments
```

### 2. **Time-Bound Research**
```
Search for "AI safety" content:
- Published in last 3 months
- From authoritative sources only
- Include expert commentary
```

### 3. **Iterative Deep Dives**
```
1. High-level overview: "What is federated learning?"
2. Technical dive: "Federated learning algorithms and implementations"
3. Applied research: "Production federated learning systems"
```

### 4. **Cross-Verification Workflow**
```
1. Research topic with full report
2. Use nci_score_source on key cited sources
3. Flag sources with HIGH/CRITICAL risk
4. Re-search with exclude_domains for flagged sources
```

### 5. **Chaining MCP with Code Work**
```
1. Research: "Best practices for Python API design"
2. Save report to docs/api-design-research.md
3. Apply findings to codebase refactoring
4. Reference report in PR description
```

## 📦 Available Resources

### Templates
- `template://default` - Standard academic structure
- `template://library` - Library/tool documentation focus
- `template://custom` - Your custom templates

**Load with:**
```
Load template://library and use it to research [topic]
```

### Config
- `config://settings` - View current MCP configuration
- Shows enabled features, API status, parameters

### Example Structures
- `example://structures/list` - List all available templates
- `example://structures/[filename]` - Load specific template file

## ⚙️ Configuration for Different Needs

### High-Thoroughness Research
```bash
# .env
EXA_HIGH_PRIORITY_RESULTS=30
EXA_NORMAL_PRIORITY_RESULTS=25
EXA_SIMILAR_RESULTS=10
```

**Best for:** Academic papers, comprehensive market analysis, regulatory research

### Fast Overview Research
```bash
EXA_HIGH_PRIORITY_RESULTS=10
EXA_NORMAL_PRIORITY_RESULTS=8
EXA_SIMILAR_RESULTS=3
```

**Best for:** Quick competitive analysis, trend spotting, initial exploration

### Credibility-Focused Research
```bash
NCI_SCORING_ENABLED=true
NCI_SCORE_THRESHOLD=6
NCI_TOP_N_SOURCES=10
```

**Best for:** Controversial topics, political research, health/medical topics, financial analysis

## 🎯 Example Prompts by Use Case

### Startup/Product
```
Research AI code assistant market positioning for a new tool launch
Include: competitors, differentiation opportunities, pricing models, distribution channels
```

### Academic
```
Comprehensive literature review on diffusion models for image generation
Focus on: key papers since 2020, architectural innovations, benchmarks, open problems
```

### Engineering
```
Deep technical analysis of distributed tracing systems (Jaeger, Tempo, Zipkin)
Include: architecture comparison, performance characteristics, deployment considerations
```

### Business Strategy
```
Analyze the enterprise AI agent platform market landscape
Include: key players, market size/growth, buyer personas, competitive moats, trends
```

### Content Creation
```
Research [technical topic] to write an authoritative blog post
Structure for: beginner-friendly intro, technical details, practical examples, future outlook
```

## 🚨 Important Notes

### What Reports Include
✅ Inline citations with URLs
✅ Data, statistics, concrete examples
✅ Expert quotes and authoritative sources
✅ Technical details explained clearly
✅ Multiple perspectives considered
✅ Historical context and future implications
✅ Comprehensive source list

### What Reports Don't Include
❌ Uncited claims
❌ Opinion without attribution
❌ Speculation without expert backing
❌ Outdated information (focuses on recent sources)
❌ Shallow summaries (aims for depth)

### Quality Indicators
- **50+ inline citations** = comprehensive coverage
- **30+ unique sources** = diverse perspective
- **Technical + practical** = actionable insights
- **Past + present + future** = complete picture
- **Strengths + limitations** = balanced analysis

## 🔗 Related Documentation

- **Setup**: `MCP_QUICKSTART.md` - Installation and configuration
- **Architecture**: `CLAUDE.md` - System design and code patterns
- **Evaluation**: `EVALUATION-QUICK-START.md` - Testing NCI scoring accuracy
- **API Details**: `README.md` - Complete API reference

## 💬 Example Session

```
User: Use the deep research agent to investigate Rust web frameworks

Claude: I'll conduct comprehensive research on Rust web frameworks.
[Invokes run_research tool]
[2-3 minutes pass]

Here's a comprehensive research report on Rust web frameworks:

# Rust Web Framework Landscape (2025)

## Executive Summary

The Rust web framework ecosystem has matured significantly, with three
primary frameworks dominating production usage: Axum (22% market share),
Actix-web (35%), and Rocket (18%) [according to Rust Survey 2024](...).

[... continues with 15-30 page equivalent report ...]

## Sources and Citations
- 45 inline citations from authoritative sources
- Mix of documentation, benchmarks, blog posts, GitHub projects
- Dates range from 2023-2025 for current relevance
```

## 🎓 Pro Tips

1. **Be specific in queries**: "Python async frameworks for web scraping" > "Python async"

2. **Request custom structures**: Get exactly the format you need for your doc

3. **Use templates**: Faster than describing structure every time

4. **Enable NCI for controversial topics**: Get credibility analysis automatically

5. **Chain with code work**: Research → implement → reference findings

6. **Save reports**: They're reusable references with fresh citations

7. **Iterate on depth**: Start broad, then drill into specific areas

8. **Specify domains**: Guide search to authoritative sources for your field

---

**Ready to use?** See `MCP_QUICKSTART.md` for setup instructions.

**Questions?** Check the logs at `~/Library/Logs/Claude/mcp*.log` or run `uv run python test_mcp_server.py`
