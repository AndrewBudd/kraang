# Documentation

## Getting Started

See the main [README.md](../README.md) in the project root for installation and quick start instructions.

## Web Interface

The fact browser is the easiest way to explore the knowledge base:

**Local**: Open `fact-browser.html` in your browser (requires local http server)
**Online**: https://andrewbudd.github.io/kraang/fact-browser.html

## Core Concepts

### Facts
Extracted statements about the codebase including:
- **Implementation**: How things are implemented
- **Constraint**: Rules and restrictions
- **Requirement**: Requirements and specifications
- **Design**: Design decisions and patterns
- **Threat Vector**: Security concerns

### Conflicts
Contradictions between facts, automatically detected and categorized by severity:
- **CRITICAL**: Fundamental contradictions requiring immediate resolution
- **HIGH**: Significant conflicts affecting core functionality
- **MEDIUM**: Important conflicts with workarounds
- **LOW**: Minor inconsistencies

### Artifacts
Source files from which facts are extracted (code, documentation, configuration)

### Relationships
Connections between facts: supports, conflicts with, requires, implemented by, etc.

## Command Line Tools

All tools are in the `src/` directory:

- `kraang.py` - Main CLI for knowledge base management
- `conflict_detector.py` - Find contradictions
- `impact_analyzer.py` - Dependency and impact analysis
- `reconciler.py` - Generate resolution suggestions
- `requirement_analyzer.py` - Feasibility assessment
- `multi_pass_extraction.py` - Fact extraction engine

## Archive

The `archive/` directory contains detailed session documentation from the development of Kraang. These files provide extensive context about the system's design, implementation, and validation but are not necessary for using the tool.

## Examples

See the `examples/` directory for:
- Demo scripts showing tool usage
- Test files for validation
- Example output files

## API Key

Kraang uses the Anthropic Claude API for fact extraction and relationship analysis. Get your API key at:

https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Data Storage

Kraang stores all data locally in the `.kraang/` directory:

- `facts.json` - All extracted facts
- `artifacts.json` - Source file registry
- `relationships.json` - Fact relationships
- `conflicts.json` - Detected conflicts

All files are JSON format and can be inspected or queried directly.

## Performance

After initial extraction (requires API):
- ✅ Conflict detection: <1 second
- ✅ Impact analysis: <2 seconds
- ✅ Requirement analysis: <1 second
- ✅ Full reconciliation: <3 seconds

## Support

- **Issues**: https://github.com/AndrewBudd/kraang/issues
- **Repository**: https://github.com/AndrewBudd/kraang
