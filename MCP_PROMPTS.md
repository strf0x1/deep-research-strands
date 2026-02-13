# MCP Prompts (Skills) Reference

The Deep Research Agent MCP now includes **prompts** that show up as **skills** in Claude Desktop. These provide guidance and templates for using the research agent effectively.

## 🎯 Available Prompts/Skills

### 1. **explain_research_agent**
**What it does:** Provides a comprehensive guide to using the Deep Research Agent

**Includes:**
- Report output format and structure
- Citation style explanation
- NCI scoring details (what scores mean, what it detects)
- Available tools and when to use them
- Example use cases by category
- Best practices and tips
- Report quality characteristics

**When to use:**
- First time using the MCP
- Need a refresher on capabilities
- Want to understand NCI scoring
- Looking for example prompts

**How to invoke in Claude Desktop:**
```
Use the explain_research_agent prompt
```

---

### 2. **research_template_comparison**
**What it does:** Provides a comparison matrix template for evaluating tools/frameworks

**Perfect for:**
- Technology evaluation
- Framework selection
- Tool comparison
- Product evaluation
- Vendor assessment

**Output structure:**
- Comparison matrix table
- Detailed profiles per option
- Selection criteria guide
- Ecosystem analysis
- Performance benchmarks
- Migration considerations

**How to invoke in Claude Desktop:**
```
Use the research_template_comparison prompt for [topic]
```

**Example:**
```
Use the research_template_comparison prompt for Python web frameworks
```

---

### 3. **research_template_quickstart**
**What it does:** Provides a quick-start guide template for learning tools/technologies

**Perfect for:**
- Learning new tools
- Creating onboarding materials
- Quick reference documentation
- Tutorial content
- Getting started guides

**Output structure:**
- TL;DR summary
- Problem statement
- 5-minute quick start
- Core concepts
- Common use cases with examples
- Best practices
- Comparison with alternatives
- Troubleshooting

**How to invoke in Claude Desktop:**
```
Use the research_template_quickstart prompt for [topic]
```

**Example:**
```
Use the research_template_quickstart prompt for Docker
```

---

### 4. **research_with_nci_focus**
**What it does:** Provides a credibility-focused research template with strong NCI emphasis

**Perfect for:**
- Controversial topics
- Political research
- Health/medical claims
- Financial analysis
- Topics prone to misinformation

**Requirements:**
- `NCI_SCORING_ENABLED=true` in your `.env` file

**Output emphasis:**
- Authoritative source focus
- Detailed NCI credibility analysis
- Cross-verification of claims
- Source quality tiers
- Confidence levels
- Red flag identification

**How to invoke in Claude Desktop:**
```
Use the research_with_nci_focus prompt for [controversial topic]
```

**Example:**
```
Use the research_with_nci_focus prompt for vaccine efficacy studies
```

---

## 📱 How They Appear in Claude Desktop

Once you restart Claude Desktop after adding/updating the MCP server, these prompts will appear in:

1. **The prompts/skills list** (if Claude Desktop exposes this UI)
2. **Auto-suggestions** when you type related queries
3. **Can be invoked explicitly**: "Use the [prompt_name] prompt"

## 🔧 How to Use

### Method 1: Explicit Invocation
```
Use the explain_research_agent prompt
```

### Method 2: Natural Language (Claude will suggest)
```
How do I use the research agent?
→ Claude may suggest: "I can use the explain_research_agent prompt to help you"
```

### Method 3: Combined with Research
```
Use the research_template_comparison prompt to research vector databases
```

## 📝 Customizing Templates

The prompts with `{TOPIC}` placeholders are templates. Claude will automatically:
1. Load the template
2. Replace `{TOPIC}` with your actual topic
3. Execute the research with that structure

**Example flow:**
```
You: Use research_template_quickstart for FastAPI

Claude: [Loads template]
        [Replaces {TOPIC} with "FastAPI"]
        [Executes research with custom structure]
        [Returns quick-start guide]
```

## 🎨 Creating Your Own Prompts

To add more prompts to the MCP server:

1. **Edit `mcp_server.py`**
2. **Add a new prompt function:**

```python
@mcp.prompt()
def your_prompt_name() -> str:
    """
    Description that appears in Claude Desktop.

    Explain what this prompt does and when to use it.
    """
    return """Your prompt content here.

    Can include:
    - Instructions
    - Templates with {PLACEHOLDERS}
    - Examples
    - Guidance
    """
```

3. **Restart the MCP server** (restart Claude Desktop)
4. **Prompt is now available** as a skill

## 🚀 Pro Tips

1. **Start with explain_research_agent** if you're new to the MCP
2. **Use templates for consistency** when you need specific formats repeatedly
3. **Combine with custom structures** for ultimate control
4. **Enable NCI scoring** before using `research_with_nci_focus`
5. **Edit prompts** to match your specific workflow needs

## 🔍 Verifying Prompts Are Loaded

Check the MCP server logs when it starts:
```bash
tail -f ~/Library/Logs/Claude/mcp-server-deep-research-agent.log
```

You should see prompts listed in the server capabilities.

## 📚 Related Documentation

- **Setup**: `MCP_QUICKSTART.md` - Initial configuration
- **Usage Guide**: `MCP_SKILL_GUIDE.md` - Comprehensive usage details
- **Architecture**: `CLAUDE.md` - System design
- **Main README**: `README.md` - Complete reference

## ❓ Troubleshooting

**Prompts not appearing:**
1. Verify MCP server is running: check Claude Desktop logs
2. Restart Claude Desktop completely (not just close window)
3. Check for errors in `~/Library/Logs/Claude/mcp*.log`

**Prompts not working:**
1. Verify the MCP server updated successfully
2. Check syntax in `mcp_server.py` (run `uv run python -c "import mcp_server"`)
3. Look for Python errors in the logs

**NCI prompt not working:**
1. Ensure `NCI_SCORING_ENABLED=true` in `.env`
2. Restart the MCP server after changing `.env`
3. Check logs for configuration validation

---

**Next Steps:** Try invoking `explain_research_agent` in Claude Desktop to see the full guide!
