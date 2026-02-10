# Kraang - Constraint Rationalization Engine

## Thesis

**"The core activity of building software is rationalizing conflicting constraints."**

Kraang is an engine that consumes artifacts (source code, documentation, requirements) and extracts:
- Facts that align with existing constraints
- Facts that contradict existing constraints
- New facts not yet related to known constraints

The resulting data structure maintains bidirectional references from facts back to source artifacts, enabling impact analysis when considering changes.

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_api_key_here
```

## Quick Start

```bash
# Initialize a new project
./kraang.py init

# Add artifacts
./kraang.py add ~/Code/LotJ/CLAUDE.md doc
./kraang.py add ~/Code/LotJ/src/act_info.c code

# Extract facts from artifacts (uses Claude)
./kraang.py extract artifact_1
./kraang.py extract artifact_2

# Analyze relationships between facts (uses Claude)
./kraang.py relate

# View contradictions
./kraang.py conflicts

# Analyze impact of changing a fact
./kraang.py impact fact_1

# List things
./kraang.py list artifacts
./kraang.py list facts
./kraang.py list relationships
```

## Data Model

### Artifact
Source documents: code files, documentation, requirements, configs.

```json
{
  "id": "artifact_1",
  "type": "code|doc|requirement|config",
  "path": "/path/to/file.c",
  "content": "..."
}
```

### Fact (Constraint)
Extracted facts, constraints, requirements, or implementation details.

```json
{
  "id": "fact_1",
  "statement": "Memory allocation MUST use CREATE macro, not malloc",
  "type": "requirement|implementation|design|constraint",
  "extracted_from": [
    {
      "artifact_id": "artifact_1",
      "location": "lines 250-270"
    }
  ],
  "confidence": 0.95
}
```

### Relationship
Connections between facts showing support, contradiction, or extension.

```json
{
  "fact_id_1": "fact_1",
  "fact_id_2": "fact_2",
  "type": "supports|contradicts|extends",
  "confidence": 0.9,
  "reasoning": "Both enforce the same memory management pattern"
}
```

## Use Cases

### 1. Detect Documentation Drift
Extract constraints from docs and code, then find contradictions where implementation doesn't match documented requirements.

### 2. Impact Analysis
Before changing a constraint, see all facts that depend on it and all artifacts that would need updates.

### 3. Onboarding New Developers
Visualize the constraint graph to understand project rules and patterns.

### 4. Refactoring Safety
Identify which constraints would be violated by a proposed architectural change.

## Storage

All data is stored in `.kraang/` as JSON files:
- `artifacts.json` - Registered artifacts
- `facts.json` - Extracted facts/constraints
- `relationships.json` - Relationships between facts
- `config.json` - Project configuration

Git-friendly format for version control.

## Architecture

1. **KraangStore**: Manages persistent JSON storage
2. **KraangExtractor**: LLM-powered fact extraction and relationship analysis
3. **KraangCLI**: Command-line interface

## Testing with LotJ

The LotJ MUD codebase is an excellent test case with clear documented constraints:

- Must use docker-compose (not direct builds)
- Must use CREATE/DISPOSE macros (not malloc/free)
- Must NOT create new header files
- Must use existing header structure
- Must use LINK/UNLINK macros for linked lists
- Must have zero compiler warnings

Test scenarios:
1. Extract facts from CLAUDE.md (documentation constraints)
2. Extract facts from C source files (implementation patterns)
3. Detect contradictions between docs and code
4. Analyze impact of changing memory management patterns

## Future Enhancements

- [ ] Batch extraction from directories
- [ ] Visualization of constraint graph
- [ ] Query language for complex impact analysis
- [ ] Integration with git to track constraint evolution
- [ ] Confidence scoring calibration
- [ ] Support for more artifact types (test files, configs, etc.)
- [ ] Caching of LLM responses
- [ ] Incremental updates when artifacts change
