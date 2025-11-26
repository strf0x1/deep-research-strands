# Deep Research Agent (Strands Version)

This is a re-implementation of the Deep Research Agent using the AWS Strands Agents SDK.

## Overview

This agent leverages Minimax M2 (via Strands) and Exa API to conduct deep, comprehensive research on any given topic. It breaks down queries into sub-questions, searches the web, and synthesizes a detailed report.

## Features

- **Strands Agents SDK**: Uses the lightweight and flexible Strands framework for agent orchestration.
- **Minimax M2**: Powered by the Minimax M2 model for reasoning and planning.
- **Exa Neural Search**: Utilizes Exa for high-quality, semantic web search.
- **Comprehensive Reports**: Generates detailed, academic-quality research reports with inline citations.

## Setup

1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and add your API keys:
    - `MINIMAX_API_KEY`
    - `OPENROUTER_API_KEY`
    - `EXA_API_KEY`

## Usage

**Interactive Mode**:
```bash
python main.py
```

**Single Query**:
```bash
python main.py -q "Your research query here"
```
